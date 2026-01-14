"""
The code in this modules illustrates how to create and launch a tkinter-based application using the tkAppFramework.
The demo application has one widgets with a button. The button text cycles between 'Start' and 'Stop' when the
button is clicked. The demo application's menubar has the standard File | Exit menu item.

This module also illustrates how to create and launch a tkinter-based simulator application, tkSimulatorApp and related
classes from tkAppFramework, using a simple DemoSimulator class that asks the user for floating point values,
squares them, and logs the results.

Exported Classes:
    DemoWidget -- A demo tkinter labelframe with a button that toggles between 'Start' and 'Stop' when clicked.
                  Also, a Subject for the DemotkViewManager to observe.
    DemotkViewManager -- Concrete implementation of tkViewManager that creates and manages a DemoWidget instace.
                         Also, an Observer of the DemoWidget.
    DemotkApp -- Concrete implementation of tkApp that creates a DemotkViewManager instance.
    DemoSimulator -- A simple simulator that asks the user for floating point values, squares them, and logs the results.
    DemoSimulatorAdapter -- Adapter to wrap DemoSimulator object for use in tkSimulatorApp.

Exported Exceptions:
    None
 
Exported Functions:
    __main__ -- Create and launch tkinter-based Demo Application or Simulator Application, at user's choice.
"""


# Standard
import tkinter as tk
from tkinter import ttk
import logging
import sysconfig

# Local
from tkAppFramework.tkSimulatorApp import tkSimulatorApp
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject
from tkAppFramework.model import Model
import tkAppFramework.tkApp
from tkAppFramework.sim_adapter import SimulatorAdapter
from UserResponseCollector.UserQueryCommand import askForFloat, UserQueryCommandMenu
import UserResponseCollector.UserQueryReceiver

class DemoModel(Model):
    """
    A concrete implementation of Model for the demo application.
    """
    def __init__(self) -> None:
        super().__init__()
        self._count = 0

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value
        self.notify()        


class DemoWidget(ttk.LabelFrame, Subject):
    """
    Class represents a tkinter label frame widget and is also a Subject in Observer design pattern.
    It has a button widget that will change it's text cyclicly from 'Start' to 'Stop' when clicked.
    """
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent, text='Demo Widget')
        Subject.__init__(self)
        
        btn = ttk.Button(self, command=self.OnButtonClicked)
        # Place button in grid and set weights for stretching the column and row in the grid
        # so that the demo widget resizes correctly.
        btn.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # Create string variable which will be the text displayed on the button
        self._lbl=tk.StringVar()
        self._lbl.set('Start')
        btn['textvariable']=self._lbl
        
        self._is_started = False

    def get_state(self):
        """
        Return whether the widget's state is started or stopped. Returns this as a bool which is True if started,
        and False if NOT started (that is, stopped).
        :return _is_Started: True if started, False if stopped, bool
        """
        return self._is_started
    
    def OnButtonClicked(self):
        """
        Event handler for button click.
        :return None:
        """
        # Flip the started state
        if self._is_started:
            # Widget state is currently started, so change state to stopped
            self._is_started = False
            # Change button text to 'Start'
            self._lbl.set('Start')
        else:
            # Widget state is currently stopped, so change it's state to started
            self._is_started = True
            # Change button text to 'Stop'
            self._lbl.set('Stop')

        # Notify observers
        self.notify()

        return None


class DemotkViewManager(tkViewManager):
    """
    Provide an implementation of _CreateWidgets(...). Implements handler functions for updates from the model
    and the demo widget.
    """
    def _CreateWidgets(self):
        """
        Create the demo widget, register 
        :return None:
        """
        dw = DemoWidget(self)
        # Attach self as an observer of the subject demo widget
        dw.attach(self)
        # Register a handler function for updates from the subject demo widget
        self.register_subject(dw,self.handle_demo_widget_update)
        # Place demo widget in grid and set weights for stretching the column and row in the grid
        # so that the demo widget resizes correctly.
        dw.grid(column=0, row=0, sticky='NWES')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        return None

    def handle_model_update(self):
        """
        Handle updates from the model.
        :return None:
        """
        print(f"Model count of button clicks is {self.getModel().count}")
        return None
    
    def handle_demo_widget_update(self):
        """
        Handle updates from the demo widget.
        :return None:
        """
        # Inform the model that the demo widget's state has changed (that is, the button was clicked),
        # so that the model can maintain a count of the button clicks / state changes.
        self.getModel().count += 1
        return None


