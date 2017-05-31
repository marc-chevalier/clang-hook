from unittest import TestCase

from lib_hook import OutputHandler, HookConfig, Stage
from lib_hook.logging import DummyLogger


class TestOutputHandler(TestCase):
    def setUp(self):
        self.output_handler = OutputHandler.__new__(OutputHandler)  # Wow ! Much trick. We don"t want to run __init__
        # since it reads files.
        self.output_handler.config = HookConfig()
        self.output_handler.config.data = \
            {
                "log": False,
                "output_stages": ["opt"],
                "filters": [{
                    "name": "f1",
                    "pattern": "(?<=Hello: )[A-Za-z_][A-Za-z_0-9]*",
                    "stages": ["opt"],
                    "type": "string",
                    "mode": "lookaround",
                    "summary": "append",
                }],
            }
        self.output_handler.config.parse_config()
        self.output_handler.logger = DummyLogger()
        self.output_handler.output_obj = {"config": self.output_handler.config.data, "compils": []}
        self.output_handler.report_obj = {"config": self.output_handler.config.data, "compils": [], "summary": []}

    def testHandleOutput(self):
        self.output_handler.handle_output("Hello: test", Stage.Opt, "in", "out")
        self.output_handler.handle_output("Hello: test2", Stage.Opt, ["in1", "in2"], "output_files")
        self.output_handler.handle_output("Hello: test3", Stage.Opt, "in", ["out1", "out2"])
        self.output_handler.handle_output("Hello: test4", Stage.Opt, ["in1", "in2"], ["out1", "out2"])
        self.assertDictEqual(
            self.output_handler.output_obj,
            {
                "compils":
                    [
                        {"input_file": "in", "stage": "opt", "output_file": "out", "stdout": "Hello: test"},
                        {"input_file": ["in1", "in2"], "stage": "opt", "output_file": "output_files",
                         "stdout": "Hello: test2"},
                        {"input_file": "in", "stage": "opt", "output_file": ["out1", "out2"], "stdout": "Hello: test3"},
                        {"input_file": ["in1", "in2"], "stage": "opt", "output_file": ["out1", "out2"],
                         "stdout": "Hello: test4"}
                    ],
                "config": self.output_handler.config.data})
        self.assertDictEqual(
            self.output_handler.report_obj,
            {
                "compils":
                    [
                        {"matches": [{"name": "f1", "match": "test"}], "stage": "opt", "c_file": "in",
                         "obj_file": "out"},
                        {"matches": [{"name": "f1", "match": "test2"}], "stage": "opt", "c_file": ["in1", "in2"],
                         "obj_file": "output_files"},
                        {"matches": [{"name": "f1", "match": "test3"}], "stage": "opt", "c_file": "in",
                         "obj_file": ["out1", "out2"]},
                        {"matches": [{"name": "f1", "match": "test4"}], "stage": "opt", "c_file": ["in1", "in2"],
                         "obj_file": ["out1", "out2"]}
                    ],
                "config": self.output_handler.config.data,
                "summary": []
            }
        )

    def testMakeSummary(self):
        self.output_handler.config.data["filters"].extend(
            [
                {
                    "name": "f2",
                    "pattern": "Hello: (?P<name>[A-Za-z_][A-Za-z_0-9]*)",
                    "stages": ["opt"],
                    "type": "string",
                    "mode": "group",
                    "group": "name",
                    "summary": "count",
                },
                {
                    "name": "f3",
                    "pattern": "Number: (?P<num>\d+)",
                    "stages": ["opt"],
                    "type": "int",
                    "mode": "group",
                    "group": "num",
                    "summary": "mean",
                },
            ]
        )
        self.output_handler.config.parse_config()

        self.output_handler.handle_output("Hello: test1", Stage.Opt, "in1", "out1")
        self.output_handler.handle_output("Hello: test2", Stage.Opt, "in2", "out2")
        self.output_handler.handle_output("Hello: test3", Stage.Opt, "in3", "out3")
        self.output_handler.handle_output("Hello: test1", Stage.Opt, "in4", "out4")
        self.output_handler.handle_output("Number: 5", Stage.Opt, "inA", "outA")
        self.output_handler.handle_output("Number: 95", Stage.Opt, "inB", "outB")
        self.output_handler.handle_output("Number: 10", Stage.Opt, "inC", "outC")
        self.output_handler.handle_output("Number: 100", Stage.Opt, "inD", "outD")

        self.output_handler.make_summary(["out1", "out2", "out3", "out4"], "out")
        self.output_handler.make_summary(["outA", "outB", "outC", "outD"], "out")

        def compare(s, t):  # Non hashable and non sortable
            t = list(t)
            try:
                for elem in s:
                    t.remove(elem)
            except ValueError:
                return False
            return not t

        ref = [
                {
                    'executable': 'out',
                    'obj_files': ['out1', 'out2', 'out3', 'out4'],
                    'results':
                        [
                            {'name': 'f1', 'result': ['test1', 'test2', 'test3', 'test1']},
                            {'name': 'f2', 'result': {'test1': 2, 'test2': 1, 'test3': 1}},
                        ]
                },
                {
                    'executable': 'out',
                    'obj_files': ['outA', 'outB', 'outC', 'outD'],
                    'results': [{'result': 52.5, 'name': 'f3'}],
                },
            ]

        self.assertTrue(
            all(
                [
                    {
                        ref[i][k] == v if k != "results" else compare(ref[i][k], v)
                        for k, v in e.items()
                    }
                    for i, e in enumerate(self.output_handler.report_obj["summary"])
                ]))
