import unittest

from parsimonious import IncompleteParseError

from cp2k_tools.parser.input import CP2KInput2Dict

from . import from_test_dir

class TestInputParser(unittest.TestCase):
    def setUp(self):
        self.parser = CP2KInput2Dict()

    def test_minimal(self):
        inp = "&GLOBAL\n&END\n"
        struct = self.parser.parse(inp)
        self.assertEqual(struct, {'global': {}})

    def test_full(self):
        with open(from_test_dir("input_parser_test_Si.inp"), "r") as fhandle:
            struct = self.parser.parse(fhandle.read())
            self.assertTrue(struct)

    def test_no_final_newline(self):
        inp = "&GLOBAL\n&END"
        struct = self.parser.parse(inp)
        self.assertEqual(struct, {'global': {}})

    def test_non_unix_newlines(self):
        struct = self.parser.parse("&GLOBAL\r\n&END\r\n")
        self.assertEqual(struct, {'global': {}})

        struct = self.parser.parse("&GLOBAL\r&END\r")
        self.assertEqual(struct, {'global': {}})

        struct = self.parser.parse("&GLOBAL\r\n&END\n")
        self.assertEqual(struct, {'global': {}})

    def test_invalids(self):
        with self.assertRaises(IncompleteParseError):
            self.parser.parse("&GLOBAL\n&ENDFOO\n")
