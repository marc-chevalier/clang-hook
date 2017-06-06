"""argparse based argument parser for clang-hook"""
import abc
import sys
import argparse

from .auto_number import AutoNumber


class OptimisationLevel(AutoNumber):
    """Enumeration for -On option. Default is -O0."""
    O0 = ()
    O1 = ()
    O2 = ()
    O3 = ()


class OutputType(AutoNumber):
    """Enumeration for the output type of the given command."""
    Obj = ()
    Asm = ()
    Elf = ()


def usage():
    """Pretty usage message <3"""
    print(sys.argv[0]+"[clang options]")


class OAction(argparse.Action):
    """Handles -On option."""
    def __call__(self, _parser, namespace, values, option_string=None):
        opt = {
            "0": OptimisationLevel.O0,
            "1": OptimisationLevel.O1,
            "2": OptimisationLevel.O2,
            "3": OptimisationLevel.O3,
        }[values]
        setattr(namespace, self.dest, opt)


class AbstractFlagAction(argparse.Action, metaclass=abc.ABCMeta):
    """Handles options of the kind -Xfoo. It stores -Xfoo (and not just foo) to be easily given to the underlying
    commands"""
    def __init__(self, prefix, option_strings, dest, **kwargs):
        self.prefix = prefix
        super(AbstractFlagAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, _parser, namespace, values, option_string=None):
        if self.dest in namespace:
            old = getattr(namespace, self.dest)
        else:
            old = []
        if old is None:
            old = []
        old.append(self.prefix + str(values))
        setattr(namespace, self.dest, old)


class WAction(AbstractFlagAction):
    """Handles warning flags"""
    def __init__(self, option_strings, dest, **kwargs):
        super(WAction, self).__init__("-W", option_strings, dest, **kwargs)


class LAction(AbstractFlagAction):
    """Handles link flags"""
    def __init__(self, option_strings, dest, **kwargs):
        super(LAction, self).__init__("-l", option_strings, dest, **kwargs)


class DAction(AbstractFlagAction):
    """Handles define flags"""
    def __init__(self, option_strings, dest, **kwargs):
        super(DAction, self).__init__("-D", option_strings, dest, **kwargs)


class IAction(AbstractFlagAction):
    """Handles include flags"""
    def __init__(self, option_strings, dest, **kwargs):
        super(IAction, self).__init__("-I", option_strings, dest, **kwargs)


def init_hook_parser():
    """Builds and returns the argument parser."""
    p = argparse.ArgumentParser(description='Hook for clang.')
    p.add_argument("input_files", metavar="File", type=str, nargs='+', help="A file to compile")
    p.add_argument('-D', metavar="flag", dest='defines', action=DAction, type=str, help="A define")
    p.add_argument('-I', metavar="path", dest='includes', action=IAction, type=str, help="An include")
    p.add_argument('-l', metavar="flag", dest='links', action=LAction, type=str, help="Enable a link flag")
    p.add_argument('-W', metavar="flag", dest='warnings', action=WAction, type=str, help="Enable a warning")
    p.add_argument('-w', dest='warnings', action='append_const', const="-w", help="Suppress all warnings")
    p.add_argument('-std', dest='standard', action='store', help="Choose the standard")
    p.add_argument('-o', metavar="path", dest='output_file', action='store', type=str, help="Output file")
    p.add_argument('-c', metavar="path", dest='output_type', action='store_const', const=OutputType.Obj,
                   default=OutputType.Elf, help="To bytecode")
    p.add_argument('-S', dest='output_type', action='store_const', const=OutputType.Asm,
                   default=OutputType.Elf, help="To assembly")
    p.add_argument('-rdynamic', dest='links', action='append_const', const='-rdynamic', help="export dynamic")
    p.add_argument('-O', metavar="level", dest='optimization_level', action=OAction, default=OptimisationLevel.O0,
                   help="Optimization level")
    p.add_argument('--hook', metavar="flag", dest='hook', action='append', type=str,
                   help="Give a parameter to the hook. Must be repeted before each hook argument")
    p.add_argument('--hook-config', metavar="path", dest='hook_config', action='store', type=str,
                   help="A path to the config. It will be look at first.")
    p.add_argument('--version', action='version', version='%(prog)s 0.1')
    return p
