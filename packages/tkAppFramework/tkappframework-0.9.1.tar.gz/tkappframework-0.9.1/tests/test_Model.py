"""
This module provides unit tests for Model class.
"""


# Standard
import unittest

# Local
from tkAppFramework.model import Model


class Test_Model(unittest.TestCase):
    def test_init(self):
        mod = Model()
        exp_val = 0
        act_val = len(mod._observers)
        self.assertEqual(exp_val, act_val)

    def test_readModelFromFile_not_implemented(self):
        mod = Model()
        self.assertRaises(NotImplementedError, mod.readModelFromFile, None, None)

    def test_writeModelToFile_not_implemented(self):
        mod = Model()
        self.assertRaises(NotImplementedError, mod.writeModelToFile, None, None)


if __name__ == '__main__':
    unittest.main()
