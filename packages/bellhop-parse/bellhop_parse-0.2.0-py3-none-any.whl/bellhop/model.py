import collections.abc
import dataclasses
import enum
import io
import itertools
import struct
import types
import typing

from . import errors

_T = typing.TypeVar("_T")
_P = typing.ParamSpec("_P")


class Endian(enum.Enum):
    native = enum.auto()
    little = enum.auto()
    big = enum.auto()


@dataclasses.dataclass
class _FieldInfo:
    endian: Endian | None
    length: int | None
    list_length: int | None
    signed: bool
    bit: bool
    fallback: bool
    post: bool
    list_post: bool
    custom: bool
    raw: bool
    padding: int | None


def Field(
    *,
    endian: Endian | None = None,
    length: int | None = None,
    list_length: int | None = None,
    signed: bool = False,
    bit: bool = False,
    fallback: bool = False,
    post: bool = False,
    list_post: bool = False,
    custom: bool = False,
    raw: bool = False,
    padding: int | None = 0,
) -> typing.Any:
    return _FieldInfo(
        endian=endian,
        length=length,
        list_length=list_length,
        signed=signed,
        bit=bit,
        fallback=fallback,
        post=post,
        list_post=list_post,
        custom=custom,
        raw=raw,
        padding=padding,
    )


_DEFAULT_FIELD_INFO: _FieldInfo = Field()


def _generate_fields(model: type) -> collections.abc.Iterator[tuple[str, typing.Any]]:
    for name, annotation in model.__annotations__.items():
        if typing.get_origin(annotation) is not typing.ClassVar:
            yield name, annotation


def _generate_all_fields(cls: type) -> collections.abc.Iterator[tuple[str, typing.Any]]:
    for ancestor in reversed(cls.mro()):
        if issubclass(ancestor, Model) and ancestor is not Model:
            yield from _generate_fields(ancestor)


def _is_valid_for_type(value: object, cls: type) -> bool:
    return isinstance(value, cls) and not (isinstance(value, bool) and cls is not bool)


def _is_valid_for_annotation(value: object, annotation: typing.Any) -> bool:
    if (origin := typing.get_origin(annotation)) is None:
        assert isinstance(annotation, type)
        return _is_valid_for_type(value, annotation)

    if origin is types.UnionType:
        return any(_is_valid_for_annotation(value, cls) for cls in annotation.__args__)
    if origin is list:
        item_type = annotation.__args__[0]
        return isinstance(value, list) and all(isinstance(item, item_type) for item in value)
    assert False  # pragma: no cover


class Implementation:
    def __init__(
        self,
        cls: type[_T],
        *,
        length: int | None = None,
        builder: collections.abc.Callable[[bytes], _T] | None = None,
    ) -> None:
        self.cls = cls
        self.length = length
        self.builder: collections.abc.Callable[[bytes], _T] = builder or cls


class _ConfigProto(typing.Protocol):
    endian: Endian | None
    implementations: dict[type, Implementation]


class Configuration:
    def __init__(
        self,
        *,
        endian: Endian | None = None,
        implementations: Implementation | collections.abc.Iterable[Implementation] = (),
    ) -> None:
        self.endian = endian
        if isinstance(implementations, Implementation):
            implementations = [implementations]
        self.implementations = {implementation.cls: implementation for implementation in implementations}

    def inherit_from(self, parent: _ConfigProto) -> None:
        if self.endian is None:
            self.endian = parent.endian

        for cls, implementation in parent.implementations.items():
            self.implementations.setdefault(cls, implementation)


class _ModelProto(typing.Protocol):
    __config__: typing.ClassVar[Configuration]


