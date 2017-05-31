from .stage import str_to_stage
from .config import BaseConfig
from .filter import Filter


class HookConfig(BaseConfig):
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

    def init(self, info_logger, name="clang-hook", debug=False, arg_path=None):
        super(HookConfig, self).init(name, info_logger, debug, arg_path)

    def parse_config(self):
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
            self.output_stages = set(str_to_stage(stage) for stage in output_stages)
        else:
            self.output_stages = None

        self.report_file = self.data.get("report_file", None)
        self.filters = [Filter(f) for f in self.data.get("filters", [])]

    @classmethod
    def get_config_path_variable(cls):
        return 'CLANG_HOOK_CONFIG'
