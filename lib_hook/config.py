"""Defines a class used as a base for configurations"""
import os
import abc
import json


class InvalidConfig(Exception):
    """Exception raised when there is an error in the config."""
    pass


class BaseConfig(metaclass=abc.ABCMeta):
    """Abstract class which should be the base of all config class. It looks for the config file, open it and parses
    it."""
    def __init__(self):
        self.data = None

    def init(self, info_logger, name, debug=False, arg_path=None):
        """Read and parse the config file."""
        try:
            with open(self.get_config_path(name, info_logger, debug, arg_path)) as fd:
                self.data = json.load(fd)
                self.parse_config()
        except ValueError as exc:
            raise InvalidConfig(*exc.args)
        except InvalidConfig:
            self.data = {}
            self.parse_config()

    @classmethod
    def get_config_path(cls, name, info_logger, debug, arg_path):
        """Looks fot the config file at standard locations: the environment variable, ., ~, etc/<name>.conf"""
        paths = [cls.get_config_env_path(), os.curdir, os.path.expanduser("~"), "/etc/%s" % name]
        paths = list(filter(lambda p: p is not None, paths))
        paths = list(map(lambda p: os.path.join(p, "%s.conf" % name), paths))
        if arg_path is not None:
            paths = [arg_path] + paths
        for path in paths:
            if os.path.exists(path):
                if debug:
                    print("Config found at %s" % path)
                info_logger("Config found at %s" % path)
                return path
            else:
                if debug:
                    print("Config not found at %s" % path)
                info_logger("Config not found at %s" % path)

        info_logger("Can't find config file")
        info_logger("Could not find config file, please set environment variable $%s or put a %s.conf "
                    "file at %s, %s or %s" % (name, cls.get_config_path_variable(), os.curdir, os.path.expanduser("~"),
                                              "/etc/%s" % name))

        raise InvalidConfig("Not found")

    @classmethod
    def get_config_env_path(cls):
        """Returns the path contains in the environement variable. If the variable does not exist, returns None"""
        path = os.environ.get(cls.get_config_path_variable(), '')
        if not path:
            return None
        return path

    @abc.abstractmethod
    def parse_config(self):
        """Should be implemented to parse the configuration from a dictionary (which comes from the JSON of the config
        file)"""
        pass

    @classmethod
    @abc.abstractmethod
    def get_config_path_variable(cls):
        """Should be implemented to return a string naming the environment variable used for locating the config
        file."""
        pass
