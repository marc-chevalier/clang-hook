from unittest import TestCase
from lib_hook.mode import get_mode, Mode
from lib_hook.logging import DummyLogger
from lib_hook.hook_parser import init_hook_parser


class TestMode(TestCase):
    def testMode(self):
        parser = init_hook_parser()
        logger = DummyLogger()

        t = [(["file1.o", "file2.o"], Mode.Linking, [("file1", ".o"), ("file2", ".o")]),
             (["file1.cpp", "file2.c"], Mode.CompilingAndLinking, [("file1", ".cpp"), ("file2", ".c")]),
             (["-c", "file1.cpp", "file2.c"], Mode.Compiling, [("file1", ".cpp"), ("file2", ".c")]),
             ]

        for (command, m, files) in t:
            args = parser.parse_args(command)
            mode, input_base_ext = get_mode(args, logger)
            self.assertEqual(mode, m)
            self.assertEqual(input_base_ext, files)
