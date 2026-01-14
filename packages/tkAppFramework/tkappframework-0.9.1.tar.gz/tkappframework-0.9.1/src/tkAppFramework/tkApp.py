"""
Defines the abstract base class tkApp, from which concrete tkinter applications can be derived.

Concrete implementation child classes must:
    (1) Implement the factory method _createViewManager() to create and return a tkViewManager instance,
        which will create and manage the widgets of the application.
    (2) Implement _createModel() factory method to create and return a Model instance, which 
        holds the data and business logic of the application.
Concrete implementation child classes likely will:
    (3) Pass AboutAppInfo named tuple into super.__init__() to set up the app's About dialog.
    (4) Pass menu_dict into super.__init__() to set up the app's menubar.
    (5) Pass file_types into super.__init__() to set up the file types for file dialogs.
    (6) Define and implement handler functions for menubar selections, beyond OnFileOpen, OnFileSave,
        OnFileSaveAs, OnFileExit, OnViewHelp, and OnHelpAbout.
Concrete implementation child classes may:
    (7) Extend _setup_child_widgets() if the tkViewManager does not create all of the app's widgets
    (8) Extend logging setup in _setup_logging(...) if application specific logging is desired.

Exported Classes:
    tkApp -- Interface (abstract base) class for tkinter applications. tkApp is a ttk.Frame.

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    A logger named 'tkApp_logger' is created and configured in _setup_logging(...), which is called by __init__(...).
    It logs to stderr through a stream handler. Default logging level is logging.INFO, but can be set by passing
    log_level into __init__(...). The 'tkApp_logger' logger can be used by concrete implementation child classes of tkApp.
"""


# standard imports
from collections import namedtuple
import os
import logging
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter import filedialog
from multiprocessing import Process

# local imports
from tkAppFramework.tkHelpViewManager import tkHelpViewManager
from tkAppFramework.HelpModel import HelpModel


# This function cannot be a method of tkApp, do to Process using pickle.
def _launch_help_app(help_file = ''):
    """
    Launch tkinter app for displaying online help.
    :parameter help_file: Path to the help file to be opened and displayed initially, string
    :return: None
    """
    # Create and configure the app
    root = tk.Tk()
    myapp = tkHelpApp(root, help_file)

    # Start the app's event loop running
    myapp.mainloop()
    return None


# Named tuple to hold the "About" information of the app.
AppAboutInfo = namedtuple('AppAboutInfo', ['name', 'version', 'copyright', 'author', 'license', 'source', 'help_file'],
                          defaults = {'name':'my app', 'version':'X.X', 'copyright':'20XX', 'author':'John Q. Public',
                                      'license':'MIT License', 'source':'github url', 'help_file':''})


