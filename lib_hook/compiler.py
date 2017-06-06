"""A class that prepare compilation commands and runs them."""
import subprocess
import typing

from .stage import Stage
from .passes import get_passes
from .logging import print_debug_info
from .hook_config import HookConfig
from .hook_parser import OptimisationLevel, OutputType
from .output_handler import OutputHandler


class Compiler:
    """A class that prepare compilation commands and runs them."""
    def __init__(self, args, config: HookConfig, logger, unknown: typing.Optional[typing.List[str]]=None):
        self.hook_config = config
        self.args = args
        self.logger = logger
        self.optimization_str = {
            OptimisationLevel.O0: "",
            OptimisationLevel.O1: "-O1",
            OptimisationLevel.O2: "-O2",
            OptimisationLevel.O3: "-O3",
            }[args.optimization_level]
        self.passes = get_passes(config, args.optimization_level)
        self.unknown = filter(lambda s: s[0] == '-', [] if unknown is None else unknown)

        self.clang_base = None
        self.opt_base = None
        self.llc_base = None
        self.link_base = None

        self.init_clang()
        self.init_opt()
        self.init_llc()
        self.init_link()

    def init_clang(self):
        """Initialize the clang command. It contains everything except the input and output file. It makes the
        generation of new commands faster."""
        self.clang_base = ["clang", "-emit-llvm", "-c", self.optimization_str]
        if self.args.warnings is not None:
            self.clang_base.extend(self.args.warnings)
        if self.args.standard is not None:
            self.clang_base.append("-std=%s" % self.args.standard)
        if self.args.defines is not None:
            self.clang_base.extend(self.args.defines)
        if self.args.includes is not None:
            self.clang_base.extend(self.args.includes)
        self.clang_base.extend(self.unknown)
        self.clang_base.append("-o")

    def clang(self,
              input_file: str,
              output_file: str,
              c_file: str,
              obj_file: str,
              output_handler: OutputHandler,
              debug: bool = False):
        """Completes the clang command and launch it."""
        clang_command = self.clang_base + [output_file, input_file]

        self.logger.info(str(clang_command))
        self.logger.info("  " + " ".join(clang_command))
        if debug:
            print_debug_info("clang_command", clang_command)

        try:
            ret = subprocess.run(clang_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8"))
            raise

        output_handler.handle_output(ret.stdout.decode("utf-8"), Stage.Clang, c_file, obj_file)

    def init_opt(self):
        """Initialize the opt command. It contains everything except the input and output file. It makes the
        generation of new commands faster."""
        self.opt_base = ["opt"] + self.passes

    def opt(self,
            input_file: str,
            output_file: str,
            c_file: str,
            obj_file: str,
            output_handler: OutputHandler,
            debug: bool = False):
        """Completes the opt command and launch it."""
        opt_command = self.opt_base + [input_file, "-o", output_file]

        self.logger.info(str(opt_command))
        self.logger.info("  " + " ".join(opt_command))
        if debug:
            print_debug_info("opt_command", opt_command)

        try:
            ret = subprocess.run(opt_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8"))
            raise

        output_handler.handle_output(ret.stdout.decode("utf-8"), Stage.Opt, c_file, obj_file)

    def init_llc(self):
        """Initialize the llc command. It contains everything except the input and output file. It makes the
        generation of new commands faster."""
        if self.args.output_type == OutputType.Asm:
            llc_output_type = "asm"
        else:
            llc_output_type = "obj"
        self.llc_base = ["llc", "-filetype=%s" % llc_output_type]

    def llc(self,
            input_file: str,
            output_file: typing.Optional[str],
            c_file: str,
            obj_file: str,
            output_handler: OutputHandler,
            debug: bool = False):
        """Completes the llc command and launch it."""
        if output_file is None:
            llc_command = self.llc_base + [input_file]
        else:
            llc_command = self.llc_base + [input_file, "-o", output_file]

        self.logger.info(str(llc_command))
        self.logger.info("  " + " ".join(llc_command))
        if debug:
            print_debug_info("llc_command", llc_command)

        try:
            ret = subprocess.run(llc_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8"))
            raise
        output_handler.handle_output(ret.stdout.decode("utf-8"), Stage.Llc, c_file, obj_file)

    def init_link(self):
        """Initialize the link command. It contains everything except the input and output file. It makes the
        generation of new commands faster.
        The link use clang for the sake of simplicity."""
        self.link_base = ["clang"]
        self.clang_base.extend(self.unknown)

        if self.args.links is not None:
            self.link_base.extend(self.args.links)

        if self.hook_config.link_flags is not None:
            self.link_base.extend(self.hook_config.link_flags)

    def link(self,
             input_files: typing.List[str],
             output_file: typing.Optional[str],
             output_handler: OutputHandler,
             debug: bool = False):
        """Completes the link command and launch it."""
        if output_file is None:
            link_command = self.link_base + input_files
        else:
            link_command = self.link_base + input_files + ["-o", output_file]

        self.logger.info(str(link_command))
        self.logger.info("  " + " ".join(link_command))

        if debug:
            print_debug_info("link_command", link_command)
        try:
            ret = subprocess.run(link_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8"))
            raise
        output = ret.stdout.decode("utf-8")
        output_handler.handle_output(output, Stage.Link, input_files, output_file)
        output_handler.make_summary(input_files, output_file)
