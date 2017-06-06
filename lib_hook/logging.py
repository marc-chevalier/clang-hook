"""Everything for logging."""
import abc
import sys
import pickle
import logging
import logging.handlers
import datetime


class AbstractLogger(metaclass=abc.ABCMeta):
    """Abstract class that constraints loggers methods."""
    @abc.abstractmethod
    def panic(self, msg, args=None):
        """Log an error and quit abnormally."""
        pass

    @abc.abstractmethod
    def warning(self, msg, args=None):
        """Log a warning and continue."""
        pass

    @abc.abstractmethod
    def debug(self, msg):
        """Log debugging information."""
        pass

    @abc.abstractmethod
    def info(self, msg):
        """Log info information."""
        pass


class Logger:
    """Simple logger. Use 3 files: error, info, debug."""
    def __init__(self):
        self.pre_log_info = []
        self.pre_log_warning = []
        self.pre_log_debug = []
        self.logger_error = None
        self.logger_info = None
        self.logger_debug = None
        self.enable = None

    def panic(self, msg, args=None):
        """Log an error and quit abnormally."""
        print(msg)
        print("Aborting")
        if self.logger_error is not None:
            self.logger_error.critical(msg)
            self.logger_error.critical("    input: "+str(sys.argv))
            if args is not None:
                self.logger_error.critical("    args: "+str(args))
        sys.exit(2)

    def warning(self, msg, args=None):
        """Log a warning and continue."""
        if self.logger_error is not None:
            self.logger_error.warning(msg)
            self.logger_error.warning("    input: "+str(sys.argv))
            self.logger_error.warning("    args: "+str(args))
        elif self.enable is None:
            self.pre_log_warning.extend([msg, "    input: "+str(sys.argv), "   args: "+str(args)])

    def debug(self, msg):
        """Log debugging information."""
        if self.logger_debug is not None:
            self.logger_debug.debug(msg)
        elif self.enable is None:
            self.pre_log_debug.append(msg)

    def info(self, msg):
        """Log info information."""
        if self.logger_info is not None:
            self.logger_info.info(msg)
        elif self.enable is None:
            self.pre_log_info.append(msg)

    def init(self, args, config):
        """Initialize the logger. Used time-based rotating file handler. The hope is to easily separate log of different
        runs of the test suite."""
        if config.log:
            self.enable = True
            if config.error_log is None:
                error_log = "error.log"
            else:
                error_log = config.error_log
            if config.info_log is None:
                info_log = "info.log"
            else:
                info_log = config.info_log
            if config.debug_log is None:
                debug_log = "debug.log"
            else:
                debug_log = config.debug_log

            handler_error = logging.handlers.TimedRotatingFileHandler(error_log, when="w6", atTime=datetime.time(),
                                                                      encoding="utf-8")
            handler_info = logging.handlers.TimedRotatingFileHandler(info_log, when="w6", atTime=datetime.time(),
                                                                     encoding="utf-8")
            handler_debug = logging.handlers.TimedRotatingFileHandler(debug_log, when="w6", atTime=datetime.time(),
                                                                      encoding="utf-8")
            formatter = logging.Formatter('%(asctime)s: [%(levelname)s] %(message)s')
            handler_error.setFormatter(formatter)
            handler_info.setFormatter(formatter)
            handler_debug.setFormatter(formatter)
            handler_debug.setLevel(logging.DEBUG)
            handler_info.setLevel(logging.INFO)
            handler_error.setLevel(logging.ERROR)
            logger_debug = logging.getLogger("debug")
            logger_info = logging.getLogger("info")
            logger_error = logging.getLogger("error")
            logger_debug.setLevel(logging.DEBUG)
            logger_info.setLevel(logging.INFO)
            logger_error.setLevel(logging.ERROR)
            logger_error.addHandler(handler_error)
            logger_info.addHandler(handler_info)
            logger_debug.addHandler(handler_debug)
            for msg in self.pre_log_warning:
                self.warning(msg, args)
            for msg in self.pre_log_debug:
                self.debug(msg)
            for msg in self.pre_log_info:
                self.info(msg)
        else:
            self.enable = False


class ServerLogger(Logger):
    """A basic logger with a dispatch function to handle network request."""
    def dispatch(self, request):
        """Redirect the request to the right function."""
        if request["args"]["level"] == "info":
            self.info(request["args"]["msg"])
        elif request["args"]["level"] == "warn":
            self.warning(request["args"]["msg"], request["args"]["args"])
        elif request["args"]["level"] == "panic":
            self.panic(request["args"]["msg"], request["args"]["args"])
        elif request["args"]["level"] == "debug":
            self.debug(request["args"]["msg"])


class ClientLogger:
    """A logger that send everything via the given socket into standard dictionnay requests."""
    def __init__(self, socket):
        self.socket = socket

    def panic(self, msg: str, args=None):
        """Log an error and quit abnormally."""
        request = pickle.dumps({
            "request_type": "log",
            "args": {
                "level": "panic",
                "msg": msg,
                "args": args
                },
        })
        size = len(request).to_bytes(4, byteorder="big")
        self.socket.send(size+request)
        sys.exit(2)

    def warning(self, msg, args=None):
        """Log a warning and continue."""
        request = pickle.dumps({
            "request_type": "log",
            "args": {
                "level": "warning",
                "msg": msg,
                "args": args
                },
        })
        size = len(request).to_bytes(4, byteorder="big")
        self.socket.send(size+request)

    def debug(self, msg):
        """Log debugging information."""
        request = pickle.dumps({
            "request_type": "log",
            "args": {
                "level": "debug",
                "msg": msg,
                },
        })
        size = len(request).to_bytes(4, byteorder="big")
        self.socket.send(size+request)

    def info(self, msg):
        """Log info information."""
        request = pickle.dumps({
            "request_type": "log",
            "args": {
                "level": "info",
                "msg": msg,
                },
        })
        size = len(request).to_bytes(4, byteorder="big")
        self.socket.send(size+request)


class DummyLogger(AbstractLogger):
    """A stupid logger that keeps everything in lists. Used for testing purposes."""
    def __init__(self):
        self.panic_list = []
        self.warning_list = []
        self.debug_list = []
        self.info_list = []

    def panic(self, msg, args=None):
        """Log an error and does NOT quit abnormally."""
        self.panic_list.append(msg)

    def warning(self, msg, args=None):
        """Log a warning and continue."""
        self.warning_list.append(msg)

    def debug(self, msg):
        """Log debugging information."""
        self.debug_list.append(msg)

    def info(self, msg):
        """Log info information."""
        self.info_list.append(msg)


def print_debug_info(name, value):
    """A nice print with color for debugging purpose."""
    print("\033[34m%s\033[0m: %s" % (name, value))
