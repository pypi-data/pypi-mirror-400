import unittest
from jpcli.parsers import lsmem_parser


class TestLsmemParser(unittest.TestCase):

    def test_parse(self):
        command_output = """\
RANGE                                 SIZE  STATE REMOVABLE  BLOCK
0x0000000000000000-0x000000007fffffff    2G online       no   0-15
0x0000000100000000-0x000000017fffffff    2G online       no  16-31
"""
        expected_output = [
            {"RANGE": "0x0000000000000000-0x000000007fffffff", "SIZE": "2G", "STATE": "online", "REMOVABLE": "no", "BLOCK": "0-15"},
            {"RANGE": "0x0000000100000000-0x000000017fffffff", "SIZE": "2G", "STATE": "online", "REMOVABLE": "no", "BLOCK": "16-31"},
        ]
        self.assertEqual(lsmem_parser.parse(command_output), expected_output)


if __name__ == '__main__':
    unittest.main()
