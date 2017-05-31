from .auto_number import AutoNumber, make_enum_to_str, make_str_to_enum


class Stage(AutoNumber):
    Clang = ()
    Opt = ()
    Llc = ()
    Link = ()


str_to_stage = make_str_to_enum(Stage, name="str_to_stage")
stage_to_str = make_enum_to_str(Stage, name="stage_to_str")
