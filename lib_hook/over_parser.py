import argparse


def init_over_parser():
    p = argparse.ArgumentParser(description='over-make.')
    p.add_argument("command", metavar="command", type=str, nargs='+', help="The command to run")
    p.add_argument("-j", metavar="n", type=int, dest="j", action="store", help="Just -j of make")
    p.add_argument('--hook-config', metavar="path", dest='hook_config', action='store', type=str,
                   help="A path to the hook config. It will be look at first.")
    p.add_argument('--over-config', metavar="path", dest='over_config', action='store', type=str,
                   help="A path to the over config. It will be look at first.")
    p.add_argument('--over', metavar="flag", dest='over', action='append', type=str,
                   help="Give a parameter to the hook. Must be repeted before each hook argument")
    p.add_argument('--version', action='version', version='%(prog)s 0.1')
    return p
