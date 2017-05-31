from unittest import TestCase
from lib_hook.compiler import Compiler
from lib_hook.hook_parser import init_hook_parser
from lib_hook.hook_config import HookConfig


class TestCompiler(TestCase):
    def setUp(self):
        parser = init_hook_parser()
        args = parser.parse_args(["file.c", "-o", "file2.c", "-O0", "-Wall", "-lm"])
        config = HookConfig()
        config.data = \
            {
                "load": ["/somewhere/truc.so"],
                "passes": ["-hello", "-stats"],
                "link_flags": ["-pthread"],
            }
        config.parse_config()
        self.compiler = Compiler(args, config, None)

    def testClang(self):
        self.assertListEqual(self.compiler.clang_base, ["clang", "-emit-llvm", "-c", "", "-Wall", "-o"])

    def testOpt(self):
        self.assertListEqual(self.compiler.opt_base, ["opt", "-load", "/somewhere/truc.so", "-hello", "-stats"])

    def testLlc(self):
        self.assertListEqual(self.compiler.llc_base, ["llc", "-filetype=obj"])

    def testLink(self):
        self.assertListEqual(self.compiler.link_base, ["clang", "-lm", "-pthread"])
