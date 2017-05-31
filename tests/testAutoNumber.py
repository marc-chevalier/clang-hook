from unittest import TestCase
from lib_hook.auto_number import AutoNumber, make_enum_to_str, make_str_to_enum


class E(AutoNumber):
    a = ()
    B = ()
    c = ()
    d = ()


class TestAutoNumber(TestCase):
    def testAutoNumber(self):
        self.assertEqual(len(E.__members__), 4)
        t = [("a", E.a, 1),
             ("B", E.B, 2),
             ("c", E.c, 3),
             ("d", E.d, 4)
             ]
        for (name, e, value) in t:
            self.assertEqual(E.__members__[name], e)
            self.assertEqual(E.__members__[name].value, value)


class TestMakeStrToEnum(TestCase):
    def setUp(self):
        self.str_to_e = make_str_to_enum(E)
        self.str_to_e_named = make_str_to_enum(E, name="str_to_e")
        self.str_to_e_sensitive = make_str_to_enum(E, case_sensitive=True)

    def testStrToEnum(self):
        self.assertEqual(self.str_to_e("a"), E.a)
        self.assertEqual(self.str_to_e("A"), E.a)
        self.assertEqual(self.str_to_e("b"), E.B)
        self.assertEqual(self.str_to_e("B"), E.B)
        self.assertEqual(self.str_to_e_sensitive("a"), E.a)
        self.assertRaises(KeyError, self.str_to_e_sensitive, "A")
        self.assertRaises(KeyError, self.str_to_e_named, "E")

    def testName(self):
        self.assertEqual(self.str_to_e.__name__, "str_to_enum")
        self.assertEqual(self.str_to_e_named.__name__, "str_to_e")


class TestMakeEnumToStr(TestCase):
    def setUp(self):
        self.e_to_str = make_enum_to_str(E)
        self.e_to_str_named = make_enum_to_str(E, name="e_to_str")
        self.e_to_str_sensitive = make_enum_to_str(E, case_sensitive=True)

    def testStrToEnum(self):
        self.assertEqual(self.e_to_str(E.a), "a")
        self.assertEqual(self.e_to_str(E.B), "b")
        self.assertEqual(self.e_to_str_sensitive(E.a), "a")
        self.assertEqual(self.e_to_str_sensitive(E.B), "B")

    def testName(self):
        self.assertEqual(self.e_to_str.__name__, "enum_to_str")
        self.assertEqual(self.e_to_str_named.__name__, "e_to_str")

