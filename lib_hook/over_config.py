"""Configuration of over-make."""

from .config import BaseConfig


class OverConfig(BaseConfig):
    """Configuration of over-make."""
    __slots__ = ("data", "error_log", "infor_log", "debug_log", "log", "output_file", "report_file", "hook_config")

    def __init__(self):
        self.error_log = None
        self.info_log = None
        self.debug_log = None
        self.log = None

        self.output_file = None
        self.report_file = None

        self.hook_config = None
        super(OverConfig, self).__init__()

    def init(self, info_logger, name=None, debug=False, arg_path=None):
        """Search the config file and parse it. For tests purposes, this function won't be called, allowing the test
        suite to put arbitrary values in attributes."""
        super(OverConfig, self).init(info_logger, "over-make" if name is None else name, debug, arg_path)

    def parse_config(self,):
        """Tells how to parse the dictionnary. Also define default values."""
        self.error_log = self.data.get("error_log", None)
        self.info_log = self.data.get("info_log", None)
        self.debug_log = self.data.get("debug_log", None)
        self.log = bool(self.data.get("log", True))
        self.output_file = self.data.get("output_file", None)

        self.report_file = self.data.get("report_file", None)

        self.hook_config = self.data.get("hook_config", None)

    @classmethod
    def get_config_path_variable(cls):
        """Returns the environment vartiable containing the path of the configuration file."""
        return 'OVER_MAKE_CONFIG'
