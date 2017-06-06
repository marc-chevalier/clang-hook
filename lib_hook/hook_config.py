"""Configuration of clang-hook."""
from .stage import Str_to_stage
from .config import BaseConfig
from .filter import Filter


class HookConfig(BaseConfig):
    """Configuration of clang-hook."""
    __slots__ = ("data", "load", "passes", "link_flags", "error_log", "info_log", "debug_log", "log", "output_file",
                 "output_stages", "report_file", "filters")

    def __init__(self):
        self.load = None
        self.passes = None
        self.link_flags = None
        self.error_log = None
        self.info_log = None
        self.debug_log = None
        self.log = None
        self.output_file = None
        self.output_stages = None
        self.report_file = None

        self.filters = None
        super(HookConfig, self).__init__()

    def init(self, info_logger, name=None, debug=False, arg_path=None):
        """Search the config file and parse it. For tests purposes, this function won't be called, allowing the test
        suite to put arbitrary values in attributes."""
        super(HookConfig, self).init(info_logger, "clang-hook" if name is None else name, debug, arg_path)

    def parse_config(self):
        """Tells how to parse the dictionnary. Also define default values."""
        self.load = self.data.get("load", [])
        self.passes = self.data.get("passes", [])
        self.link_flags = self.data.get("link_flags", [])
        self.error_log = self.data.get("error_log", None)
        self.info_log = self.data.get("info_log", None)
        self.debug_log = self.data.get("debug_log", None)
        self.log = bool(self.data.get("log", True))
        self.output_file = self.data.get("output_file", None)

        output_stages = self.data.get("output_stages", None)
        if output_stages is not None:
            self.output_stages = set(Str_to_stage(stage) for stage in output_stages)
        else:
            self.output_stages = None

        self.report_file = self.data.get("report_file", None)
        self.filters = [Filter(f) for f in self.data.get("filters", [])]

    @classmethod
    def get_config_path_variable(cls):
        """Returns the environment vartiable containing the path of the configuration file."""
        return 'CLANG_HOOK_CONFIG'
