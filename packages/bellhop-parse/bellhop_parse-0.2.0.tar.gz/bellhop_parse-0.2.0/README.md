*"Let me get that for you."*

Bellhop provides deserealization of binary data according to a model.

For example,

```python
import bellhop

class Model(bellhop.Model):
    num: int = bellhop.Field(length=4, endian=bellhop.Endian.big)
    flag: bool
    data: bytes = bellhop.Field(length=3)

obj = Model(b"\x00\x00\x00\xff\x01\x01\x02\x03\x04")
print(obj) # Model(num=255, flag=True, data=b"\x01\x02\x03")
```

# Supported types

## Basic types

The basic types supported are `bool`, any `int` subclass (though `bool` is treated differently), `bytes`, and any `bellhop.Model` subclass.

### Integers

Integer fields (not counting `bool`) must have their length specified.  The allowed values are 1, 2, 4, and 8.  Furthermore, you may specify the endianness.  The possible values are `Endian.native` (the default), `Endian.big`, and `Endian.little`.

If the length is not specified in `bellhop.Field`, then you must implement the `resolve_length` class method:

```python
    @classmethod
    def resolve_length(cls, ctx: bellhop.ParsingContext) -> int:
        ...
```

A `ParsingContext` has the signature

```python
class ParsingContext:
    @property
    def user_data(self) -> typing.Any:
        ...
    
    @property
    def offset(self) -> int:
        ...
    
    @property
    def field(self) -> str:
        ...
    
    @property
    def stash(self) -> dict[str, typing.Any]:
        ...
    
    @property
    def list_index(self) -> int:
        ...
```

`ctx.offset` is the offset (relative to the start of the model) of the field currently being parsed.  `ctx.field` is the name of the field.  `ctx.stash` not only holds the values of the previously parsed fields but can also be used to stash information for later use.  Note that changing a previously parsed field's value via the stash does change the field's actual value.

The rest of the context's properties will be discussed later.

#### Bit integers

By specifying `bit=True` in `bellhop.Field` for an integer field, you can make the integer only consume bits and not bytes.  The length can be any positive number but the endian is forced to be big.

```python
class Model(bellhop.Model):
    num1: int = bellhop.Field(bit=True, length=3)
    num2: int = bellhop.Field(bit=True, length=10)

obj = Model(b"\x3f\xab")
assert obj.num1 == 1
assert obj.num2 == 0x3f5
```

### Boolean values

A `bool` field consumes one byte and is `True` if and only if the byte is non-zero.

#### Bit booleans

Boolean fields can also have bit width the same way as integers.  Their length must be specified the same way.

### Bytes

A `bytes` field consumes the data as is.  Its length can be specified as in the original example.  Setting the length to a negative value will consume all remaining data.

The length can be specified by either `bellhop.Field` or `resolve_length`.

## Compound types

### Lists

You can have a list of any basic type:

```python
class Model(bellhop.Model):
    array: list[int] = bellhop.Field(length=1, list_length=4)

obj = Model(b"\x00\x01\x02\x03")
print(obj) # Model(array=[0, 1, 2, 3])
```

If the list length is not specified via the `bellhop.Field`, then you must implement the `resolve_list_length` class method:

```python
    @classmethod
    def resolve_list_length(cls, ctx: bellhop.ParsingContext) -> int:
        ...
```

The individual item length (if applicable) can be specified via either a `bellhop.Field` or `resolve_length`.  Every element of a list will have the same length.

You can set the list length to a negative value.  This will cause elements to be continually added until a `bellhop.TerminateList` exception is raised (i.e., from a callback method).

If you add `list_post=True` to the `bellhop.Field`, the `list_post_processing` class method will be called for every item in the list:

```python
    @classmethod
    def list_post_processing(cls, ctx: bellhop.ParsingContext, item: typing.Any) -> typing.Any:
        ...
```

`ctx.list_index` will equal the index within the list of the current item.  `item` will be the parsed item and you must return either the item or a replacement item (which must still match the expected type).

### Unions

You can have a union of any basic type, any list type, and `None`:

```python
class Model(bellhop.Model):
    field: int | list[bytes] | None
```

You must implement the `resolve_union` class method:

```python
    @classmethod
    def resolve_union(cls, ctx: bellhop.ParsingContext) -> typing.Any:
        ...
```

This method must retain the type to use.  If you want to use `None` (which consumes zero bytes), you can return either `None` or `types.NoneType`.  When returning a list type, you must be specific.  For example, using the example above, you would have to return `list[bytes]` and not `list`.

To sidestep ambiguities, the length of a union field must be specified via `resolve_length` and not `bellhop.Field`.

#### Fallback

It may be the case that you have a field which you think will match a particular `bellhop.Model` subclass but you're not sure.  You can specify the field as

```python
class Model(bellhop.Model):
    field: Submodel | bytes = bellhop.Field(fallback=True)
```

In such a case, you wouldn't have to implement `resolve_union` (unless there were another subclass in the union).  Instead, the parser would first try to parse the field as a `Submodel` and then, if that failed, it would backtrack and treat it as a `bytes`.

