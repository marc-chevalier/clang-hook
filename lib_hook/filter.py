"""Filters allows to match the output against a regex and use the match for statistic purpose."""

import re
import typing

from lib_hook.auto_number import AutoNumber
from .stage import Str_to_stage, Stage


class InvalidStage(Exception):
    """A filter was applied at a wrong stage."""
    pass


class FilterMode(AutoNumber):
    """Whether the filter should use lookaroung regex or extract the match thanks to groups."""
    LookAround = ()
    Groups = ()


class Filter:
    """The Filter class contains everyting about a filter and is made to look into output and returns the match with the
    right type."""
    def __init__(self, data):
        self.name = data["name"]
        self.regex = re.compile(data["pattern"])
        self.mode = FilterMode.Groups if data["mode"] == "group" else FilterMode.LookAround
        self.group = data["group"] if self.mode == FilterMode.Groups else None
        self.stages = [Str_to_stage(e) for e in data["stages"]]
        self.type = {"bool": bool, "int": int, "float": float, "string": str}[data["type"]]
        self.summary = data["summary"]

    def search(self, output: str, stage: Stage) -> typing.Union[bool, int, float, str, None]:
        """Looks for a match in the given string and returns the match. If the filter does not match, return None."""
        if stage not in self.stages:
            return None
        match = self.regex.search(output)

        if match is None:
            return None
        if self.mode == FilterMode.Groups:
            return self.type(match.group(self.group))
        return self.type(match.group(0))
