from .config import BaseConfig


class OverConfig(BaseConfig):
    __slots__ = ("data", )

    def __init__(self):
        self.error_log = None
        self.info_log = None
        self.debug_log = None
        self.log = None

        self.output_file = None
        self.report_file = None

        self.hook_config = None
        super(OverConfig, self).__init__()

    def init(self, info_logger, name="over-make", debug=False, arg_path=None):
        super(OverConfig, self).init(name, info_logger, debug, arg_path)

    def parse_config(self,):
        self.error_log = self.data.get("error_log", None)
        self.info_log = self.data.get("info_log", None)
        self.debug_log = self.data.get("debug_log", None)
        self.log = bool(self.data.get("log", True))
        self.output_file = self.data.get("output_file", None)

        self.report_file = self.data.get("report_file", None)

        self.hook_config = self.data.get("hook_config", None)

    @classmethod
    def get_config_path_variable(cls):
        return 'OVER_MAKE_CONFIG'
