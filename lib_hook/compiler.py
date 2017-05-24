import subprocess
import typing

from .output_handler import OutputHandler
from .hook_parser import OptimisationLevel, OutputType
from .passes import get_passes
from .logging import print_debug_info
from .hook_config import HookConfig
from .stage import Stage


class Compiler:
    def __init__(self, args, config: HookConfig, logger, unknown: typing.Optional[typing.List[str]]=None):
        self.hook_config = config
        self.args = args
        self.logger = logger
        self.optimization_str = {OptimisationLevel.O0: "",
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
              debug: bool=False):
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
        self.opt_base = ["opt"] + self.passes

    def opt(self,
            input_file: str,
            output_file: str,
            c_file: str,
            obj_file: str,
            output_handler: OutputHandler,
            debug: bool=False):
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
            debug: bool=False):
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
             debug: bool=False):
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
