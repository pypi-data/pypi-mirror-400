"""
Defines the abstract base class SimulatorAdapter, which follows an Adapter design pattern. It's client is a SimulatorModel object.
It's adaptee is a simulator. It is expected that a new subclass (e.g. BlackJackSimulatorAdapter) will need to be created for each simulator
that is serviced by the tkSimulatorApp. This should be the only "customization" required. The tkSimulatorApp,
SimulatorModel, and tkSimulatorViewManager should be able to service any simulator that meets certain requirements,
as long as an approriate SimulatorAdapter subclass can be created.

Simulator requirements:
(1) Obtain all user input through execution of UserQueryCommand objects.
(2) Provide all output to user through python logging library.
(3) Appropriately captures UserQueryReceiver.UserQueryReceiverTerminateQueryingThreadError exception as a request
    to gracefully terminate itself.

Subclasses must:
(1) Implement run() - Which should call a method of self._simulator to start a simulation
Subclasses may also implement:
(1) load_and_run() - Which should load a simulation state and run the simulation with that state.

Exported Classes:
    SimulatorAdapter -- Interface (abstract base) class for classes that adapt a simulator to the
                        tkSimulatorApp.

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    None
"""

# standard imports
from queue import Queue
from logging.handlers import QueueHandler
import logging

# local imports


class SimulatorAdapter(object):
    """
    This abstract base class follows an Adapter design pattern. It's client is a SimulatorModel object. It's adaptee is a simulator.
    It is expected that a new subclass (e.g. BlackJackSimulatorAdapter) will need to be created for each simulator
    that is serviced by the tkSimulatorApp. This should be the only "customization" required. The tkSimulatorApp,
    SimulatorModel, and tkSimulatorViewManager should be able to service any simulator that meets certain requirements,
    as long as an approriate SimulatorAdapter subclass can be created.

    Simulator requirements:
    (1) Obtain all user input through execution of UserQueryCommand objects.
    (2) Provide all output to user through python logging library.
    (3) Appropriately captures UserQueryReceiver.UserQueryReceiverTerminateQueryingThreadError exception as a request
        to gracefully terminate itself.

    Subclasses must:
    (1) Implement run() - Which should call a method of self._simulator to start a simulation
    Subclasses may also implement:
    (1) load_and_run() - Which should load a simulation state and run the simulation with that state
    """
    def __init__(self, sim=None, logger_name='', logging_queue=None, logging_level = logging.INFO):
        """
        :paramter sim: The simulator object adaptee of the simualator adapter object, any type
        :parameter logger_name: The name of a logging.logger that the simulator object adaptee uses for its
                                simulation output.
        :parameter logging_queue: The Queue() object for a logging queue handler. This queue will receive
                                  the simulation output LogRecords. It should always be set to
                                  tkSimulatorApp.sim_output_queue property.
        :parameter logging_level: The threshold for the queue handler, e.g. logging.INFO or logging.DEBUG
        """
        self.simulator = sim
        self._setup_logging(logger_name, logging_queue, logging_level)

    @property
    def simulator(self):
        return self._simulator

    @simulator.setter
    def simulator(self, value):
        self._simulator = value

    def run(self):
        """
        This abstract method must be implemented by subclasses. When called, it should start a simulation.
        :return: None
        """
        raise NotImplementedError
        return None

    def load_and_run(self):
        """
        This abstract method must be implemented by subclasses. When called, it should load a simulation state and run the
        simulation with that state.
        """
        raise NotImplementedError
        return None
    
    def _setup_logging(self, name='', queue=None, log_level = logging.INFO):
        """
        Add a queue handler to the simulator's logger. The queue that this queue handler writes to will be
        the queue from which the tkSimulatorViewManager obtains simulator output.
        :parameter name: The name of a logging.logger that the simulator object adaptee uses for its
                         simulation output, as string
        :parameter logging_queue: The Queue() object for a logging queue handler. This queue will receive
                                  the simulation output LogRecords. As Queue object.
        :parameter logging_level: The threshold for the queue handler, e.g. logging.INFO or logging.DEBUG
        """
        assert(type(name)==str and len(name)>0)

        # Get the adaptee simulator's logger
        logger = logging.getLogger(name)
        
        # If argument queue is not None, and a name has been provided, then set up the simulator logger with a QueueHandler
        if queue is not None:
            assert(isinstance(queue, Queue))
            qh = logging.handlers.QueueHandler(queue)
            # Set the threshold for the queue handler itself, which will come into play only after the logger threshold is met.
            qh.setLevel(log_level)
            # Add the queue handler to the logger
            logger.addHandler(qh)

