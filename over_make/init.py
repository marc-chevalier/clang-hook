"""Contains init() to setup everything."""
import os
import socket
import lib_hook


def init():
    """Returns everything over_make needs to run."""
    args = lib_hook.init_over_parser().parse_args()
    debug = args.over is not None and "debug" in args.over
    over_config = lib_hook.OverConfig()
    over_logger = lib_hook.Logger()
    over_config.init(over_logger.info, arg_path=args.over_config, debug=debug)
    over_logger.init(args, over_config)

    hook_parser = lib_hook.init_hook_parser()
    hook_config = lib_hook.HookConfig()
    hook_logger = lib_hook.ServerLogger()
    config = args.hook_config if args.hook_config is not None else over_config.hook_config
    hook_config.init(hook_logger.info, arg_path=config, debug=debug)
    hook_logger.init(args, hook_config)

    if args.hook_config is not None:
        os.environ["CLANG_HOOK_CONFIG"] = args.hook_config
    elif over_config.hook_config is not None:
        os.environ["CLANG_HOOK_CONFIG"] = over_config.hook_config

    output_handler = lib_hook.ServerOutputHandler(hook_config)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 0))
    sock.listen(100)
    sock.setblocking(False)

    os.environ["OVER_CLANG_ADDR"] = str(sock.getsockname()[0])
    os.environ["OVER_CLANG_PORT"] = str(sock.getsockname()[1])

    return args, output_handler, hook_parser, hook_logger, hook_config, sock, debug
