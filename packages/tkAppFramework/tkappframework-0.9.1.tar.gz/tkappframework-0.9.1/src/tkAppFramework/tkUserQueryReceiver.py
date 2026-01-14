"""
tkUserQueryReceiver is a concrete implementation of UserResponseCollector.UserQueryReceiver.UserQueryReceiver.

A concrete UserResponseCollector.UserQueryCommand.UserQueryCommand object can use tkUserQueryReceiver to obtain raw responses
from the user through a tkInter based GUI. The workflow is:
(1) Add an objectified query message to a FIFO query queue in the tkinter app, that runs on the tkinter thread.
(2) Generate an event to a designated tkinter widget that will handle input, that a query is waiting in the queue.
(3) Sit in a tight loop, checking a separate response queue that runs in the same thread as self, waiting for the tkinter widget
to place an objectified response message in the response queue.
(4) Read the response message from the respone queue, exit the tight loop, and act on the response. 

Exported Classes:
    tkUserQueryReceiver -- A concrete UserResponseCollector.UserQueryReceiver.UserQueryReiver object that can provide raw responses
                           to any code that creates and Executes() UserResponseCollector.UserQueryCommand.UserQueryCommand  objects,
                           obtaining the raw responses from the user through a tkInter based GUI.
    QueryInfo -- Named tuple subclass used to objectify query messages placed in the tkinter app's query queue.
    QueryResponse -- Named tuple subclass used to objectify response messages placed in the response queue by the tkinter app.

Exported Exceptions:
    UserQueryReceiverBadResponseError - Custom exception to be raised when the tkinter-based app returns a raw response that cannot be successfully converted to
                                        a processed response.

Exceptions Raised:
    UserResponseCollector.UserQueryReceiver.UserQueryReceiverTerminateQueryingThreadError - Raised if a response of
        '<<QueryingThreadTerminationRequest>>' is received in the response queue.
 
Exported Functions:
    UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver -- Global prebound method that returns the global, single instance of a concrete UserQueryReceiver.
        Replaces the original prebound method implemented in UserResponseCollector.UserQueryReceiver so that the global instance IS-A tkUserQueryReceiver.
        See for reference:
            (1) Global Object Pattern: https://python-patterns.guide/python/module-globals/
            (2) Prebound Method Pattern: https://python-patterns.guide/python/prebound-methods/
    tkUserQueryReceiver_setup -- Global prebound method for calling the setup() method of the global tkUserQueryReceiver instance.
"""

# Standard
from tkinter.messagebox import showerror
# from tkinter import filedialog
from collections import namedtuple
from uuid import uuid4
from time import sleep
from queue import Queue
# from pathlib import Path

# Local
import UserResponseCollector.UserQueryReceiver

