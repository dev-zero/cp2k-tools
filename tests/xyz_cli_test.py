# vim: set fileencoding=utf8 :

import unittest

from click.testing import CliRunner

from cp2k_tools.parser.xyz_cli import xyz_restart_cleaner

from . import from_test_dir

class TestXYZCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_simple(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(xyz_restart_cleaner,
                                        [from_test_dir("xyz_parser_test-cp2k-output.xyz"), "foo.xyz"])

            output_msg = [
                "WARNING: found earlier restart point than previous one, can not drop already flushed frames",
                "found restart point @4, dropping 2 frames, flushing 0",
                "flushing remaining 2 frames",
                ]
            self.assertSequenceEqual(result.output.splitlines(), output_msg)
