import re
import typing

from lib_hook.auto_number import AutoNumber
from .stage import str_to_stage, Stage


class InvalidStage(Exception):
    pass


class FilterMode(AutoNumber):
    LookAround = ()
    Groups = ()


class Filter:
    def __init__(self, data):
        self.name = data["name"]
        self.regex = re.compile(data["pattern"])
        self.mode = FilterMode.Groups if data["mode"] == "group" else FilterMode.LookAround
        self.group = data["group"] if self.mode == FilterMode.Groups else None
        self.stages = [str_to_stage(e) for e in data["stages"]]
        self.type = {"bool": bool, "int": int, "float": float, "string": str}[data["type"]]
        self.summary = data["summary"]

    def search(self, s: str, stage: Stage) -> typing.Union[bool, int, float, str, None]:
        if stage not in self.stages:
            return None
        match = self.regex.search(s)

        if match is None:
            return None
        elif self.mode == FilterMode.Groups:
            return self.type(match.group(self.group))
        else:
            return self.type(match.group(0))
