import unittest
from core.synchronizer import Synchronizer

class TestSynchronizer(unittest.TestCase):
    def test_sync_basic(self):
        s = Synchronizer()
        # Just ensure it doesn't crash on skeleton call
        s.sync("dummy_proj", {}, mode='patch')
