"""
This module provides unit tests for tkSimulatorApp class.
"""


# Standard
import unittest
import tkinter as tk
import sysconfig

# Local
from tkAppFramework.tkSimulatorApp import tkSimulatorApp
from tkAppFramework.tkSimulatorViewManager import tkSimulatorViewManager
from tkAppFramework.SimulatorModel import SimulatorModel
from tkAppFramework.tkApp import AppAboutInfo


class Test_tkSimulatorApp(unittest.TestCase):
    def test_init_exit(self):
        root = tk.Tk()
        simapp = tkSimulatorApp(root)
        self.assertEqual(root.title(), 'Simulator Application')
        self.assertIsInstance(simapp._view_manager, tkSimulatorViewManager)
        self.assertIsInstance(simapp.getModel(), SimulatorModel)
        help_file_path = sysconfig.get_path('data') + '\\Help\\tkAppFramework\\SimApp_HelpFile.txt'
        info = AppAboutInfo(name='Simulator Application', version='0.9.1', copyright='2025', author='Kevin R. Geurts',
                           license='MIT License', source='https://github.com/KevinRGeurts/tkAppFramework',
                           help_file=help_file_path)
        self.assertTupleEqual(simapp.getAboutInfo(), info)
        self.assertIsNone(simapp.onFileExit())


if __name__ == '__main__':
    unittest.main()
