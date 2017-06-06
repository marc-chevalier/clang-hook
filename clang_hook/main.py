""" Entrypoint of clang-hook. There is a profiled version, to use with care.
"""

import io
import pstats
import cProfile

import lib_hook

from .init import init


def main():
    """
    Entrypoint of clang-hook command. It support both standalone mode and network mode.
    """
    args, compiler, logger, output_handler, sock, debug = init()
    mode, input_base_ext = lib_hook.get_mode(args, logger)

    if mode in [lib_hook.Mode.Compiling, lib_hook.Mode.CompilingAndLinking]:
        logger.info("The following command will be run")
        for (base, ext) in input_base_ext:
            c_file = base + ext
            bc_file = "%s.bc" % base

            if mode == lib_hook.Mode.CompilingAndLinking:
                obj_file = "%s.o" % base
            elif args.output_file is not None:
                obj_file = args.output_file
            else:
                obj_file = "%s.o" % base

            compiler.clang(c_file, bc_file, c_file, obj_file, output_handler, debug)
            compiler.opt(bc_file, bc_file, c_file, obj_file, output_handler, debug)
            compiler.llc(bc_file, obj_file, c_file, obj_file, output_handler, debug)

    if mode in [lib_hook.Mode.Linking, lib_hook.Mode.CompilingAndLinking]:
        if mode == lib_hook.Mode.CompilingAndLinking:
            link_input = ["%s.o" % base for (base, ext) in input_base_ext]
        else:
            link_input = args.input_files
        if args.output_file is not None:
            link_output = args.output_file
        else:
            link_output = None

        compiler.link(link_input, link_output, output_handler)
        if debug:
            lib_hook.print_debug_info("link_input", link_input)
            lib_hook.print_debug_info("link_output", link_output)

    output_handler.finalize()
    if sock is not None:
        sock.close()


def profiled_main():
    """A profiled version of clang-hook known as profiled-clang-hook. To use with care since it tends to be very
    voluble"""
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

if __name__ == "__main__":
    main()
