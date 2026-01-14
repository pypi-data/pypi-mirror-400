"""
This module contains dummy implementatons of tkApp (TesttkApp) and tkViewManager (TesttkViewManager)
and a TestWidget, to facilitate testing.
"""

# Standard
from tkinter import ttk

# Local
from tkAppFramework.tkApp import tkApp
from tkAppFramework.model import Model
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject


class TestWidget(ttk.LabelFrame, Subject):
    """
    Class represents a tkinter label frame widget, for testing tkViewManager.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent, text='Test Widget')
        Subject.__init__(self)


class TesttkViewManager(tkViewManager):
    """
    Class is a very simple child of tkViewManager, intended only to provide an implementations of _CreateWidgets(...)
    and handel_test_widget_update(), to facilitate unit testing.
    """
    def _CreateWidgets(self):
        """
        Concrete Implementation, does nothing, but does not raise NotImplementedError.
        :return None:
        """
        return None
    
    def handle_test_widget_update(self):
        """
        Handle updates from the test widget:
        :return None:
        """
        raise NotImplementedError
        return None


class TesttkApp(tkApp):
    """
    Class is a very simple child of tkApp, intended only to provide implementations of _createViewManager(...)
     and _createModel() factory methods, to facilitate unit testing.
    """
    def _createViewManager(self):
        """
        Concrete Implementation, which returns a TesttkViewManager instance.
        :return: tkViewManager instance that will be the app's view manager
        """
        return TesttkViewManager(self)

    def _createModel(self):
        """
        Concrete Implementation, which returns a Model instance.
        :return: Model instance that will be the app's model
        """
        return Model()


