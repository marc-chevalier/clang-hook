import sys
import pickle
import logging
import datetime
import logging.handlers


class Logger:
    def __init__(self):
        self.pre_log_info = []
        self.pre_log_warning = []
        self.pre_log_debug = []
        self.logger_error = None
        self.logger_info = None
        self.logger_debug = None
        self.enable = None

    def panic(self, msg, args=None):
        print(msg)
        print("Aborting")
        if self.logger_error is not None:
            self.logger_error.critical(msg)
            self.logger_error.critical("    input: "+str(sys.argv))
            if args is not None:
                self.logger_error.critical("    args: "+str(args))
        sys.exit(2)

    def warning(self, msg, args=None):
        if self.logger_error is not None:
            self.logger_error.warning(msg)
            self.logger_error.warning("    input: "+str(sys.argv))
            self.logger_error.warning("    args: "+str(args))
        elif self.enable is None:
            self.pre_log_warning.extend([msg, "    input: "+str(sys.argv), "   args: "+str(args)])

    def debug(self, msg):
        if self.logger_debug is not None:
            self.logger_debug.debug(msg)
        elif self.enable is None:
            self.pre_log_debug.append(msg)

    def info(self, msg):
        if self.logger_info is not None:
            self.logger_info.info(msg)
        elif self.enable is None:
            self.pre_log_info.append(msg)

    def init(self, args, config):
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
    def dispatch(self, request):
        if request["args"]["level"] == "info":
            self.info(request["args"]["msg"])
        elif request["args"]["level"] == "warn":
            self.warning(request["args"]["msg"], request["args"]["args"])
        elif request["args"]["level"] == "panic":
            self.panic(request["args"]["msg"], request["args"]["args"])
        elif request["args"]["level"] == "debug":
            self.debug(request["args"]["msg"])


class ClientLogger:
    def __init__(self, socket):
        self.socket = socket

    def panic(self, msg: str, args=None):
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
        request = pickle.dumps({
            "request_type": "log",
            "args": {
                "level": "info",
                "msg": msg,
                },
        })
        size = len(request).to_bytes(4, byteorder="big")
        self.socket.send(size+request)


def print_debug_info(n, s):
    print("\033[34m%s\033[0m: %s" % (n, s))
