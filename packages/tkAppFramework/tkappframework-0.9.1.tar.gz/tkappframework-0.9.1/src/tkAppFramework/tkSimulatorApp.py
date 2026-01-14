"""
Defines tkSimulatorApp class, which is a concrete implementation of tkApp for simulator applications.

Class is a child of tkApp, extending it's functionality for "simulator" type applications, where there is a
simulator engine that is "in control", rather than control being the user interacting with the GUI. The GUI
becomes a thin shell for launching the simulator on a separate thread. The simulator then progresses as it
wishes, but periodically requests input from the user through tkUserQueryReceiver, and periodically uses
logging to send output caught by tkSimulatorViewManager.

Exported Classes:
    tkSimulatorApp -- Is-A tkAppnterface implementation for simulator applications.

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    None
"""


# standard imports
import tkinter as tk
from tkinter import ttk
from threading import Thread
import sysconfig

# local imports
# -- Leave these next two imports EXACTLY how they are, so that tkUserResponseCollector correctly changes values of globals in UserResponseCollector --
import UserResponseCollector.UserQueryReceiver
import tkAppFramework.tkSimulatorViewManager
import tkAppFramework.tkUserQueryReceiver
# -- End Leave --
from tkAppFramework.tkApp import tkApp, AppAboutInfo
from tkAppFramework.tkUserQueryViewManager import tkUserQueryViewManager
from tkAppFramework.tkSimulatorViewManager import tkSimulatorViewManager
from tkAppFramework.SimulatorModel import SimulatorModel


class tkSimulatorApp(tkApp):
    """
    Class is a child of tkApp, extending it's functionality for "simulator" type applications, where there is a
    simulator engine that is "in control", rather than control being the user interacting with the GUI. The GUI
    becomes a thin shell for launching the simulator on a separate thread. The simulator then progresses as it
    wishes, but periodically requests input from the user through tkUserQueryReceiver, and periodically uses
    logging to send output caught by tkSimulatorViewManager.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The top-level tkinter widget, typicaly the return value from tkinter.Tk()
        """
        help_file_path = sysconfig.get_path('data') + '\\Help\\tkAppFramework\\SimApp_HelpFile.txt'
        info = AppAboutInfo(name='Simulator Application', version='0.9.1', copyright='2025', author='Kevin R. Geurts',
                                  license='MIT License', source='https://github.com/KevinRGeurts/tkAppFramework',
                                  help_file=help_file_path)
        menu_dictionary = {'File':{'Start Simulator':self.onStartSimulator, 'Load Simulation':self.onLoadSimulation, 'End Simulator':self.onEndSimulator, 'Exit':self.onFileExit},
                           'Help':{'View Help...':self.onViewHelp, 'About...':self.onHelpAbout}}
        super().__init__(parent, title="Simulator Application", menu_dict=menu_dictionary, app_info=info)

        # Disable File | End Simulator menu item, since no simulator will now be running
        self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['End Simulator'][1], state=tk.DISABLED)

        # Thread on which the Simulator will be run
        self._sim_thread = None

    def _createViewManager(self):
        """
        Factory method to create the view manager for the app.
        """
        return tkSimulatorViewManager(self)

    def _createModel(self):
        """
        Factory method to create the model (simulator) for the app.
        :return: The model for the app, simulator
        """
        model = SimulatorModel(self)
        return model

    def _setup_child_widgets(self):
        """
        Utility function of tkApp class extended here to set up tkUserQueryViewManager. 
        :return: None
        """
        super()._setup_child_widgets()

        # Setup for tkUserQueryViewManager
        self._query_view_manager = tkUserQueryViewManager(self)
        # Attach view manager as observer of model, because tkViewManager.onDestroy() will attempt detach
        self.getModel().attach(self._query_view_manager)
        self._query_view_manager.grid(column=0, row=0, sticky='NWES') # Grid-1 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx

        # Adjust grid setting for self._view_manager, since we want the UserQueryEntry at the top.
        self._view_manager.grid(column=0, row=1, sticky='NWES') # Grid-1 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(1, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx

        return None

    @property
    def sim_output_queue(self):
        return self.getModel().sim_output_queue
        
    def onFileExit(self):
        """
        Method called when menu item File | Exit is selected.
        Extended from tkApp.onExit() to request simulator termination ahead of exiting.
        """
        self.request_simulator_end()
        super().onFileExit()
        return None
    
    def _run_simulator_helper(self, thread_target=None):
        """
        A helper function called to run the simulator on a separate thread.
        :parameter thread_target: The callable to be called on the new thread to run the simulator, typically
                                  SimulatorModel.run() method.
        """
        # TODO: Call some method on the App (now) or mediator (later) that will clean up the UI ahead of the new simulation, since the previous simulation may have been terminated
        # in the middle. This also requires that the QueryWidget get itself cleaned up.

        if self._sim_thread is None:
            # Call thread_target on a new thread
            self._sim_thread = Thread(target=thread_target)
            self._sim_thread.start()
            # Start processing of the SimulatorModel's simulator event queue
            self._model.SimulatorOutputEventHandler()
            # TODO: The way entryconfig() is used is so cryptic, it cries out for a helper function, which
            # should be defined at the tkApp level.
            # enable File | End Simulator, since we now have a currently running simulation
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['End Simulator'][1], state=tk.NORMAL)
            # disable File | Start Simlator menu item, since we don't want more than one simulator currently running.
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['Start Simulator'][1], state=tk.DISABLED)
            # disable File | Load Simlation menu item, since we don't want more than one simulator currently running.
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['Load Simulation'][1], state=tk.DISABLED)
        else:
            # Do nothing.
            pass
        return None
    
    def onStartSimulator(self):
        """
        Method called when menu item File | Start Simulator is selected.
        """
        self._run_simulator_helper(thread_target=self.getModel().run)
        return None

    def onLoadSimulation(self):
        """
        Method called when menu item File | Load Simulation is selected.
        :return: None
        """
        self._run_simulator_helper(thread_target=self.getModel().load_and_run)
        return None

    def onEndSimulator(self):
        """
        Method called when menu item File | End Simulator is selected.
        :return: None
        """
        if self._sim_thread:
            self._query_view_manager.reset_widgets()
            self.request_simulator_end()
            # Disable File | End Simulator menu item, since no simulator will now be running
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['End Simulator'][1], state=tk.DISABLED)
            # enable File | Start Simulator, since now we have no running simlator
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['Start Simulator'][1], state=tk.NORMAL)
            # enable File | Load Simulation, since now we have no running simlator
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['Load Simulation'][1], state=tk.NORMAL)
        else:
            pass

        return None

    def request_simulator_end(self):
        """
        Utility method that places a termination request in the response queue of the tkUserResponseCollector.
        :return: None
        """
        # Note: Had considered changing this so that instead a request to end the simulator is sent to
        # self._query_view_manager, and it sends the requrired response to the tkUserQueryReceiver, because
        # this may seem like the App getting involved in the business of the query view manager, and that the app
        # should not need to import tkUserQueryReceiver at all. However, it is the app, and not the query view
        # manager that knows that the simulator is running on self._sim_thread, and needs to be requested to shut down
        # like this. So elected to leave this as is.
        
        # Don't do anything if self._sim_thread = None, because there is no running simulator to end.
        
        if self._sim_thread:
            end_sim_response = tkAppFramework.tkUserQueryReceiver.QueryResponse(query_response='<<QueryingThreadTerminationRequest>>', query_ID='')
            UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver().put_response_in_queue(end_sim_response)
            self._sim_thread = None
        else:
            pass
            
        return None
        
        