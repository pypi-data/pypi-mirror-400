"""
This module provides the SimlatorModel class, which represents the "business logic" of an application for interacting with
a simulator. It also maintains a queue of output events from the simulator, which can be observed by Views in the MVC pattern.
And, as a ttk.Frame, it can receive tkinter events.

Exported Classes:
    SimulatorModel -- This class represents (wraps) the simulator, and is a Model in the MVC pattern.

Exported Exceptions:
    None    
 
Exported Functions:
    None.
"""

# standard imports
from tkinter import ttk
from logging import LogRecord
from queue import Queue

# local imports
from tkAppFramework.model import Model


class SimulatorModel(Model, ttk.Frame):
    """
    This class represents the "business logic" for a tkSimulatorApp interacting with a simulator, and is a Model in the MVC pattern.
    It is also a ttk.Frame, so that it can receive tkinter events.
    
    This class monitors an internal Queue of output events from the simulator, which runs on a
    separate thread from the tkinter application. The internal queue will be the designated target of a logging.handler.QueueHandler,
    and the simulator will use logging to place output events into the internal queue. Any Observers of the model, such as a tkSimulatorViewManager
    can display these output events to the user, for example, through the tkSimulatorViewManager's SimulatorShowInfoWidget.
    """
    def __init__(self, parent, sim_adapt=None) -> None:
        """
        :parameter parent: The parent widget of this widget, the tkinter App, which hereafter will be
                           accessed as self.master.
        :parameter sim_adapt: The SimulatorAdapter subclass object that interfaces with the simulator, SimulatorAdapter object
        """
        ttk.Frame.__init__(self, parent)
        Model.__init__(self)
        self.sim_adapter = sim_adapt

        # Event queue (FIFO) for communicating with the thread running the simulator, intended for simulator output events
        # Queue size must be big enough that it can handle the amount of logging from the simulator that happens between queries. (Note: 10 was too small.)
        self._sim_event_queue = Queue(100)
        # A time in seconds to wait when attempting to access a queue with a put or get before timing out
        self._queue_access_timeout = 1
        parent.master.bind('<<SimulatorOutputEvent>>', self.SimulatorOutputEventHandler)

        # Placeholder that will store the most recent LogRecord retrieved from the simulator event queue
        self._log_record = None

    @property
    def sim_output_queue(self):
        return self._sim_event_queue

    def SimulatorOutputEventHandler(self, event=None):
        """
        Method which handles output events from simulator which the tkSimulatorApp expects the simulator's Observers to visualize.
        :parameter event: The tkinter event object associated with this event handler call. Default is None.
        :return None:
        """
        if not self._sim_event_queue.empty():
            # Retrieve a LogRecord from the simulator event queue
            info = self._sim_event_queue.get(timeout=self._queue_access_timeout)
            
            # Make sure we are retrieving what we think we are retrieving, that is, a LogRecord object
            assert(isinstance(info, LogRecord))

            # Put the message from the Log Record in the SimulatorShowInfoWidget
            self._log_record = info
            # Notify observers that new simulator output is available
            self.notify()
            # Clear out the placeholder
            self._log_record = None

        # Schedule the next execution of this handler
        # First argument to master is delay time (which is in microseconds)
        self.master.master.after(1, self.SimulatorOutputEventHandler)
        return None

    @property
    def log_record(self):
        return self._log_record
    
    @property
    def sim_adapter(self):
        return self._sim_adapter

    @sim_adapter.setter
    def sim_adapter(self, value):
        self._sim_adapter = value
        self.notify()

    def run(self):
        """
        Method called to run the simulator, using the simulator adapter.
        :return: None
        """
        self._sim_adapter.run()
        return None

    def load_and_run(self):
        """
        Method called to load a simulator state, and then run the simulator with that state, using the simulator adapter.
        :return: None
        """
        self._sim_adapter.load_and_run()
        return None