# TODO: Refactor the way the menubar is created, so that File|Exit and Help|About are always present. If the
# user provides a non-empty menu_dict, and it contains File|Exit or Help|About, then use the user's handler.
# If the user provides an empty menu_dict, or a non-empty menu_dict that does not contain File|Exit or Help|About,
# then add those items with the default handlers.
class tkApp(ttk.Frame):
    """
    Abstract base class for applications built using tkinter.
    Concrete implementation child classes must:
        (1) Implement the factory method _createViewManager() to create and return a tkViewManager instance,
            which will create and manage the widgets of the application.
        (2) Implement _createModel() factory method to create and return a Model instance, which 
            holds the data and business logic of the application.
    Concrete implementation child classes likely will:
        (3) Pass AboutAppInfo named tuple into super.__init__() to set up the app's About dialog.
        (4) Pass menu_dict into super.__init__() to set up the app's menubar.
        (5) Pass file_types into super.__init__() to set up the file types for file dialogs.
        (6) Define and implement handler functions for menubar selections, beyond OnFileOpen, OnFileSave,
            OnFileSaveAs, OnFileExit, and OnHelpAbout.
    Concrete implementation child classes may:
        (7) Extend _setup_child_widgets() if the tkViewManager does not create all of the app's widgets
    """
    def __init__(self, parent, title = '', menu_dict = {}, app_info = AppAboutInfo(), file_types=[],
                 log_level = logging.INFO) -> None:
        """
        :parameter parent: The top-level tkinter widget, typicaly the return value from tkinter.Tk()
        :parameter title: The title of the application, to appear on the app's main window, string
        :parameter menu_dict: A dictionary describing the app's menubar:
            {menu text string : handler callable or another menu_dict if there is a cascade}
            If menu_dict is empty, then the menubar will only have:
                (a) File|Open... which will call OnFileOpen
                (b) File|Save which will call OnFileSave
                (c) File|Save As... which will call OnFileSaveAs
                (d) File|Exit which will call OnFileExit
                (e) Help|About... which will call OnHelpAbout
            If menu_dict is not empty, then the above items will not be added to the menubar automatically.
        :parameter app_info: An AppAboutInfo named tuple with the app's "About" information:
            (name, version, copyright, author, license, source, help_file), all fields provided as strings
            Example:
            ('my app', 'X.X', '20XX', 'John Q. Public', 'MIT License', 'github url')
        :parameter file_types: A list of file type tuples for saving and opening, in this format:
            [('Description1', '*.ext1'), ('Description2', '*.ext2'), ...]
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        """
        super().__init__(parent)

        self._appInfo = app_info
        self._fileTypes = list(file_types) # List of file extensions for file dialogs
        self._savePath = '' # Path of last save, empty string if never saved
        
        # self._menuConfigDict is a dictionary of the following form, provided here as an example:        
        #   self._menuConfigDict = {'File':(File_menu_obj, {'Start Simulation':(None, 0_index_on_file_menu_obj)})}
        # key is always a string that exactly matches a menu item. value is always a tuple. If we have a cascade,
        # then the tuple is (menu_object, cascade_menu_dictionary). If we have a menu command, then the tuple is
        # (None, 0-based_index_of_command_on_menu_object)
        # This dictionary is populated when self._setup_menubar() is called, and it can be used, for example,
        # to enable and disable menu items, like thus:
        # self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['Start Simulation'][1], state=DISABLED)
        # Note that when getting the object to call entryconfig() on, the tuple index at the end will always be [0], whereas
        # an previous tuple indices would be [1].
        # And, when getting the menu index to use in the entryconfig() call, all tuple indices should be [1]
        # TODO: Using the dictionary to call entryconfig() is so cryptic that a helper function would be nice.
        self._menuConfigDict = {}

        self.grid(column=0, row=0, sticky='NWES') # Grid-0
        # Weights control the relative "stretch" of each column and row as the frame is resized
        parent.columnconfigure(0, weight=1) # Grid-0
        parent.rowconfigure(0, weight=1) # Grid-0
        parent.option_add('*tearOff', False) # Prevent menus from tearing off
        parent.title(title)

        # Create and setup a menubar for the app
        if len(menu_dict)==0:
            # menu_dict is empty, so just set up File | [Open, Save, Save As, Exit] and Help | [View Help, About] by default
            file_menu_dict={}
            file_menu_dict['Open...']=self.onFileOpen
            file_menu_dict['Save']=self.onFileSave
            file_menu_dict['Save As...']=self.onFileSaveAs
            file_menu_dict['Exit']=self.onFileExit
            help_menu_dict={}
            help_menu_dict['View Help...']=self.onViewHelp
            help_menu_dict['About...']=self.onHelpAbout
            menu_dict['File']=file_menu_dict
            menu_dict['Help']=help_menu_dict
        self._setup_menubar(menu_dict)

        # Create and initialize the model of the app
        self._model = self._createModel()
        
        # Create and setup the child widgets of the app, including the view manager self._view_manager
        self._setup_child_widgets()

        # Attach view manager as observer of model
        self._model.attach(self._view_manager)
        
        # Process running the HelpApp
        self._help_process = None

        # If the user X's the main window, make sure we clean up 
        parent.protocol("WM_DELETE_WINDOW", self.onFileExit)

        # Set up logging for this app
        self._setup_logging(log_level)
        
        # Get the logger 'tkApp_logger'
        logger = logging.getLogger('tkApp_logger')
        logger.debug(f"Starting {self._appInfo.name} version {self._appInfo.version}")
        logger.debug(f"Menu configuration dictionary: {self._menuConfigDict}")

    def getModel(self):
        """
        Accessor method to return the model of the app.
        :return: The model of the app, instance of Model
        """
        return self._model
        
    def _setup_menubar(self, menu_dict={}):
        """
        Utility function to be called by __init__ to set up the menu bar of the app.
        :parameter menu_dict: A dictionary describing the app's menubar:
            {menu text string : handler callable or another menu_dict if there is a cascade}
        :return: None
        """
        self._menubar = tk.Menu(self.master)
        self.master['menu'] = self._menubar
        self._setup_menu(menu_dict, self._menubar, self._menuConfigDict)
        return None

    def _setup_menu(self, menu_dict={}, add_to_menu=None, config_dict={}):
        """
        Utility function to be called by _setup_menubar(...) to set up one cascade menu. Designed to be called
        recursively as needed.
        :parameter menu_dict: A dictionary describing a cascade menu:
            {menu text string : handler callable or another menu_dict if there is another cascade}
        :parameter add_to_menu: The cascade menu object to which the next cascade or action should be added
        :parameter config_dict: The nested dictionary within self._menuConfigDict to which the next cascade or
                                action should be added
        :return: None
        """
        index = 0
        for menu_label in menu_dict:
            menu_action = menu_dict[menu_label]
            if type(menu_action) is dict:
                index += 1
                # Set up a cascade
                menu_obj=tk.Menu(add_to_menu)
                add_to_menu.add_cascade(menu=menu_obj, label=menu_label)
                # For later access to menu command, store in self._menuConfigDict
                # a new entry for key=menu_label, with tuple (menu_obj, new empty {}) as the value
                cascade_dict = {}
                config_dict[menu_label] = (menu_obj, cascade_dict)
                # Recurse downward into the new cascade    
                self._setup_menu(menu_action, menu_obj, cascade_dict)
            else:
                assert(callable(menu_action))
                add_to_menu.add_command(label=menu_label, command=menu_action)
                # For later access to menu command, store in self._menuConfigDict
                # a new entry for key=menu_label, with tuple (None, index_on_add_to_menu)
                config_dict[menu_label] = (None, index)
                index += 1
        return None

    def _setup_child_widgets(self):
        """
        Utility function to be called by __init__ to set up the child widgets of the app.
        This function calls the factory method _createViewManager() to create a tkViewManager instance for the app.
        It is expected that the tkViewManager will create all other widgets of the app. If this is not the case
        then this method should be extended by the child class.
        :return: None
        """
        self._view_manager = self._createViewManager()
        self._view_manager.grid(column=0, row=0, sticky='NWES') # Grid-1
        self.columnconfigure(0, weight=1) # Grid-1
        self.rowconfigure(0, weight=1) # Grid-1
        return None

    def _createViewManager(self):
        """
        This is an abstract factory method called to create and return a tkViewManager instance.
        Must be implemented by children to create a child of tkViewManager.
        Will raise NotImplementedError if called.
        :return: An instance of a concrete implementation child class of tkViewManager
        """
        raise NotImplementedError
        return None

    def _createModel(self):
        """
        This is an abstract factory method called to create and return a Model instance.
        Must be implemented by children to create a child of Model
        Will raise NotImplementedError if called.
        :return: An instance of a concrete implementation child class of Model
        """
        raise NotImplementedError
        return None

    def getAboutInfo(self):
        """
        Method to be called to get the "About" information of the app.
        :return: AppAboutInfo named tuple with the app's "About" information:
            (name, version, copyright, author, license, source), all fields returned as strings
            Example:
            ('my app', 'X.X', '20XX', 'John Q. Public', 'MIT License', 'github url')
        """
        return self._appInfo
    
    def onFileOpen(self):
        """
        Respond to a File|Open menu selection by using the tkFileDialog for open to get the path,
        then opening that path for read, and calling the model's readModelFromFile(...) method.
        :return: None
        """
        initial_dir = None
        if len(self._savePath)>0:
            initial_dir = os.path.dirname(self._savePath)
        else:
            initial_dir = os.getcwd()
        # Pop up tkFileDialog for open
        response = filedialog.askopenfilename(defaultextension=self._fileTypes[0][1], filetypes=self._fileTypes,
                                              initialdir=initial_dir, title='Select file to open')
        if len(response)>0: # User did not cancel
            with open(response) as f:
                self._model.readModelFromFile(f, os.path.splitext(response)[1])
                self._savePath = response
        return None

    def onFileSave(self):
        """
        Respond to a File|Save menu selection by opening self._savePath for write, and
        calling the model's writeModelToFile(...) method. If self._savePath is '',
        because there has not been a previous open or save as, then do nothing.
        :return: None
        """
        if len(self._savePath)>0:
            with open(self._savePath, mode='w') as f:
                self._model.writeModelToFile(f, os.path.splitext(self._savePath)[1])
        return None

    def onFileSaveAs(self):
        """
        Respond to a File|Save As menu selection by using the tkFileDialog for save to get the path,
        then opening that path for write, and calling the model's writeModelToFile(...) method.
        :return: None
        """
        initial_dir = None
        if len(self._savePath)>0:
            initial_dir = os.path.dirname(self._savePath)
        else:
            initial_dir = os.getcwd()
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(defaultextension=self._fileTypes[0][1], filetypes=self._fileTypes,
                                                initialdir=initial_dir, title='Select file to save as')
        if len(response)>0: # User did not cancel
            with open(response, mode='w') as f:
                self._model.writeModelToFile(f, os.path.splitext(response)[1])
                self._savePath = response
        return None

    def onFileExit(self):
        """
        Method called when menu item File | Exit is selected.
        :return: None
        """
        # Get the logger 'tkApp_logger'
        logger = logging.getLogger('tkApp_logger')

        if self._help_process:
            logger.debug(f"Help Process {self._help_process.name} is alive={self._help_process.is_alive()}")

        self.master.destroy()
        return None

    def onViewHelp(self):
        """
        Method called when menu item Help | View Help is selected. Launch help app to view help.
        :return: None
        """
        if not self._help_process or not self._help_process.is_alive():
            # Help app is not running, so launch it
            self._help_process = Process(target=_launch_help_app, name='HelpApp Process', kwargs={'help_file':self._appInfo.help_file})
            self._help_process.start()
        return None

    # TODO: Investigate if instead of showinfo(...) we can create a pop-up dialog that contains a
    # tkinter.Text widget, so that the app's "About" information can be "rich" formatted text.
    # This would allow clickable hyperlink for source, bold, italic, etc. Requires investigation of 
    # ability to auto tag text in the widget.
    def onHelpAbout(self):
        """
        Method called when menu item Help | About is selected.
        :return: None
        """
        msg = self._appInfo.name + '\n'
        msg += 'version ' + self._appInfo.version + '\n'
        msg += 'Copyright (c) ' + self._appInfo.copyright + ' by ' + self._appInfo.author + '\n'
        msg += 'Licensed under the ' + self._appInfo.license + '\n'
        msg += 'Source: ' + self._appInfo.source
        dialog_title = 'About ' + self._appInfo.name
        showinfo(title=dialog_title, message=msg, parent=self.master)
        return None

    def _setup_logging(self, log_level=logging.INFO):
        """
        This method configures logging.
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        :return: None
        """
        # Create a logger with name 'tkApp_logger'. This is NOT the root logger, which is one level up from here, and has no name.
        logger = logging.getLogger('tkApp_logger')
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
            
        return None


class tkHelpApp(tkApp):
    """
    Class represent help application built using tkinter, leveraging tkApp framework.
    """
    def __init__(self, parent, help_file='') -> None:
        """
        :parameter help_file: Path to the help file to be opened and displayed initially, string
        """
        info = AppAboutInfo(name='Help Application', version='0.9.0', copyright='2025', author='Kevin R. Geurts',
                                  license='MIT License', source='https://github.com/KevinRGeurts/tkAppFramework')
        menu_dictionary = {'File':{'Exit':self.onFileExit},
                           'Help':{'About...':self.onHelpAbout}}
        super().__init__(parent, title="Help Application", menu_dict=menu_dictionary, app_info=info)
        self._model.help_file = help_file
        
    def _createViewManager(self):
        """
        Factory method to create the view manager for the app.
        """
        return tkHelpViewManager(self)

    def _createModel(self):
        """
        Factory method to create the model for the app.
        :return: The model for the app, HelpModel
        """
        model = HelpModel()
        return model
        



