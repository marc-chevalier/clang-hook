"""Defines an abstract class of output handlers."""
import abc
import typing

from .stage import Stage


class AbstractOutputHandler(metaclass=abc.ABCMeta):
    """Assuming these classes will be enough"""
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    @abc.abstractmethod
    def handle_output(self,
                      output: str,
                      stage: Stage,
                      input_file: typing.Union[str, typing.List[str]],
                      output_file: typing.Union[str, typing.List[str]]):
        """Runs filter on the output of underlying commands."""
        pass

    @abc.abstractmethod
    def make_summary(self, input_files: typing.List[str], output_file: str):
        """Make the summary of all reports"""
        pass

    @abc.abstractmethod
    def finalize(self):
        """Finalize the output files. Not always useful."""
        pass
