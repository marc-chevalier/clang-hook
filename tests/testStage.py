from unittest import TestCase
from lib_hook.stage import Stage, Str_to_stage, Stage_to_str


class TestStage(TestCase):
    def testStrToStage(self):
        self.assertEqual(Str_to_stage("clang"), Stage.Clang)
        self.assertEqual(Str_to_stage("Clang"), Stage.Clang)
        self.assertEqual(Str_to_stage("opt"), Stage.Opt)
        self.assertEqual(Str_to_stage("Opt"), Stage.Opt)
        self.assertEqual(Str_to_stage("llc"), Stage.Llc)
        self.assertEqual(Str_to_stage("Llc"), Stage.Llc)
        self.assertEqual(Str_to_stage("link"), Stage.Link)
        self.assertEqual(Str_to_stage("Link"), Stage.Link)
        self.assertRaises(KeyError, Str_to_stage, "bla")

    def testStageToStr(self):
        self.assertEqual(Stage_to_str(Stage.Clang), "clang")
        self.assertEqual(Stage_to_str(Stage.Opt), "opt")
        self.assertEqual(Stage_to_str(Stage.Llc), "llc")
        self.assertEqual(Stage_to_str(Stage.Link), "link")
