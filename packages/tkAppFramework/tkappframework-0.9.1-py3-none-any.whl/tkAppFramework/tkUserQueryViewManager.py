"""
Defines the tkUserQueryViewManager class, and its child widgets. tkUserQueryViewManager IS-A tkViewManager which will
allow the user to respond to tkUserQueryReceiver queries. It will be necessary for a consumer of an object of this class
to place it within an application's main window, for example.

Exported Classes:
    tkUserQueryViewManager -- A tkViewManager implementation that mediates child widgets which allow the user to respond to tkUserQueryReceiver queries.
    QueryPromptWidget -- A tkinter label frame widget that displays a query prompt for the user.
    QueryResponseEntryWidget -- A tkinter label frame widget that lets the user type in a response to a query.
    QueryResponseSendWidget -- A tkinter label frame widget that lets the user send a response to a query.
    QueryResponseToolsWidget -- A tkinter label frame widget that lets the user launch a tool to assist with response to a query.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from queue import Queue

# Local imports
# -- Leave these next two imports EXACTLY how they are, so that tkUserQueryReceiver correctly changes values of globals in UserQueryReceiver --
import UserResponseCollector.UserQueryReceiver
import tkAppFramework.tkUserQueryReceiver
# -- End Leave --
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject

# TODO: Before, when UserQueryWidget was a tkinter.ttk.LabelFrame, it had text label 'Query' to show to the user. Now,
# as a tkViewManager, it is a tkinter.ttk.Frame. Do we need to find a way to have a Query text label to help the
# user understand the purpose of the child widgets?

class tkUserQueryViewManager(tkViewManager):
    """
    Class is a tkViewManager which will mediate child widgets which will allow the user to respond to tkUserQueryReceiver queries.
    It will be necessary for a consumer of an object of this class to place it within an application's main window, for example.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget, expected to be a tkApp object
        """
        super().__init__(parent)

        # Query queue (FIFO) for communicating QueryInfo objects with the tkUserQueryReceiver object
        self._query_info_queue = Queue(10)
        # A time in seconds to wait when attempting to access a queue with a put or get before timing out
        self._queue_access_timeout = 1
        
        # Set to the QueryInfo object pulled out of the query queue
        self._current_query_info = None

        # Set up tkUserQueryReceiver so it has the correct callbacks
        tkAppFramework.tkUserQueryReceiver.tkUserQueryReceiver_setup(query_event_callback=self.event_generate, query_queue_callback=self.put_query_info_in_queue)

        self.bind('<<TkinterAppQueryEvent>>', self.TkAppQueryEventHandler)

    def handle_model_update(self):
        """
        Handler function called when the model notifies the tkUserQueryViewManager of a change in state.
        Do nothing, but if not implemented, tkViewManager.handle_model_update() will raise NotImplementedError.
        :return None:
        """
        return None

    def _CreateWidgets(self):
        """
        Utility function to be called by super.__init__ to set up the child widgets of the query view manager.
        :return None:
        """
        # QueryPromptWidget for showing the query prompt text, that is, the text descibing what query the user is responding too
        self._query_prompt_widget = QueryPromptWidget(self)
        self.register_subject(self._query_prompt_widget, self.handle_query_prompt_widget_update)
        self._query_prompt_widget.attach(self)
        self._query_prompt_widget.grid(column=0, row=0, sticky='NWSE') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx

        # QueryResponseEntryWidget, that is, the widget where the user types in their response to the query
        self._query_response_entry_widget = QueryResponseEntryWidget(self)
        self.register_subject(self._query_response_entry_widget, self.handle_query_response_entry_widget_update)
        self._query_response_entry_widget.attach(self)
        self._query_response_entry_widget.grid(column=1, row=0, sticky='NWSE') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(1, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx

        # Widget for sending query response
        self._query_response_send_widget = QueryResponseSendWidget(self)
        self.register_subject(self._query_response_send_widget, self.handle_query_response_send_widget_update)
        self._query_response_send_widget.attach(self)
        self._query_response_send_widget.grid(column=2, row=0) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(2, weight=0) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=0) # Grid-2 in Documentation\UI_WireFrame.pptx
        
        # QueryResponseToolsWidget - For launching "tools" that help the user fill in the QueryResponseEntryWidget under different circumstances.
        self._query_response_tools_widget = QueryResponseToolsWidget(self)
        self.register_subject(self._query_response_tools_widget, self.handle_query_response_tools_widget_update)
        self._query_response_tools_widget.attach(self)
        self._query_response_tools_widget.grid(column=3, row=0) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(3, weight=0) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=0) # Grid-2 in Documentation\UI_WireFrame.pptx
        
        self.reset_widgets()

        return None

    def handle_query_prompt_widget_update(self):
        """
        Handler function called when the QueryPromptWidget object notifies the tkUserQueryViewManager of a change in state.
        Currently does nothing.
        :return None:
        """
        # Do nothing
        # TODO: Determine if this should do something.
        return None

    def handle_query_response_entry_widget_update(self):
        """
        Handler function called when the QueryResponseEntryWidget object notifies the tkUserQueryViewManager of a change in state.
        Currently does nothing.
        :return None:
        """
        # Do nothing
        # TODO: Determine if this should do something.
        return None

    def handle_query_response_send_widget_update(self):
        """
        Handler function called when the QueryResponseSendWidget object notifies the tkUserQueryViewManager of a change in state.
        :return None:
        """
        # Get line of text from response QueryResponeEntryWidget
        response = self._query_response_entry_widget.get_state()
        if len(response)>0:
            # Create QueryResponse object
            query_response=tkAppFramework.tkUserQueryReceiver.QueryResponse(query_response=response, query_ID=self._current_query_info.query_ID)
            # Place QueryResponse object in tkUserResponseCollector's response queue
            UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver().put_response_in_queue(query_response)

            self.reset_widgets()

        return None

    def handle_query_response_tools_widget_update(self):
        """
        Handler function called when the QueryResponseToolsWidget object notifies the tkUserQueryViewManager of a change in state.
        :return None:
        """
        # Get the tool response text from the QueryResponseToolsWidget
        response = self._query_response_tools_widget.get_state()
        # Push the tool response text into the QueryResponseEntryWidget
        self._query_response_entry_widget.set_state(response)
        return None

    def put_query_info_in_queue(self, query_info):
        """
        Called (through a callback) by tkUserQueryReceiver, to put a QueryInfo object in the query view manager's query queue.
        :return: None
        """
        item = self._query_info_queue.put(query_info, timeout=self._queue_access_timeout)
        return None

    def TkAppQueryEventHandler(self, event):
        """
        Called to handle a <<TkinterAppQueryEvent>> virtual event generated by tkUserQueryReceiver.
        :parameter event: The tkinter event object
        :return: None
        """
        self.handle_query_event()
        return None

    def handle_query_event(self):
        """
        Utility function that handle's a query event.
        :return: None
        """
        # Retrieve an item from the simulator event queue to determine what type of information we need from the user
        item = self._query_info_queue.get(timeout=self._queue_access_timeout)
        # Store the QueryInfo that we just retrieved, so that we can access it's ID when we respond
        self._current_query_info = item
        # Send the prompt text to the QueryPromptWidget
        self._query_prompt_widget.set_state(item.prompt_text)
        # Activate the QueryResponseSendWidget
        self._query_response_send_widget.disable_query_response_send(False)
        # Activate the QueryResponseToolsWidget
        self._query_response_tools_widget.disable_query_response_tools(False)
        # Activate the QueryResponseEntryWidget, and request that it be given focus (if the app has focus)
        self._query_response_entry_widget.disable_query_response_entry(False)
        self._query_response_entry_widget.focus_set()

        return None

    def reset_widgets(self):
        """
        Reset all child widgets to a state appropriate for no query yet received, or waiting for the next query to be received.
        :return: None
        """
        self._query_prompt_widget.set_state('--')
        self._query_response_entry_widget.set_state('')
        self._query_response_entry_widget.disable_query_response_entry(True)
        self._query_response_send_widget.disable_query_response_send(True)
        self._query_response_tools_widget.disable_query_response_tools(True)
        return None


class QueryPromptWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which display a query prompt for the user.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        """
        ttk.Labelframe.__init__(self, parent, text='Query Prompt')
        Subject.__init__(self)

        # Message widget for showing the query prompt text, that is, the text descibing what query the user is responding too
        self._msg_query = tk.Message(self, relief=tk.RIDGE, aspect=1000, takefocus=0)
        self._msg_query.grid(column=0, row=0, sticky='NWSE') # Grid-3 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        # Control variable for Message widget
        self._msg_query_txt = tk.StringVar()
        # Tell the Message widget to watch this variable.
        self._msg_query["textvariable"] = self._msg_query_txt

    def set_state(self, value=''):
        """
        Set the query prompt text of the QueryPromptWidget.
        :parameter value: The query prompt text to display to the user, string
        :return: None
        """
        assert(type(value)==str)
        self._msg_query_txt.set(value)
        self.notify()
        return None


class QueryResponseEntryWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which let the user type in a response to a query.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        """
        ttk.Labelframe.__init__(self, parent, text='Query Response')
        Subject.__init__(self)

        # Query response Entry widget, that is, the entry widget where the user types in their response to the query
        self._ent_response = ttk.Entry(self, width=50, takefocus=1)
        self._ent_response.grid(column=1, row=0, sticky='NWSE') # Grid-3 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(1, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        # Control variable for the Entry widget
        self._ent_response_txt = tk.StringVar()
        # Tell the Entry widget to match this variable.
        self._ent_response["textvariable"] = self._ent_response_txt
        # Set up a horizontal scroll bar
        self._ent_scroll_hor = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.onScrollHorizontal)
        self._ent_scroll_hor.grid(column=1, row=1, sticky='NWSE') # Grid-3 in Documentation\UI_WireFrame.pptx
        self._ent_response['xscrollcommand'] = self._ent_scroll_hor.set

    # See: https://tkdocs.com/shipman/entry-scrolling.html
    def onScrollHorizontal(self, *L):
        """
        Handle horizontal scrolling of query response entry widget.
        :parameter L: List of arguments from the scrollbar command
        """
        op, howMany = L[0], L[1]
        if op == 'scroll':
            units = L[2]
            self._ent_response.xview_scroll(howMany, units)
        elif op == 'moveto':
            self._ent_response.xview_moveto(howMany)

    def get_state(self):
        """
        Get the query response text from the QueryResponseEntryWidget.
        :return: Query response text, string
        """
        return self._ent_response_txt.get()

    def set_state(self, value=''):
        """
        Set the query response text of the QueryResponseEntryWidget.
        :paramter value: Query response text, string
        :return: None
        """
        assert(type(value)==str)
        self._ent_response_txt.set(value)
        self.notify()
        return None

    def disable_query_response_entry(self, disabled=True):
        """
        Used to set if the widget will accept a query respone entry or not.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._ent_response.state(['disabled'])
        else:
            self._ent_response.state(['!disabled'])
        return None


class QueryResponseSendWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which let the user send a response to a query.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        """
        ttk.Labelframe.__init__(self, parent, text='Send Query Response')
        Subject.__init__(self)

        # Enter button
        self._btn_enter = ttk.Button(self, text='Enter', command=self.OnEnterButton, takefocus=1)
        self._btn_enter.grid(column=2, row=0) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(2, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx

    def OnEnterButton(self):
        """
        Called when Enter button is clicked.
        :return: None
        """
        self.notify()
        return None

    def disable_query_response_send(self, disabled=True):
        """
        Used to set if the widget can send a query respone entry or not.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._btn_enter.state(['disabled'])
        else:
            self._btn_enter.state(['!disabled'])
        return None


class QueryResponseToolsWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which let the user launch a tool to
    assist with response to a query.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        """
        ttk.Labelframe.__init__(self, parent, text='Query Response Tools')
        Subject.__init__(self)

        self._tool_response_txt = ''

        # Tools menu button - The menu choices here select "tools" that help the user fill in the QueryResponseEntryWidget text
        # under different circumstances. Example, if the user is asked for a file path to save to, they can use the tools menu button
        # to launch a file save dialog.
        self._mbtn_tools = ttk.Menubutton(self, text='Tools', takefocus=1)
        self._mbtn_tools.grid(column=3, row=3) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(3, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        # Tools menu button menu
        self._menu_tools = tk.Menu(self._mbtn_tools)
        self._mbtn_tools['menu'] = self._menu_tools
        self._menu_tools.add_command(label='File Save Path...', command=self.OnFileSavePath)
        self._menu_tools.add_command(label='File Open Path...', command=self.OnFileOpenPath)

    def get_state(self):
        """
        Get the tool response text from the QueryResponseToolsWidget.
        :return: Tool response text, string
        """
        return self._tool_response_txt

    def OnFileSavePath(self):
        """
        Help respond to a file save path query by using the tkFileDialog for save to get the path.
        :return: None
        """
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(title='File Save Path')
        self._tool_response_txt = response
        self.notify()
        return None
    
    def OnFileOpenPath(self):
        """
        Help respond to a file open path query by using the tkFileDialog for open to get the path.
        :return: None
        """
        # Pop up tkFileDialog for open
        response = filedialog.askopenfilename(title='File Open Path')
        self._tool_response_txt = response
        self.notify()
        return None

    def disable_query_response_tools(self, disabled=True):
        """
        Used to set if the widget can launch respone tools or not.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._mbtn_tools.state(['disabled'])
        else:
            self._mbtn_tools.state(['!disabled'])
        return None
