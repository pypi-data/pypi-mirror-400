"""
This module provides unit tests for tkApp class.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkAppFramework.dummy_AppViewMgr import TesttkApp, TesttkViewManager
from tkAppFramework.model import Model
from tkAppFramework.tkApp import AppAboutInfo


class Test_tkApp(unittest.TestCase):
    def test_init_exit(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        self.assertEqual(root.title(), 'Test App')
        self.assertIsInstance(app._view_manager, TesttkViewManager)
        self.assertIsInstance(app.getModel(), Model)
        self.assertIs(app.getModel(), app._model)
        self.assertIsNone(app.onFileExit())

    def test_getAppInfo(self):
        root = tk.Tk()
        info = AppAboutInfo(name='Test App', version='1.0', copyright='2025', author='Tester', license='MIT', source='local repo')
        app = TesttkApp(root, title='Test App', app_info=info)
        self.assertTupleEqual(app.getAboutInfo(), info)


if __name__ == '__main__':
    unittest.main()
