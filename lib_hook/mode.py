import os

from .hook_parser import OutputType
from .auto_number import AutoNumber


class Mode(AutoNumber):
    Compiling = ()
    Linking = ()
    CompilingAndLinking = ()


def get_mode(args, logger):
    if len(args.input_files) == 0:
        logger.panic("Need at least one input file", args)

    input_base_ext = [os.path.splitext(e) for e in args.input_files]

    if any(ext not in [".c", ".o", ".cc", ".cxx", ".C", ".cpp"] for (base, ext) in input_base_ext):
        logger.panic("File with unknown extension", args)

    all_c = all(ext in [".c", ".cc", ".cxx", ".C", ".cpp"] for (base, ext) in input_base_ext)
    all_obj = all(ext == ".o" for (base, ext) in input_base_ext)
    one_file = (len(args.input_files) == 1)

    if not all_c and not all_obj:
        logger.panic("Mixed .c and .o input files", args)

    mode = None

    if one_file:
        if all_c:
            if args.output_type == OutputType.Elf:
                mode = Mode.CompilingAndLinking
            elif args.output_type == OutputType.Obj:
                mode = Mode.Compiling
            elif args.output_file == OutputType.Asm:
                mode = Mode.Compiling
        elif all_obj:
            if args.output_type == OutputType.Elf:
                mode = Mode.Linking
            elif args.output_type == OutputType.Obj:
                logger.panic(".o -> .o is not supported", args)
            elif args.output_file == OutputType.Asm:
                logger.panic(".o -> .S is not supported", args)
    elif not one_file:
        if all_c:
            if args.output_file is None:
                if args.output_type == OutputType.Elf:
                    mode = Mode.CompilingAndLinking
                elif args.output_type == OutputType.Obj:
                    mode = Mode.Compiling
                elif args.output_file == OutputType.Asm:
                    mode = Mode.Compiling
            elif args.output_file is not None:
                if args.output_type == OutputType.Elf:
                    mode = Mode.CompilingAndLinking
                elif args.output_type == OutputType.Obj:
                    logger.panic("-o and multiple output are incompatible", args)
                elif args.output_file == OutputType.Asm:
                    logger.panic("-o and multiple output are incompatible", args)
        elif all_obj:
            if args.output_type == OutputType.Elf:
                mode = Mode.Linking
            elif args.output_type == OutputType.Obj:
                logger.panic(".o -> .o is not supported", args)
            elif args.output_file == OutputType.Asm:
                logger.panic(".o -> .S is not supported", args)

    return mode, input_base_ext