class _Verifier:
    def __init__(self, model: type[_ModelProto]) -> None:
        self.model = model

        self.field_info = _DEFAULT_FIELD_INFO
        self.in_union = False
        self.in_list = False

    def verify(self) -> None:
        for name, annotation in _generate_fields(self.model):
            self.field_info = getattr(self.model, name, _DEFAULT_FIELD_INFO)

            if not isinstance(self.field_info, _FieldInfo):
                raise TypeError(
                    f"Invalid value type for field {name} in class {self.model.__name__}: Expected"
                    f" bellhop.Field but got {type(self.field_info)}."
                )

            self.in_union = False
            self.in_list = False
            self.validate_field(name, annotation)

    def validate_field(self, name: str, annotation: typing.Any) -> None:
        if self.field_info.bit:
            self.validate_bit_field(name, annotation)
        elif (origin := typing.get_origin(annotation)) is not None:
            self.validate_complex_type(name, annotation, origin)
        elif not isinstance(annotation, type):
            raise TypeError(
                f"Field {name} in class {self.model.__name__} has invalid annotation: {annotation}"
            )
        elif self.field_info.custom or self.field_info.raw:
            self.validate_custom_or_raw(name, annotation)
        elif annotation in self.model.__config__.implementations:
            pass
        elif annotation is bool:
            pass
        elif issubclass(annotation, int):
            if not self.in_union:
                self.validate_int(name)
        elif annotation is bytes:
            pass
        elif self.in_union and annotation is types.NoneType:
            pass
        elif issubclass(annotation, Model) and annotation is not Model:
            pass
        else:
            raise TypeError(f"Invalid type for field {name} in class {self.model.__name__}: {annotation}")

    def validate_bit_field(self, name: str, annotation: typing.Any) -> None:
        if not isinstance(annotation, type) or not issubclass(annotation, int):
            raise TypeError(
                f"Bit field {name} in class {self.model.__name__} must be an integer type and not "
                f"{annotation}"
            )

        if self.field_info.custom or self.field_info.raw:
            description = "custom" if self.field_info.custom else "raw"
            raise ValueError(f"Bit field {name} in class {self.model.__name__} cannot be {description}")

        if self.field_info.length is not None and self.field_info.length <= 0:
            raise ValueError(f"Length for bit field {name} in class {self.model.__name__} must be positive")

        if annotation in self.model.__config__.implementations:
            raise TypeError(
                f"Bit field {name} in class {self.model.__name__} cannot have a configured implementation"
            )

    def validate_complex_type(self, name: str, annotation: typing.Any, origin: typing.Any) -> None:
        if origin is types.UnionType:
            if self.in_list:
                raise TypeError(
                    f"Invalid type for field {name} in class {self.model.__name__}.  Cannot have a"
                    " union inside of a list."
                )
            self.validate_union(name, annotation)
        elif origin is list:
            self.in_list = True
            self.validate_field(name, annotation.__args__[0])
        else:
            raise TypeError(f"Invalid type for field {name} in class {self.model.__name__}: {annotation}")

    def validate_custom_or_raw(self, name: str, annotation: type) -> None:
        if issubclass(annotation, Model):
            description = "custom" if self.field_info.custom else "raw"
            raise TypeError(
                f"Field {name} in class {self.model.__name__} cannot be {description} because it is of a"
                " submodel type."
            )

        if self.field_info.custom and self.field_info.raw:
            raise ValueError(f"Field {name} in class {self.model.__name__} cannot be both custom and raw")

    def validate_int(self, name: str) -> None:
        if self.field_info.length is not None and self.field_info.length not in (1, 2, 4, 8):
            raise ValueError(f"Invalid length specification for field {name} in class {self.model.__name__}.")

    def validate_union(self, name: str, annotation: types.UnionType) -> None:
        if self.field_info.fallback:
            self.validate_fallback(name, annotation)

        self.in_union = True
        for subtype in annotation.__args__:
            self.validate_field(name, subtype)

    def validate_fallback(self, name: str, annotation: types.UnionType) -> None:
        found_bytes = False
        for subtype in annotation.__args__:
            if subtype is bytes:
                found_bytes = True
            elif not issubclass(subtype, Model) or subtype is Model:
                raise TypeError(
                    f"Invalid type in union when fallback is specified for field {name} in class"
                    f" {self.model.__name__}: {subtype}"
                )

        if not found_bytes:
            raise TypeError(
                f"bytes must be in union when fallback is specified for field {name} in class"
                f" {self.model.__name__}."
            )


class ParsingContext:
    def __init__(self, user_data: typing.Any) -> None:
        self._user_data = user_data
        self._offset = 0
        self._field = ""
        self._stash: dict[str, typing.Any] = {}
        self._list_index = 0

    @property
    def user_data(self) -> typing.Any:
        return self._user_data

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def field(self) -> str:
        return self._field

    @property
    def stash(self) -> dict[str, typing.Any]:
        return self._stash

    @property
    def list_index(self) -> int:
        return self._list_index


