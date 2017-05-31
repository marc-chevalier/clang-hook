import enum
import typing


class AutoNumber(enum.Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


def make_str_to_enum(e: typing.Type[AutoNumber], name: typing.Optional[str] = None, case_sensitive: bool = False):
    def str_to_enum(s: str) -> e:
        try:
            return {k if case_sensitive else k.lower(): v
                    for k, v in e.__members__.items()}[s if case_sensitive else s.lower()]
        except KeyError:
            raise KeyError(s)

    if name is not None:
        str_to_enum.__name__ = name
    return str_to_enum


def make_enum_to_str(e: typing.Type[AutoNumber], name: typing.Optional[str] = None, case_sensitive: bool = False):
    def enum_to_str(s: e) -> str:
        return {v: k if case_sensitive else k.lower() for k, v in e.__members__.items()}[s]

    if name is not None:
        enum_to_str.__name__ = name
    return enum_to_str
