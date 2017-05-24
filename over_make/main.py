import os
import pickle
import socket
import lib_hook
import selectors
import subprocess


def dispatch(sock, request, output_handler, hook_parser, hook_logger, hook_config, debug=False):
    if debug:
        d = {
            "output": "\033[1;49;34moutput\033[0m",
            "report": "\033[1;49;36mreport\033[0m",
            "summary": "\033[1;49;32msummary\033[0m",
        }
        print("request type", d[request["request_type"]])
    if request["request_type"] == "output":
        output_handler.handle_output(request["args"])
    elif request["request_type"] == "report":
        output_handler.handle_report(request["args"])
    elif request["request_type"] == "summary":
        output_handler.handle_summary(request["args"]["input_files"], request["args"]["output_file"])
    elif request["request_type"] == "parse_args":
        namespace, unknown = hook_parser.parse_known_args(request["args"]['argv'][1:])
        response = pickle.dumps((namespace, unknown))
        size = len(response).to_bytes(4, byteorder="big")
        sock.send(size + response)
    elif request["request_type"] == "log":
        hook_logger.dispatch(request)
    elif request["request_type"] == "get_config":
        response = pickle.dumps(hook_config)
        size = len(response).to_bytes(4, byteorder="big")
        sock.send(size + response)
    else:
        print("\033[1;49;31mUnknown request type: %s\033[0m", request)


def main():
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

    sel = selectors.DefaultSelector()

    def accept(s):
        conn, addr = s.accept()  # Should be ready
        if debug:
            print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)

    def read(conn):
        size = conn.recv(4)  # Should be ready
        bsize = int.from_bytes(size, byteorder="big")
        if debug:
            print("receiving", bsize, "bytes")
        data = conn.recv(bsize)
        if data:
            request = pickle.loads(data)
            dispatch(conn, request, output_handler, hook_parser, hook_logger, hook_config, debug=debug)
        else:
            if debug:
                print('closing', conn)
            sel.unregister(conn)
            conn.close()

    sel.register(sock, selectors.EVENT_READ, accept)

    if debug:
        print(args.command)
    command = [e for l in args.command for e in l.split()]
    if args.j is not None:
        command.append("-j%d" % args.j)

    p = subprocess.Popen(command)

    while p.poll() is None:
        events = sel.select(timeout=0.5)
        for key, event in events:
            callback = key.data
            callback(key.fileobj)

    output_handler.finalize()
    print("Command terminate with return code", p.returncode)