@dataclasses.dataclass
class _ParsingCapsule:
    data: typing.BinaryIO
    chain: errors.Chain
    user_data: typing.Any


class Model:
    __config__: typing.ClassVar[Configuration] = Configuration()

    def __init_subclass__(cls) -> None:
        if (config := cls.__dict__.get("__config__")) is not None:
            for parent_cls in cls.mro()[1:]:
                if (parent_config := parent_cls.__dict__.get("__config__")) is not None:
                    config.inherit_from(parent_config)
                    break

        _Verifier(cls).verify()

    @typing.final
    def __init__(self, data: bytes | bytearray | typing.BinaryIO, user_data: typing.Any = None) -> None:
        if isinstance(user_data, _ParsingCapsule):
            data = user_data.data
            chain = user_data.chain
            user_data = user_data.user_data
        else:
            if isinstance(data, (bytes, bytearray)):
                data = io.BytesIO(data)
            chain = []

        for name, value in _Parser(type(self), data, chain, user_data).parse():
            setattr(self, name, value)

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    def __repr__(self) -> str:
        entries = []
        for field, _ in _generate_all_fields(self.__class__):
            value = getattr(self, field)
            entries.append(f"{field}={value}")
        return f"{self.__class__.__name__}({', '.join(entries)})"

    @classmethod
    def resolve_length(cls, ctx: ParsingContext) -> int:
        raise NotImplementedError

    @classmethod
    def resolve_union(cls, ctx: ParsingContext) -> typing.Any:
        raise NotImplementedError

    @classmethod
    def resolve_list_length(cls, ctx: ParsingContext) -> int:
        raise NotImplementedError

    @classmethod
    def post_processing(cls, ctx: ParsingContext, value: typing.Any) -> typing.Any:
        raise NotImplementedError

    @classmethod
    def list_post_processing(cls, ctx: ParsingContext, item: typing.Any) -> typing.Any:
        raise NotImplementedError

    @classmethod
    def resolve_custom(cls, ctx: ParsingContext, chunk: bytes) -> typing.Any:
        raise NotImplementedError

    @classmethod
    def resolve_raw(cls, ctx: ParsingContext, reader: collections.abc.Callable[[int], bytes]) -> typing.Any:
        raise NotImplementedError

    @classmethod
    def resolve_padding(cls, ctx: ParsingContext) -> int:
        raise NotImplementedError

    @classmethod
    def update_user_data(cls, ctx: ParsingContext) -> typing.Any:
        return ctx.user_data


