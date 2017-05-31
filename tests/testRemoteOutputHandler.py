from unittest import TestCase
import socket
import pickle

from lib_hook import HookConfig, ClientOutputHandler, Stage, ServerOutputHandler
from lib_hook.logging import DummyLogger


class TestRemoteOutputHandler(TestCase):
    def setUp(self):
        self.config = HookConfig()
        self.config.data = {
                "log": False,
                "output_stages": ["opt"],
                "filters": [
                    {
                        "name": "f1",
                        "pattern": "(?<=Hello: )[A-Za-z_][A-Za-z_0-9]*",
                        "stages": ["opt"],
                        "type": "string",
                        "mode": "lookaround",
                        "summary": "append",
                    },
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
                ],
            }
        self.config.parse_config()

    def testClientOutputHandler(self):
        client, server = socket.socketpair()
        output_handler = ClientOutputHandler(self.config, DummyLogger(), client)
        output_handler.handle_output("Hello: test1", Stage.Opt, "in1", "out1")
        output_handler.handle_output("Hello: test2", Stage.Opt, "in2", "out2")
        output_handler.handle_output("Hello: test3", Stage.Opt, "in3", "out3")
        output_handler.handle_output("Hello: test1", Stage.Opt, "in4", "out4")
        output_handler.handle_output("Number: 5", Stage.Opt, "inA", "outA")
        output_handler.handle_output("Number: 95", Stage.Opt, "inB", "outB")
        output_handler.handle_output("Number: 10", Stage.Opt, "inC", "outC")
        output_handler.handle_output("Number: 100", Stage.Opt, "inD", "outD")

        t = [(166, 225, "in1", "out1", "Hello: test1", [{
                'name': 'f1',
                'match': 'test1'
                }, {
                'name': 'f2',
                'match': 'test1'
            }]),
             (166, 225, "in2", "out2", "Hello: test2", [{
                 'name': 'f1',
                 'match': 'test2'
             }, {
                 'name': 'f2',
                 'match': 'test2'
             }]),
             (166, 225, "in3", "out3", "Hello: test3", [{
                 'name': 'f1',
                 'match': 'test3'
             }, {
                 'name': 'f2',
                 'match': 'test3'
             }]),
             (166, 225, "in4", "out4", "Hello: test1", [{
                 'name': 'f1',
                 'match': 'test1'
             }, {
                 'name': 'f2',
                 'match': 'test1'
             }]),
             (163, 184, "inA", "outA", "Number: 5", [{
                 'name': 'f3',
                 'match': 5
             }]),
             (164, 184, "inB", "outB", "Number: 95", [{
                 'name': 'f3',
                 'match': 95
             }]),
             (164, 184, "inC", "outC", "Number: 10", [{
                 'name': 'f3',
                 'match': 10
             }]),
             (165, 184, "inD", "outD", "Number: 100", [{
                 'name': 'f3',
                 'match': 100
             }]),
             ]

        for size1, size2, input_file, output_file, stdout, match in t:
            size = int.from_bytes(server.recv(4), byteorder="big")
            self.assertEqual(size, size1)
            data = server.recv(size)
            request = pickle.loads(data)
            self.assertDictEqual(
                request,
                {
                    'args': {
                        'input_file': input_file,
                        'output_file': output_file,
                        'stage': 'opt',
                        'stdout': stdout,
                    },
                    'request_type': 'output',
                }
            )
            size = int.from_bytes(server.recv(4), byteorder="big")
            self.assertEqual(size, size2)
            data = server.recv(size)
            request = pickle.loads(data)
            self.assertDictEqual(
                request,
                {
                    'request_type': 'report',
                    'args': {
                        'matches': match,
                        'stage': 'opt',
                        'obj_file': output_file,
                        'c_file': input_file,
                    },
                }
            )

    def testServerOutputHandler(self):
        output_handler = ServerOutputHandler(self.config)
        output_handler.report_obj = \
            {
                'compils': [
                    {
                        'obj_file': 'out1',
                        'matches': [
                            {'name': 'f1', 'match': 'test1'},
                            {'name': 'f2', 'match': 'test1'}
                        ],
                        'c_file': 'in1',
                        'stage': 'opt'
                    }, {
                        'obj_file': 'out2',
                        'matches': [
                            {'name': 'f1', 'match': 'test2'},
                            {'name': 'f2', 'match': 'test2'}
                        ],
                        'c_file': 'in2',
                        'stage': 'opt'
                    }, {
                        'obj_file': 'out3',
                        'matches': [
                            {'name': 'f1', 'match': 'test3'},
                            {'name': 'f2', 'match': 'test3'}
                        ],
                        'c_file': 'in3',
                        'stage': 'opt'
                    }, {
                        'obj_file': 'out4',
                        'matches': [
                            {'name': 'f1', 'match': 'test1'},
                            {'name': 'f2', 'match': 'test1'}
                        ],
                        'c_file': 'in4',
                        'stage': 'opt'
                    }, {
                        'obj_file': 'outA',
                        'matches': [
                            {'name': 'f3', 'match': 5}
                        ],
                        'c_file': 'inA',
                        'stage': 'opt'
                    }, {
                        'obj_file': 'outB',
                        'matches': [
                            {'name': 'f3', 'match': 95}
                        ],
                        'c_file': 'inB',
                        'stage': 'opt'
                    }, {
                        'obj_file': 'outC',
                        'matches': [
                            {'name': 'f3', 'match': 10}
                        ],
                        'c_file': 'inC',
                        'stage': 'opt'
                    }, {
                        'obj_file': 'outD',
                        'matches': [
                            {'name': 'f3', 'match': 100}
                        ],
                        'c_file': 'inD',
                        'stage': 'opt'
                    }
                ],
                'config': self.config.data,
                'summary': []
            }
        output_handler.output_obj = {
                "compils":
                    [
                        {"input_file": "in", "stage": "opt", "output_file": "out", "stdout": "Hello: test"},
                        {"input_file": ["in1", "in2"], "stage": "opt", "output_file": "output_files",
                         "stdout": "Hello: test2"},
                        {"input_file": "in", "stage": "opt", "output_file": ["out1", "out2"], "stdout": "Hello: test3"},
                        {"input_file": ["in1", "in2"], "stage": "opt", "output_file": ["out1", "out2"],
                         "stdout": "Hello: test4"}
                    ],
                "config": output_handler.config.data
        }

        output_handler.handle_summary(["out1", "out2", "out3", "out4"], "out")
        output_handler.handle_summary(["outA", "outB", "outC", "outD"], "out")

        ref = \
            [
                {
                    'obj_files': ['out1', 'out2', 'out3', 'out4'],
                    'results': [
                        {'result': ['test1', 'test2', 'test3', 'test1'], 'name': 'f1'},
                        {'result': ['test1', 'test2', 'test3', 'test1'], 'name': 'f2'}
                    ],
                    'executable': 'out'
                }, {
                    'obj_files': ['outA', 'outB', 'outC', 'outD'],
                    'results': [
                        {'result': 52.5, 'name': 'f3'}
                    ],
                    'executable': 'out'}
            ]

        def compare(s, t):  # Non hashable and non sortable
            t = list(t)
            try:
                for elem in s:
                    t.remove(elem)
            except ValueError:
                return False
            return not t

        self.assertTrue(
            all(
                [
                    {
                        ref[i][k] == v if k != "results" else compare(ref[i][k], v)
                        for k, v in e.items()
                    }
                    for i, e in enumerate(output_handler.report_obj["summary"])
                ]))