# Custom fields

You can specify custom parsing for a particular field, even one not of a basic type, by setting `custom=True` in `bellhop.Field`.  Its length will be determined by either `bellhop.Field` or `resolve_length`.  The appropriate number of bytes will be read and then passed to `resolve_custom`:

```python
    @classmethod
    def resolve_custom(cls, ctx: bellhop.ParsingContest, chunk: bytes) -> typing.Any:
        ...
```

Custom fields cannot have `bit=True`.

# Raw fields

Sometimes you can't know how long a field will be until you start reading its bytes.  For example, suppose the bytes of a `str` field are preceded by a one-byte length (e.g., `b"\x05hello"`).  `resolve_custom` won't work for you here since you'd have to first create a field for the length.  Instead you can do

```python
class Model(bellhop.Model):
    word: str = bellhop.Field(raw=True)

    @classmethod
    def resolve_raw(cls, ctx: bellhop.ParsingContext, reader: Callable[[int], bytes]) -> typing.Any:
        length = reader(1)[0]
        return reader(length).decode("utf-8")

obj = Model(b"\x05helloabc")
assert obj.word == "hello"
```

A field cannot be both custom and raw.

Raw fields cannot have `bit=True`.

# Configuration

You can provide a configuration object to your model that can set the default endianness and even add new basic types.

## Default endianness

As stated above, if an integer's endianness is not stated, it defaults to native endianness.  You can change this in your configuration:

```python
class Model(bellhop.Model):
    __config__ = bellhop.Configuration(endian=bellhop.Endian.big)

    ...
```

If one model inherits from another, then the child model will inherit its parent's endianness unless the child specifies it in its own configuration.

## New basic types

You can expand the list of basic types which your model accepts via an implementation:

```python
@dataclasses.dataclass
class Foo:
    x: int
    y: int

def foo_builder(chunk: bytes) -> Foo:
    x, y = struct.unpack(">HH", chunk)
    return Foo(x=x, y=y)

implementation = bellhop.Implementation(Foo, builder=foo_builder, length=4)

class Model(bellhop.Model):
    __config__ = bellhop.Configuration(implementations=implementation)

    foo: Foo

obj = Model(b"\x00\x01\x00\x02")
assert obj.foo.x == 1
assert obj.foo.y == 2
```

The `implementations` argument to `Configuration` can either be a single implementation or an iterable thereof.

If the implementation's length is not provided, then the length will be determined by either `bellhop.Field` or `resolve_length`.

If the builder is not provided, then the class' constructor will be used (meaning it has to take a `bytes` as its only argument).

As with endianness, child models inherit implementations from their ancestors.

Fields of implemented types cannot have `bit=True`.

# Padding

You can state that padding bytes should follow a field by

```python
class Model(bellhop.Model):
    flag: bool = bellhop.Field(padding=1)
    num: int = bellhop.Field(length=1)

obj = Model(b"\x00\xff\x01")
assert obj.num == 1
```

If you set `padding=None`, then you must implement

```python
    @classmethod
    def resolve_padding(cls, ctx: bellhop.ParsingContext) -> int:
        ...
```

# Post init

You can define a `__post_init__` method which will be called after all of the fields have been parsed:

```python
class Model(bellhop.Model):
    num: int = bellhop.Field(length=1)

    def __post_init__(self) -> None:
        self.num += 1

obj = Model(b"\x00")
assert obj.num == 1
```

# Errors

The are several error types that can be raised by the parsing logic.  All of them inherit from `bellhop.Error` and have a `chain` attribute.  The chain is a description of where the parsing logic was when the error occurred.  For example,

```python
class Submodel(bellhop.Model):
    flag: bool
    num: int = bellhop.Field(length=1, post=True)

    @classmethod
    def post_processing(cls, ctx: bellhop.ParsingContext, value: typing.Any) -> typing.Any:
        return 1/0

class Model(bellhop.Model):
    chunk: bytes = bellhop.Field(length=4)
    sub: Submodel

try:
    Model(bytes(6))
except bellhop.Error as e:
    assert isinstance(e, bellhop.UserCallbackError)
    assert e.chain == [(Model, "sub", 4), (Submodel, "num", 1)]
    assert isinstance(e.__cause__, ZeroDivisionError)
```

# User data

You can pass a custom object that will be passed to all of your callback functions via `ctx.user_data`:

```python
user_data = object()

class Model(bellhop.Model):
    flag: bool = bellhop.Field(post=True)

    @classmethod
    def post_processing(cls, ctx: bellhop.ParsingContext, value: typing.Any) -> typing.Any:
        assert ctx.user_data is user_data
        return value

Model(b"\x00", user_data=user_data)
```

By default, the user data will also be inherited by any submodels.  However, this can be changed with

```python
    @classmethod
    def update_user_data(cls, ctx: bellhop.ParsingContext) -> typing.Any:
```

The return value of this method will be the user data that is passed to the submodel.