#!/usr/bin/python3
"""A small script to make the work of clang but with more things under the carpet!
And fulfilling the PEP8!
You're going to love me!"""

import io
import os
import sys
import pickle
import pstats
import socket
import lib_hook
import cProfile
import selectors


def main():
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
            size = conn.recv(4)  # Should be ready
            bsize = int.from_bytes(size, byteorder="big")
            if debug:
                print("receiving", bsize, "bytes")
            data = conn.recv(bsize)
            response = pickle.loads(data)
            return response

        def send_request(request):
            size = len(request).to_bytes(4, byteorder="big")
            sock.send(size+request)

        def send_and_get(request):
            send_request(request)
            sel = selectors.DefaultSelector()
            sel.register(sock, selectors.EVENT_READ, read_response)
            events = sel.select()
            for key, event in events:
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
        output_handler.finalize()
    else:
        sock.close()


def profiled_main():
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

# echo "$@" >> ~/4A/LIP/llvm/log
# clang -emit-llvm -c test.c -o test.bc
# opt -O3 test.bc -o test.bc
# llc -filetype=obj test.bc -o test.o

# Tested with arguments like:
#   -DNDEBUG -I/home/cheche/4A/LIP/llvm/4.0.0/llvm/projects/test-suite/MultiSource/Benchmarks/MallocBench/cfrac
#   -I/home/cheche/4A/LIP/llvm/4.0.0/test-suite-build/MultiSource/Benchmarks/MallocBench/cfrac -w -Werror=date-time
#   -DNOMEMOPT -o CMakeFiles/cfrac.-dir/ptoa.c.o
#   -c /home/cheche/4A/LIP/llvm/4.0.0/llvm/projects/test-suite/MultiSource/Benchmarks/MallocBench/cfrac/ptoa.c
