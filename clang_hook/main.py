""" Entrypoint of clang-hook. There is a profiled version, to use with care.
"""

import io
import os
import sys
import pickle
import pstats
import socket
import cProfile
import selectors

import lib_hook


def main():
    """
    Entrypoint of clang-hook command. It support both standalone mode and network mode.
    """
    sock = None
    if "OVER_CLANG_ADDR" in os.environ:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = os.environ["OVER_CLANG_ADDR"]
        port = int(os.environ["OVER_CLANG_PORT"])
        sock.connect((addr, port))
        logger = lib_hook.ClientLogger(sock)
        debug = False

        request_args = pickle.dumps({
            "request_type": "parse_args",
            "args": {
                "argv": sys.argv,
            },
        })
        request_config = pickle.dumps({
            "request_type": "get_config",
            "args": {
            },
        })

        def read_response(conn):
            """Read a aize encoded on 4 bytes and then the request of this size. Thus, everything must be send at the
            same time otherwise, there is nothing to read and recv() throws an exception.

            It is used as the callback of the socket."""
            size = conn.recv(4)  # Should be ready
            bsize = int.from_bytes(size, byteorder="big")
            if debug:
                print("receiving", bsize, "bytes")
            data = conn.recv(bsize)
            response = pickle.loads(data)
            return response

        def send_request(request):
            """Send a request preceded by their size on 4 bytes (big endian). The size and the request are send at
            once."""
            size = len(request).to_bytes(4, byteorder="big")
            sock.send(size+request)

        def send_and_get(request):
            """Send a request, wait for a response and return it."""
            send_request(request)
            sel = selectors.DefaultSelector()
            sel.register(sock, selectors.EVENT_READ, read_response)
            events = sel.select()
            for key, _ in events:
                callback = key.data
                return callback(key.fileobj)

        args, unknown = send_and_get(request_args)
        debug = args.hook is not None and "debug" in args.hook
        hook_config = send_and_get(request_config)

        compiler = lib_hook.Compiler(args, hook_config, logger, unknown)
        if debug:
            print("Run in network mode.")

        output_handler = lib_hook.ClientOutputHandler(hook_config, logger, sock)
    else:
        hook_config = lib_hook.HookConfig()
        logger = lib_hook.Logger()
        args, unknown = lib_hook.init_hook_parser().parse_known_args()

        debug = args.hook is not None and "debug" in args.hook

        hook_config.init(logger.info, arg_path=args.hook_config, debug=debug)
        logger.init(args, hook_config)

        compiler = lib_hook.Compiler(args, hook_config, logger)
        if debug:
            print("Run in standalone mode.")
        output_handler = lib_hook.OutputHandler(hook_config, logger)

    if debug:
        lib_hook.print_debug_info("args.hook_config", args.hook_config)
        lib_hook.print_debug_info("args.hook", args.hook)
        lib_hook.print_debug_info("defines", args.defines)
        lib_hook.print_debug_info("warnings", args.warnings)
        lib_hook.print_debug_info("includes", args.includes)
        lib_hook.print_debug_info("links", args.links)
        lib_hook.print_debug_info("input", " ".join(args.input_files))
        lib_hook.print_debug_info("output file", args.output_file)
        lib_hook.print_debug_info("output type", args.output_type)
        lib_hook.print_debug_info("optimization level", args.optimization_level)

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

    if sock is None:
        if isinstance(output_handler, lib_hook.OutputHandler):  # Make type checkers happy
            output_handler.finalize()
    else:
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
    # cProfile.runctx('main()', globals(), locals())

if __name__ == "__main__":
    main()
