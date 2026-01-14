"""
This module provides unit tests for:
    (1) Subject and (2) Observer classes
"""


# Standard imports
import unittest

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer


class Test_Subject(unittest.TestCase):
    def test_attach_notify_detach(self):
        obs = Observer()
        sub = Subject()
        sub.attach(obs)
        self.assertTrue(sub._observers.index(obs)>=0)
        self.assertRaises(NotImplementedError, sub.notify)
        sub.detach(obs)
        self.assertRaises(ValueError, sub._observers.index, obs)

    def test_attach_nonobserver(self):
        obs = Subject()
        sub = Subject()
        self.assertRaises(AssertionError, sub.attach, obs)

    def test_detach_missing_observer(self):
        obs = Observer()
        sub = Subject()
        self.assertRaises(ValueError, sub.detach, obs)


class Test_Observer(unittest.TestCase):
    def test_update(self):
        obs = Observer()
        sub = Subject()
        self.assertRaises(NotImplementedError, obs.update, sub)


if __name__ == '__main__':
    unittest.main()
