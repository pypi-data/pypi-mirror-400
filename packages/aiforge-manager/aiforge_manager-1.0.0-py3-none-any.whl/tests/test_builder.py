import unittest
import os
import shutil
from core.builder import Builder

class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_output_project"

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_build_creates_dir(self):
        b = Builder()
        b.build({}, self.test_dir, mode='clean')
        self.assertTrue(os.path.exists(self.test_dir))
