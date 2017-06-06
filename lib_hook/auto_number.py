"""Defines automatic enumration. We use it with the syntax:
class MyEnum(AutoNumber):
    foo = ()
    bar = ()
"""
import enum
import typing


class AutoNumber(enum.Enum):
    """Pythonic magic.
    From https://docs.python.org/3/library/enum.html"""
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


def make_str_to_enum(enum_type: typing.Type[AutoNumber], name: typing.Optional[str]=None, case_sensitive: bool = False):
    """Given an enum type, it returns a function which convert strings to enumeration members.
    An optional name can (and should) be provided."""
    def str_to_enum(enum_str: str) -> enum_type:
        """Transform a string into an enumeration member."""
        try:
            return {k if case_sensitive else k.lower(): v
                    for k, v in enum_type.__members__.items()}[enum_str if case_sensitive else enum_str.lower()]
        except KeyError:
            raise KeyError(enum_str)

    if name is not None:
        str_to_enum.__name__ = name
    return str_to_enum


def make_enum_to_str(enum_type: typing.Type[AutoNumber], name: typing.Optional[str]=None, case_sensitive: bool = False):
    """Given an enum type, it returns a function which convert enumeration members to strings.
    An optional name can (and should) be provided."""
    def enum_to_str(enum_member: enum_type) -> str:
        """Transform a enumeration member into a string."""
        return {v: k if case_sensitive else k.lower() for k, v in enum_type.__members__.items()}[enum_member]

    if name is not None:
        enum_to_str.__name__ = name
    return enum_to_str
