"""Tools to work this the stage (clang, opt, llc or link)."""
from .auto_number import AutoNumber, make_enum_to_str, make_str_to_enum


class Stage(AutoNumber):
    """An enum for the stage."""
    Clang = ()
    Opt = ()
    Llc = ()
    Link = ()


Str_to_stage = make_str_to_enum(Stage, name="str_to_stage")
Stage_to_str = make_enum_to_str(Stage, name="stage_to_str")
