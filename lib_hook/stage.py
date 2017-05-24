from .auto_number import AutoNumber


class Stage(AutoNumber):
    Clang = ()
    Opt = ()
    Llc = ()
    Link = ()


def str_to_stage(s: str) -> Stage:
    return {"clang": Stage.Clang, "opt": Stage.Opt, "llc": Stage.Llc, "link": Stage.Link}[s]


def stage_to_str(s: Stage) -> str:
    return {Stage.Clang: "clang", Stage.Opt: "opt", Stage.Llc: "llc", Stage.Link: "link"}[s]
