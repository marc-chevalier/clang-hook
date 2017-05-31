from unittest import TestCase
from lib_hook.stage import Stage, str_to_stage, stage_to_str


class TestStage(TestCase):
    def testStrToStage(self):
        self.assertEqual(str_to_stage("clang"), Stage.Clang)
        self.assertEqual(str_to_stage("Clang"), Stage.Clang)
        self.assertEqual(str_to_stage("opt"), Stage.Opt)
        self.assertEqual(str_to_stage("Opt"), Stage.Opt)
        self.assertEqual(str_to_stage("llc"), Stage.Llc)
        self.assertEqual(str_to_stage("Llc"), Stage.Llc)
        self.assertEqual(str_to_stage("link"), Stage.Link)
        self.assertEqual(str_to_stage("Link"), Stage.Link)
        self.assertRaises(KeyError, str_to_stage, "bla")

    def testStageToStr(self):
        self.assertEqual(stage_to_str(Stage.Clang), "clang")
        self.assertEqual(stage_to_str(Stage.Opt), "opt")
        self.assertEqual(stage_to_str(Stage.Llc), "llc")
        self.assertEqual(stage_to_str(Stage.Link), "link")
