import unittest
from core.parser import Parser

class TestParser(unittest.TestCase):
    def test_parse_structure(self):
        p = Parser()
        res = p.parse("dummy.txt")
        self.assertIn("project_type", res)
        self.assertIn("files", res)
