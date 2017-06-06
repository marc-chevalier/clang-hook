"""This module contains as much code as possible which is shared between clang-hook and over-make."""
from .mode import Mode, get_mode
from .stage import Str_to_stage, Stage_to_str, Stage
from .filter import Filter, InvalidStage
from .logging import Logger, ServerLogger, ClientLogger, print_debug_info
from .compiler import Compiler
from .auto_number import AutoNumber
from .hook_config import HookConfig
from .hook_parser import OptimisationLevel, OutputType, usage, init_hook_parser
from .over_config import OverConfig
from .over_parser import init_over_parser
from .output_handler import OutputHandler
from .remote_output_handler import ClientOutputHandler, ServerOutputHandler
