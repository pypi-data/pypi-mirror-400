"""
This module defines the tkHelpViewManager class. It is a concrete implementation of tkViewManager.
It acts as a Mediator and an Observer, and handles the interactions between the help viewer application's widgets.

Exported Classes:
    tkHelplViewManager -- Concrete implementation of tkViewManager.
                          Acts as a Mediator and an Observer, and handles the interactions between
                          the help viewer application's widgets.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk

# Local imports
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject


class tkHelpViewManager(tkViewManager):
    """
    Concrete implementation of tkViewManager. Acts as Observer, and handles the interactions between help viewer application's widgets.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, most probably a Toplevel window
        """
        tkViewManager.__init__(self, parent)
        
    def _CreateWidgets(self):
        """
        Concrete implementation of tkViewManager._CreateWidgets.
        Sets up and registers the child widgets of the tkHelpViewManager widget.
        :return None:
        """

        self._helptxt_widget = HelpTextWidget(self, help_file=self.getModel().help_file)
        self.register_subject(self._helptxt_widget, self.handle_helptxt_widget_update)
        self._helptxt_widget.attach(self)
        self._helptxt_widget.grid(column=0, row=0, sticky='NWES') # Grid-2
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        return None

    def handle_helptxt_widget_update(self):
        """
        Handle updates from help text widget.
        :return None:
        """
        # Do something
        return None

    def handle_model_update(self):
        """
        Handler function called when the model notifies the view manager of a change in state.
        :return None:
        """
        self._helptxt_widget._readHelpFileContent(self.getModel().help_file)
        return None


# TODO: Assess whether or not this widget needs to keep as a member the path to the help content file,
# since this can be obtained from the HelpModel through the tkHelpViewManager and tkHelpApp.
class HelpTextWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which allow viewing of help topic content.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent, help_file='') -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        :parameter help_file: Path to the help file to be opened and displayed initially, string
        """
        ttk.Labelframe.__init__(self, parent, text="Help Topic Content")
        Subject.__init__(self)
        self._help_file=help_file

        self._txt_content = tk.Text(self)
        self._txt_content.grid(column=0, row=0, sticky='NWSE') # Grid-2
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        # Create a vertical Scrollbar and associate it with _txt_content
        self._scrollbar_vert = ttk.Scrollbar(self, command=self._txt_content.yview)
        self._scrollbar_vert.grid(column=1, row=0, sticky='NWSE')
        self._txt_content['yscrollcommand'] = self._scrollbar_vert.set

        # Create a horizontal Scrollbar and associate it with _txt_content
        self._scrollbar_hor = ttk.Scrollbar(self, command=self._txt_content.xview, orient='horizontal')
        self._scrollbar_hor.grid(column=0, row=1, sticky='NWSE')
        self._txt_content['xscrollcommand'] = self._scrollbar_hor.set

        # Read in help file content
        self._readHelpFileContent(help_file)
    
    def _readHelpFileContent(self, help_file=''):
        """
        Utility function that reads in the help file content and inserts it into the Text widget.
        :parameter help_file: Path to the help file from which to read content, string
        :return: None
        """
        if len(help_file)>0:
            with open(help_file, 'r') as f:
                self._txt_content.insert(tk.INSERT, f.read())
            self._txt_content.config(state='disabled')
        return None

