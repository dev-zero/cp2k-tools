# vim: set fileencoding=utf8 :

import unittest

from cp2k_tools.parser.xyz import XYZParser

from . import from_test_dir

class TestXYZParser(unittest.TestCase):
    def test_parsing_multiframe(self):
        with open(from_test_dir('xyz_parser_test-simple_multiframe_file.xyz'), 'r') as fhandle:
            parsed = XYZParser.parse(fhandle.read())

            self.assertEqual(len(parsed), 3)
            # check the number of atoms in each frame
            self.assertSequenceEqual([e['natoms'] for e in parsed], [5]*3)
            # check the (order of) the symbols in each frame
            self.assertSequenceEqual([[a[0] for a in e['atoms']] for e in parsed], [['C', 'H', 'H', 'H', 'H']]*3)
            # check the position of the first element in each frame
            self.assertSequenceEqual([e['atoms'][0] for e in parsed], [('C', (5., 5., 5.), )]*3)

    def test_unicode(self):
        with open(from_test_dir('xyz_parser_test-unicode.xyz'), 'r') as fhandle:
            parsed = XYZParser.parse(fhandle)

            self.assertEqual(parsed[0]['comment'], u'Ω≈ç√∫˜µ≤≥÷')

    def test_arg_handling(self):
        with open(from_test_dir('xyz_parser_test-simple_multiframe_file.xyz'), 'r') as fhandle:
            parsed = XYZParser.parse(fhandle.read())
            self.assertTrue(parsed)

        with open(from_test_dir('xyz_parser_test-simple_multiframe_file.xyz'), 'r') as fhandle:
            parsed = XYZParser.parse(fhandle)
            self.assertTrue(parsed)

        with open(from_test_dir('xyz_parser_test-simple_multiframe_file.xyz'), 'rb') as fhandle:
            parsed = XYZParser.parse(fhandle)
            self.assertTrue(parsed)
