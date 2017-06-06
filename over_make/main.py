"""Entrypoint of over-make."""
import pickle
import selectors
import subprocess

from .dispatch import dispatch
from .init import init


def main():
    """Entry point of over-make"""
    args, output_handler, hook_parser, hook_logger, hook_config, sock, debug = init()
    sel = selectors.DefaultSelector()

    def accept(master_sock):
        """Accept connexion, put the sock in the selector with the action "read"."""
        conn, addr = master_sock.accept()  # Should be ready
        if debug:
            print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)

    def read(conn):
        """Read from a ready socket. First, it reads 4 bytes (big-endian encoding) which is the size of the following
        of the request. Then <this size> bytes are read and decoded from pickle. The resulting dict is sent
        to dispatch(...)."""
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
        for key, _ in events:
            callback = key.data
            callback(key.fileobj)

    output_handler.finalize()
    print("Command terminate with return code", p.returncode)