class DemotkApp(tkAppFramework.tkApp.tkApp):
    """
    Provide implementations of _createViewManager() and _createModel() factory methods.
    """
    def __init__(self, parent):
        help_file_path = sysconfig.get_path('data') + '\\Help\\tkAppFramework\\HelpFile.txt'
        info = tkAppFramework.tkApp.AppAboutInfo(name='Demo Application', version='0.1', copyright='2025', author='John Q. Public',
                                                 license='MIT License', source='GitHub', help_file=help_file_path)
        super().__init__(parent, title="Demo Application", app_info=info, file_types=[('Text file', '*.txt')])

    def _createViewManager(self):
        """
        Concrete Implementation, which returns a DemotkViewManager instance.
        :return: tkViewManager instance that will be the app's view manager
        """
        return DemotkViewManager(self)

    def _createModel(self):
        """
        Concrete Implementation, which returns a DemoModel().
        :return: DemoModel instance that will be the app's model
        """
        return DemoModel()

class DemoSimulator:
    """
    This class is a very simple simulator. In a loop, until terminated, it asks the user for a floating point
    value, squares the value, and logs it.
    """
    def __init__(self, log_level=logging.INFO):
        """
        All that needs to be done is to set up logging.
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        """
        # Create a logger with name 'demo_simulator_logger'. This is NOT the root logger, which is one level up from here, and has no name.
        logger = logging.getLogger('demo_simulator_logger')
        # This is the threshold level for the logger itself, before it will pass to any handlers, which can have their own threshold.
        # Should be able to control here what the stream handler receives and thus what ends up going to stderr.
        # Use this key for now:
        #   DEBUG = debug messages sent to this logger will end up on stderr
        #   INFO = info messages sent to this logger will end up on stderr
        logger.setLevel(log_level)
        # Set up this highest level below root logger with a stream handler
        sh = logging.StreamHandler()
        # Set the threshold for the stream handler itself, which will come into play only after the logger threshold is met.
        sh.setLevel(log_level)
        # Add the stream handler to the logger
        logger.addHandler(sh)

    def go(self):
        """
        Execute a simulation.
        :return: None
        """
        logger = logging.getLogger('demo_simulator_logger')
        while True:
            try:
                response = askForFloat('Enter a value to square.')
            except UserResponseCollector.UserQueryReceiver.UserQueryReceiverTerminateQueryingThreadError:
                break
            squared = response * response
            logger.info(f"The square of {response} is {squared}.")
        return None

class DemoSimulatorAdapter(SimulatorAdapter):
    """
    Adapter to wrap DemoSimulator object.
    """
    def __init__(self, out_queue=None):
        """
        """
        super().__init__(DemoSimulator(), 'demo_simulator_logger', out_queue)

    def run(self):
        """
        Launch a simulation.
        :return: None
        """
        self.simulator.go()
        return None

    def load_and_run(self):
        """
        No loading functionality implemented for DemoSimulator, so just log a message and launch a simulation.
        :return: None
        """
        logger = logging.getLogger('demo_simulator_logger')
        logger.info(f"Loading functinality not implemented for DemoSimulator, so just lauching a simulation...")
        self.simulator.go()
        return None
    

if __name__ == '__main__':
    
    """
    Create and launch, at user's choice:
        (1) tkinter-based DemotkApp, or
        (2) tkinter-based tkSimulatorApp with DemoSimulator object
    """

    # Since the global UserQueryReceiver is a tkUserQueryReceiver, we have to construct a local one for the console
    receiver = UserResponseCollector.UserQueryReceiver.ConsoleUserQueryReceiver()
    command = UserQueryCommandMenu(receiver,
                                   'Which demo do you want to launch?', {'d':'Demo tkApp', 's':'Simulator app'})
    response = command.Execute()

    match response:
        case 'd':
    
            # DemotkApp

            # Create and configure the app
            root = tk.Tk()
            myapp = DemotkApp(root)

            # # Start the app's event loop running
            myapp.mainloop()

        case 's':

            # tkSimulatorApp

            root = tk.Tk()
            simapp = tkSimulatorApp(root)
            simapp.getModel().sim_adapter = DemoSimulatorAdapter(simapp.sim_output_queue)
            simapp.mainloop()



     