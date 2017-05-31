from unittest import TestCase
from lib_hook.filter import Filter
from lib_hook.stage import Stage


class TestFilter(TestCase):
    def testFilter(self):
        data1 = \
            {
                "name": "test",
                "pattern": "(?<=Hello: )[A-Za-z_][A-Za-z_0-9]*",
                "stages": ["opt"],
                "type": "string",
                "mode": "lookaround",
                "summary": "append",
            }
        data2 = \
            {
                "name": "test",
                "pattern": "Hello: (?P<bla>[0-9]+)",
                "stages": ["opt"],
                "type": "int",
                "mode": "group",
                "group": "bla",
                "summary": "append",
            }
        f1 = Filter(data1)
        f2 = Filter(data2)
        t = [(f1, "Hello: bla", "bla"),
             (f1, "Hello: bla truc", "bla"),
             (f1, "Hello: 123", None),
             (f2, "Hello: bla", None),
             (f2, "Hello: 123", 123),
             (f2, "Hello: 123 456", 123),
             ]

        for (f, text, response) in t:
            match = f.search(text, Stage.Opt)
            self.assertEqual(match, response)