class _Parser:
    def __init__(
        self, model: type[Model], data: typing.BinaryIO, chain: errors.Chain, user_data: typing.Any
    ) -> None:
        self.model = model
        self.data = data
        self.base_offset = data.tell()
        self.chain = chain
        self.ctx = ParsingContext(user_data)

        self.field_info = _DEFAULT_FIELD_INFO
        self.in_union = False
        self.in_list = False
        self.list_item_length = 0
        self.list_start = 0
        self.bit_cache = 0
        self.bit_cache_length = 0

    def parse(self) -> collections.abc.Iterator[tuple[str, typing.Any]]:
        for field, annotation in _generate_all_fields(self.model):
            self.ctx._field = field
            self.field_info = getattr(self.model, field, _DEFAULT_FIELD_INFO)
            self.in_union = False
            self.in_list = False

            if not self.field_info.bit:
                self.bit_cache = 0
                self.bit_cache_length = 0

            value = self.parse_value(annotation)
            if self.field_info.post:
                value = self.handle_post_processing(value, annotation)
            self.ctx._stash[field] = value
            self.consume_padding()
            yield field, value

    def parse_value(self, annotation: typing.Any) -> typing.Any:
        self.ctx._offset = self.data.tell() - self.base_offset
        if (origin := typing.get_origin(annotation)) is not None:
            return self.parse_complex_type(annotation, origin)
        elif self.field_info.custom:
            return self.parse_custom(annotation)
        elif self.field_info.raw:
            return self.parse_raw(annotation)
        elif (implementation := self.model.__config__.implementations.get(annotation)) is not None:
            return self.parse_implementation(implementation)
        elif annotation is bool:
            return self.parse_bool()
        elif issubclass(annotation, int):
            return self.parse_int(annotation)
        elif annotation is bytes:
            return self.parse_bytes()
        elif issubclass(annotation, Model):
            return self.parse_submodel(annotation)
        else:
            assert False  # pragma: no cover

    def handle_post_processing(self, value: typing.Any, annotation: typing.Any) -> typing.Any:
        if self.in_list:
            self.ctx._offset = self.list_start
        value = self.callback(self.model.post_processing, value)
        if not _is_valid_for_annotation(value, annotation):
            raise errors.InvalidResolution(
                f"Invalid type returned by post-processing.  Expected {annotation} but got {type(value)}.",
                chain=self.updated_chain(),
            )
        return value

    def consume_padding(self) -> None:
        length = (
            self.field_info.padding
            if self.field_info.padding is not None
            else self.callback(self.model.resolve_padding)
        )
        if length != 0:
            self.get_data(length)

    def updated_chain(self) -> errors.Chain:
        return self.chain + [(self.model, self.ctx._field, self.ctx._offset)]

    def callback(
        self,
        func: collections.abc.Callable[typing.Concatenate[ParsingContext, _P], _T],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _T:
        try:
            return func(self.ctx, *args, **kwargs)
        except errors.TerminateList as e:
            e.chain = self.updated_chain()
            raise
        except (NotImplementedError, AssertionError, errors.Error):
            raise
        except Exception as e:
            raise errors.UserCallbackError(chain=self.updated_chain()) from e

    def field_length(self) -> int:
        if self.in_list and self.list_item_length > 0:
            return self.list_item_length

        length = (
            self.field_info.length
            if self.field_info.length is not None and not self.in_union
            else self.callback(self.model.resolve_length)
        )
        if self.in_list:
            self.list_item_length = length
        return length

    def get_data(self, num: int) -> bytes:
        try:
            data = self.data.read(num)
        except Exception as e:
            raise errors.ReadError(chain=self.updated_chain()) from e
        if len(data) < num:
            raise errors.InsufficientData(
                f"Insufficient data for field {self.ctx._field} in class {self.model.__name__}",
                chain=self.updated_chain(),
            )
        return data

    def parse_complex_type(self, annotation: typing.Any, origin: typing.Any) -> typing.Any:
        if origin is types.UnionType:
            return self.parse_union(annotation)
        if origin is list:
            return self.parse_list(annotation)
        assert False  # pragma: no cover

    def parse_custom(self, annotation: type) -> typing.Any:
        value = self.callback(self.model.resolve_custom, self.parse_bytes())
        if not _is_valid_for_type(value, annotation):
            raise errors.InvalidResolution(
                f"Invalid type for field {self.ctx._field} in class {self.model.__name__}.  Expected"
                f" {annotation} but got {type(value)}.",
                chain=self.updated_chain(),
            )
        return value

    def parse_raw(self, annotation: type) -> typing.Any:
        value = self.callback(self.model.resolve_raw, self.get_data)
        if not _is_valid_for_type(value, annotation):
            raise errors.InvalidResolution(
                f"Invalid type for field {self.ctx._field} in class {self.model.__name__}.  Expected"
                f" {annotation} but got {type(value)}.",
                chain=self.updated_chain(),
            )
        return value

    def parse_implementation(self, implementation: Implementation) -> typing.Any:
        length = implementation.length if implementation.length is not None else self.field_length()
        obj = implementation.builder(self.get_data(length))
        if not isinstance(obj, implementation.cls):
            raise errors.InvalidResolution(
                f"Invalid type for field {self.ctx._field} in class {self.model.__name__}.  Expected"
                f" {implementation.cls} but got {type(obj)}.",
                chain=self.updated_chain(),
            )
        return obj

    def parse_bool(self) -> bool:
        num = self.parse_bit_int() if self.field_info.bit else self.get_data(1)[0]
        return bool(num)

    def parse_int(self, annotation: type[int]) -> int:
        num = self.parse_bit_int() if self.field_info.bit else self.parse_whole_byte_int()
        try:
            return annotation(num)
        except ValueError as e:
            raise errors.InvalidInteger(
                f"Invalid value for class {annotation.__name__} for field {self.ctx._field} in class"
                f" {self.model.__name__}: {num}",
                cls=annotation,
                value=num,
                chain=self.updated_chain(),
            ) from e

    def parse_whole_byte_int(self) -> int:
        match self.field_info.endian or self.model.__config__.endian or Endian.native:
            case Endian.native:
                fmt = "="
            case Endian.little:
                fmt = "<"
            case Endian.big:
                fmt = ">"

        match length := self.field_length():
            case 1:
                fmt += "B"
            case 2:
                fmt += "H"
            case 4:
                fmt += "I"
            case 8:
                fmt += "Q"
            case _:
                raise errors.InvalidResolution(
                    f"Invalid length for field {self.ctx._field} in class {self.model.__name__}: {length}",
                    chain=self.updated_chain(),
                )

        if self.field_info.signed:
            fmt = fmt.lower()

        return struct.unpack(fmt, self.get_data(length))[0]

    def parse_bit_int(self) -> int:
        length = self.field_length()
        if length <= 0:
            raise errors.InvalidResolution(
                f"Invalid length for field {self.ctx._field} in class {self.model.__name__}: {length}",
                chain=self.updated_chain(),
            )

        if length > self.bit_cache_length:
            chunk_length = (length - self.bit_cache_length + 7) // 8
            for octet in self.get_data(chunk_length):
                self.bit_cache = (self.bit_cache << 8) | octet
                self.bit_cache_length += 8

        remaining_length = self.bit_cache_length - length
        num = self.bit_cache >> remaining_length
        self.bit_cache &= (1 << remaining_length) - 1
        self.bit_cache_length = remaining_length
        return num

    def parse_bytes(self) -> bytes:
        return self.get_data(self.field_length())

    def parse_submodel(self, submodel: type[Model]) -> typing.Any:
        current_offset = self.data.tell()
        user_data = self.callback(self.model.update_user_data)
        try:
            return submodel(
                b"",
                _ParsingCapsule(data=self.data, chain=self.updated_chain(), user_data=user_data),
            )
        except errors.TerminateList:
            raise
        except errors.Error:
            if not self.field_info.fallback:
                raise
            self.data.seek(current_offset)
            return self.parse_value(bytes)

    def parse_union(self, annotation: types.UnionType) -> typing.Any:
        if self.field_info.fallback and len(annotation.__args__) == 2:
            for submodel in annotation.__args__:
                if submodel is not bytes:
                    return self.parse_submodel(submodel)
            assert False  # pragma: no cover

        cls = self.callback(self.model.resolve_union)
        if cls is None:
            cls = types.NoneType
        if cls not in annotation.__args__:
            raise errors.InvalidResolution(
                f"Unexpected type returned from resolve_union for field {self.ctx._field} in class"
                f" {self.model.__name__}.  Expected one of {annotation.__args__} but got {cls}.",
                chain=self.updated_chain(),
            )

        if cls is types.NoneType:
            return None

        self.in_union = True
        return self.parse_value(cls)

    def parse_list(self, annotation: types.GenericAlias) -> list[typing.Any]:
        self.in_list = True
        self.list_item_length = 0
        self.list_start = self.ctx._offset

        length = (
            self.field_info.list_length
            if self.field_info.list_length is not None
            else self.callback(self.model.resolve_list_length)
        )
        iterable: collections.abc.Iterable[int] = itertools.count(0) if length < 0 else range(length)

        item_type = annotation.__args__[0]
        value: list[typing.Any] = []
        try:
            for k in iterable:
                value.append(self.parse_list_item(k, item_type))
        except errors.TerminateList:
            pass
        return value

    def parse_list_item(self, index: int, item_type: type) -> typing.Any:
        self.ctx._list_index = index
        item = self.parse_value(item_type)

        if not self.field_info.list_post:
            return item

        item = self.callback(self.model.list_post_processing, item)
        if not _is_valid_for_type(item, item_type):
            raise errors.InvalidResolution(
                f"Unexpected type returned from list_post_processing.  Expected {item_type} but got"
                f" {type(item)}.",
                chain=self.updated_chain(),
            )
        return item
