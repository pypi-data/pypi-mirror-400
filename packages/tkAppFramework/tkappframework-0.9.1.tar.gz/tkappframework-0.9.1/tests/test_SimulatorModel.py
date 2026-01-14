"""
This module provides unit tests for the SimulatorModel class.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkAppFramework.SimulatorModel import SimulatorModel
from tkAppFramework.sim_adapter import SimulatorAdapter
from tkAppFramework.dummy_AppViewMgr import TesttkApp


class Test_SimulatorModel(unittest.TestCase):
    def test_init_set_get_adapter(self):
        root = tk.Tk()
        app = TesttkApp(root)
        # Test __init__ and @property getter
        adapt1 = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(app, adapt1)
        self.assertEqual(id(mod.sim_adapter), id(adapt1))
        # Test @property setter
        adapt2 = SimulatorAdapter(logger_name='test_simulator_model_logger2')
        mod.sim_adapter = adapt2
        self.assertEqual(id(mod.sim_adapter), id(adapt2))

    def test_run(self):
        root = tk.Tk()
        app = TesttkApp(root)
        adapt = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(app, adapt)
        self.assertRaises(NotImplementedError, mod.run)

    def test_load_and_run(self):
        root = tk.Tk()
        app = TesttkApp(root)
        adapt = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(app, adapt)
        self.assertRaises(NotImplementedError, mod.load_and_run)


if __name__ == '__main__':
    unittest.main()
