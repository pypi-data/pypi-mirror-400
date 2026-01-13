import typing

Chain = list[tuple[type, str, int]]


class Error(Exception):
    def __init__(self, *args: typing.Any, chain: Chain, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.chain = chain


class ReadError(Error):
    pass


class InsufficientData(Error):
    pass


class UserCallbackError(Error):
    pass


class InvalidResolution(Error):
    pass


class TerminateList(Error):
    def __init__(self) -> None:
        super().__init__(chain=[])


class InvalidInteger(Error):
    def __init__(self, *args: typing.Any, cls: type[int], value: int, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.cls = cls
        self.value = value
