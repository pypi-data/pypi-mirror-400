"""
This module provides unit tests for tkViewManager.
"""

# Standard
import unittest
import tkinter as tk
from tkinter import ttk

# Local
from tkAppFramework.dummy_AppViewMgr import TestWidget, TesttkApp


class Test_tkViewManager(unittest.TestCase):
    def test_getModel(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        vm = app._view_manager
        model = vm.getModel()
        self.assertIsInstance(model, type(app._model))
        self.assertIs(model, app._model)

    def test_register_subject(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        vm = app._view_manager
        cw = TestWidget(vm)
        vm.register_subject(cw,vm.handle_test_widget_update)
        self.assertTrue(vm._subjects.__contains__(cw))

    def test_detach(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        vm = app._view_manager
        cw = TestWidget(vm)
        cw.attach(vm)
        self.assertTrue(len(cw._observers)==1)
        vm.register_subject(cw,vm.handle_test_widget_update)
        vm._detach_from_subjects()
        self.assertTrue(len(cw._observers)==0)

    def test_update(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        vm = app._view_manager
        cw = TestWidget(vm)
        cw.attach(vm)
        vm.register_subject(cw,vm.handle_test_widget_update)
        self.assertRaises(NotImplementedError, vm.update, cw)

    def test_handle_model_update(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        vm = app._view_manager
        self.assertRaises(NotImplementedError, vm.handle_model_update)


if __name__ == '__main__':
    unittest.main()