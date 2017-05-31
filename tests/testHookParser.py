from unittest import TestCase
from lib_hook.hook_parser import init_hook_parser, OptimisationLevel, OutputType


class TestHookParser(TestCase):
    def setUp(self):
        self.parser = init_hook_parser()

    def testSimple(self):
        namespace, unknown = self.parser.parse_known_args(["-o", "file.o", "file.c"])
        self.assertListEqual(namespace.input_files, ["file.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, [])

    def testMultipleInputs(self):
        namespace, unknown = self.parser.parse_known_args(["-c", "file.c", "file2.c"])
        self.assertListEqual(namespace.input_files, ["file.c", "file2.c"])
        self.assertEqual(namespace.output_file, None)
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Obj)
        self.assertListEqual(unknown, [])

        # Not cool, cf. http://bugs.python.org/issue14191
        namespace, unknown = self.parser.parse_known_args(["file2.c", "-o", "file.o", "file.c"])
        self.assertListEqual(namespace.input_files, ["file2.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, ["file.c"])

    def testDefine(self):
        namespace, unknown = self.parser.parse_known_args(["-o", "file.o", "file.c", "-DFLAG", "-D", "FLAG_BIS"])
        self.assertListEqual(namespace.input_files, ["file.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertEqual(namespace.defines, ["-DFLAG", "-DFLAG_BIS"])
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, [])

    def testInclude(self):
        namespace, unknown = self.parser.parse_known_args(["-o", "file.o", "file.c", "-Iwhere/am/I", "-I", "/here"])
        self.assertListEqual(namespace.input_files, ["file.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertEqual(namespace.includes, ["-Iwhere/am/I", "-I/here"])
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, [])

    def testLink(self):
        namespace, unknown = self.parser.parse_known_args(["-o", "file.o", "file.c", "-lm"])
        self.assertListEqual(namespace.input_files, ["file.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertEqual(namespace.links, ["-lm"])
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, [])

    def testWarn(self):
        namespace, unknown = self.parser.parse_known_args(["-o", "file.o", "file.c", "-w", "-Wall", "-Wextra"])
        self.assertListEqual(namespace.input_files, ["file.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertEqual(namespace.warnings, ["-w", "-Wall", "-Wextra"])
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, [])

    def testOpt(self):
        namespace, unknown = self.parser.parse_known_args(["-o", "file.o", "file.c", "-O1"])
        self.assertListEqual(namespace.input_files, ["file.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O1)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, [])

    def testHook(self):
        namespace, unknown = self.parser.parse_known_args(["-o", "file.o", "file.c", "--hook", "debug", "--hook", "a"])
        self.assertListEqual(namespace.input_files, ["file.c"])
        self.assertEqual(namespace.output_file, "file.o")
        self.assertListEqual(namespace.hook, ["debug", "a"])
        self.assertEqual(namespace.optimization_level, OptimisationLevel.O0)
        self.assertEqual(namespace.output_type, OutputType.Elf)
        self.assertListEqual(unknown, [])