class UserQueryReceiverBadResponseError(UserResponseCollector.UserQueryReceiver.UserQueryReceiverError):
    """
    Custom exception to be raised when the tkinter-based app returns a raw response that cannot be successfully converted to
    a processed response.
    Arguments expected in **kwargs:
        none at this time    
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)


# Define a tuple subclass QueryInfo that will be the objectified query message placed in the query queue
# Fields:
# prompt_text: Text displayed to the user to request their response, string
# query_ID: Unique identifier of the query, which should be returned with the response to help ensure the the query and response are matched up
#               correctly since they are placed in different queues, string from str(uuid)
QueryInfo = namedtuple('QueryInfo', ['prompt_text', 'query_ID'])

# Define a tuple subclass QueryResponse that will be the objectified query message placed in the response queue
# Fields:
# query_response: Response returned by the tkinter app to the query request, always a string of text
# query_ID: Unique identifier of the query, which should be returned with the response to help ensure the the query and response are matched up
#               correctly since they are placed in different queues, string from str(uuid)
QueryResponse = namedtuple('QueryResponse', ['query_response','query_ID'])


class tkUserQueryReceiver(UserResponseCollector.UserQueryReceiver.UserQueryReceiver):
    """
    Following the Command design pattern, this is a concrete implementation of a UserQueryReceiver, that a concrete UserQueryCommand object
    can use to obtain raw responses from the user through a tkInter based GUI. The workflow is:
    (1) Add an objectified query message to a FIFO query queue in the tkinter app, that runs on the tkinter thread.
    (2) Generate an event to a designated tkinter widget that will handle input, that a query is waiting in the queue.
    (3) Sit in a tight loop, checking a separate response queue that runs in the same thread as self, waiting for the tkinter widget
    to place an objectified response message in the response queue.
    (4) Read the response message from the respones queue, exit the tight loop, and act on the response. 
    """
    def __init__(self, query_event_callback=None, query_queue_callback=None):
        """
        :parameter query_event_callback: Calleable object (e.g., tkinter_widget.event_generate(<<event>>) that will generate events when self
        has placed a query message in the tkinter app's query queue.
        :parameter query_queue_callback: Calleable object (e.g., tkinter_wdiget.put_item_in_queue(item, timeout=)) that will place a query message
        in the queury queue.
        """
        UserResponseCollector.UserQueryReceiver.UserQueryReceiver.__init__(self)
        # Sanity check the arguments to make sure they are callable. This does not guarantee they are bound methods, e.g., a class is callable
        # for construction. But it is better than nothing.
        if query_event_callback: assert(callable(query_event_callback))
        if query_queue_callback: assert(callable(query_queue_callback))
        self._query_event_callback = query_event_callback
        self._query_queue_callback = query_queue_callback
        # The queue where we expect the tkinter-based app to place the objectifed response to the query, to be accessed through a method.
        self._response_queue = Queue(10)
        # A time in seconds to wait when attempting to access a queue with a put or get before timing out
        self._queue_access_timeout = 1
    
    def GetRawResponse(self, prompt_text=''):
        """
        Called to obtain a raw response from the user through thier interaction with the tkinter based app, which will always be a sting of text.
        :parameter prompt_text: String of text to use to tell the user what response is requrired, string
        :return: raw_response, string
        Raises UserResponseCollector.UserQueryReceiver.UserQueryReceiverTerminateQueryingThreadError exception if a response of
        '<<QueryingThreadTerminationRequest>>' is received in the response queue.
        """
        # Check that a valid set up has been provided, either through __init__ or by calling setup()
        assert(self._query_queue_callback is not None)
        assert(self._query_event_callback is not None)
        
        # Create a unique ID for the query
        query_ID = uuid4()

        # Package up the query information in a named tuple
        query_message = QueryInfo(prompt_text, str(query_ID))

        # Place the query message in the query queue in the tkinter app
        self._query_queue_callback(query_message)

        # Generate event that will cause the query item to be picked out of the tkinter event queue and acted on
        self._query_event_callback('<<TkinterAppQueryEvent>>')

        # Wait in a tight loop for the tkinter app to provide a response in the response queue
        while self._response_queue.empty():
            sleep(1)
        response = self._response_queue.get(timeout=self._queue_access_timeout)

        # Check if response is the string '<<QueryingThreadTerminationRequest>>'
        if response.query_response == '<<QueryingThreadTerminationRequest>>':
            # Raise exception
            raise UserResponseCollector.UserQueryReceiver.UserQueryReceiverTerminateQueryingThreadError(f"tkinter app has requested that querying thread terminate.")

        # Assert that the query_ID of the response matches the query_ID of the request
        assert(response.query_ID == str(query_ID))

        raw_response = response.query_response

        return raw_response
    
    def IssueErrorMessage(self, msg=''):
        """
        Called to inform the user that their raw response does not meet requirements.
        :parameter msg: Error message to be shown to the user, string
        :return: None       
        """
        # Let the user know that there was a problem with their response, by popping up a tkMessageBox dialog
        showerror(title='User Query Error', message=msg)
        # print(msg)
        return None
    
    def setup(self, query_event_callback, query_queue_callback):
        """
        Establish the callbacks required by objects in order to process queries.
        :parameter query_event_callback: Calleable object (e.g., tkinter_widget.event_generate(<<event>>) that will generate events when self
        has placed a query message in the tkinter app's query queue.
        :parameter querey_queue_callback: Calleable object (e.g., tkinter_wdiget.put_item_in_queue(item, timeout=)) that will place a query message
        in the queury queue.
        :return None:
        """
        assert(callable(query_event_callback))
        assert(callable(query_queue_callback))
        self._query_event_callback = query_event_callback
        self._query_queue_callback = query_queue_callback
        return None

    def put_response_in_queue(self, response):
        """
        Method to be provided as a callback to the tkinter-based app, to be called by the app to provided a response to a query.
        :parameter response: The objectified response to be placed in the response queue, QueryResponse object
        :return None:
        """
        self._response_queue.put(response, timeout=self._queue_access_timeout)
        return None


# Replace the global (intended to be private), single instance, with an object of the new subclass
UserResponseCollector.UserQueryReceiver._instance = tkUserQueryReceiver()

# Replace the global prebound method(s)
UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver = UserResponseCollector.UserQueryReceiver._instance.GetCommandReceiver

# Create a global prebound method for setup
tkUserQueryReceiver_setup = UserResponseCollector.UserQueryReceiver._instance.setup


