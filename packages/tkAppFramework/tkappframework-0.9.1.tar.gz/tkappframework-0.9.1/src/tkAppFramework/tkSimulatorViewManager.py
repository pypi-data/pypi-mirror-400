"""
Defines tkSimulatorViewManager class, which is a concrete implementation of tkViewManager for simulator applications.

tkSimulatorViewManager, as an Observer of the SimulatorModel, repsonds to updates from the Model by retrieving simulator output events, and
displays these output events to the user through it's SimulatorShowInfoWidget.

Exported Classes:
    tkSimulatorViewManager -- Is-A tkViewManager implementation for simulator applications.

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    None
"""


# Standard imports
from logging import LogRecord
import tkinter as tk
from tkinter import ttk

# Local imports
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject

class tkSimulatorViewManager(tkViewManager):
    """
    tkSimulatorViewManager IS-A tkViewManager. This class is an Observer of the SimulatorModel, and thus it will be
    notified of updates to the Model, including when new simulator output events are available from the simulator.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, The tkinter App
        """
        super().__init__(parent)

    def reset_widgets_for_new_simulation(self):
        """
        Utility function called to put child widgets in appropriate state ahead of a new simulation.
        :return: None
        """
        return None

    def _CreateWidgets(self):
        """
        Utility function to be called by tkViewManager.__init__ to set up the child widgets of the tkSimulatorViewManager widget.
        This method could be extended by a child class, in the event that the child class wanted to add additional widgets for
        displaying simulator output.
        :return None:
        """
        self._info_widget = SimulatorShowInfoWidget(self)
        self.register_subject(self._info_widget, self.handle_info_widget_update)
        self._info_widget.attach(self)
        self._info_widget.grid(column=0, row=0, sticky='NWES') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        return None

    def handle_model_update(self):
        """
        Handler function called when the SimulatorModel object notifies the tkSimulatorViewManager of a change in state.
        Retrieve simulator output log record from SimulatorModel and display in SimulatorShowInfoWidget.
        :return None:
        """
        # Retrieve a LogRecord from the simulator event queue
        info = self.getModel().log_record
        if info is not None:
            # Make sure we are retrieving what we think we are retrieving, that is, a LogRecord object
            assert(isinstance(info, LogRecord))
            # Put the message from the Log Record in the SimulatorShowInfoWidget
            self._info_widget.insert_end(info.message)
        return None

    def handle_info_widget_update(self):
        """
        Handler function called when the SimulatorShowInfoWidget object notifies the tkSimulatorViewManager of a change in state.
        Currently does nothing.
        :return None:
        """
        # Do nothing
        # TODO: Determine if this should do something.
        return None


class SimulatorShowInfoWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which will display simulator output to the user
    during a simulation.
    :parameter parent: The parent widget of this widget, The tkSimulatorViewManager
    """
    def __init__(self, parent) -> None:
        super().__init__(parent, text='Simulation Output', takefocus=0)
        Subject.__init__(self)
        
       # Create a text widget which will display all the logging.info messages received from the simulator
       
        self._txt_info =  tk.Text(self, width=40, height=10)
        self._txt_info.grid(column=0, row=0, sticky='NWSE') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        # Set wrap to NONE, so that there are no line breaks
        self._txt_info['wrap']=tk.NONE

        # Create a vertical Scrollbar and associate it with _txt_info
        self._scrollbar_vert = ttk.Scrollbar(self, command=self._txt_info.yview)
        self._scrollbar_vert.grid(column=1, row=0, rowspan=2, sticky='NWSE')
        self._txt_info['yscrollcommand'] = self._scrollbar_vert.set

        # Create a horizontal Scrollbar and associate it with _txt_info
        self._scrollbar_horz = ttk.Scrollbar(self, command=self._txt_info.xview, orient=tk.HORIZONTAL)
        self._scrollbar_horz.grid(column=0, row=1, columnspan=2, sticky='NWSE')
        self._txt_info['xscrollcommand'] = self._scrollbar_horz.set

        # Set state to DISABLED so the user can't add or change content
        self._txt_info['state']=tk.DISABLED

    def insert_end(self, message=''):
        """
        Utility function to insert a message at the end of the Text widget.
        :parameter message: The message (text) to insert at the end of the Text widget. Default is empty string.
        :return: None
        """
        # Set state to NORMAL so we can insert text
        self._txt_info['state']=tk.NORMAL
        self._txt_info.insert('end', f"{message}\n")
        # Force cursor to last line of text widget, so that the text widget "scrolls to the last line"
        self._txt_info.yview_moveto(1.0)
        # Set state to DISABLED so the user can't add or change content
        self._txt_info['state']=tk.DISABLED
        # Let observers know that state has changed
        self.notify()
        return None
