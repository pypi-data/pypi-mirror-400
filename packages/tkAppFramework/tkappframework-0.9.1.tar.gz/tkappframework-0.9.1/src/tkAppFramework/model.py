"""
Defines the abstract base class Model, from which classes representing the data and business logic of an application
should be derived.

Concrete implementation child classes likely will:
    (1) Implement readModelFromFile() method for reading model data from a file-like object.
        (a) Before reading from a file, the model may need to clear exsisting data.    
        (b) After reading from a file, the model should call self.notify() to inform observers of changes.
    (2) Implement writeModelToFile() method for writing model data to a file-like object.

Exported Classes:
    Model -- Interface (abstract base) class for classes representing the data and business logic
             of an application. Model is a Subject in the Observer design pattern.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# standard imports

# local imports
from tkAppFramework.ObserverPatternBase import Subject


class Model(Subject):
    """
    Model is the abstract base class from which classes representing the data and business logic of an application
    should be derived.

    Model is a Subject in the Observer design pattern.

    Concrete implementation child classes likely will:
        (1) Implement readModelFromFile() method for reading model data from a file-like object.
            (a) Before reading from a file, the model may need to clear exsisting data.    
            (b) After reading from a file, the model should call self.notify() to inform observers of changes.
        (2) Implement writeModelToFile() method for writing model data to a file-like object.
    """
    def __init__(self) -> None:
        """Initialize the Model."""
        super().__init__()
        # Initialize model data here

    def readModelFromFile(self, file, filetype) -> None:
        """
        Abstract method for reading the model data from a file-like object. Must be implemented by
        subclasses to be useful, as otherwise will raise NotImplementedError if called.
        :parameter file: A file-like object from which to read the model data.
        :parameter filetype: A string indicating the type of file (e.g., 'json', 'xml', etc.).
        :return: None
        """
        raise NotImplementedError("Subclasses must implement readModelFromFile(...) method.")
        return None

    def writeModelToFile(self, file, filetype) -> None:
        """
        Abstract method for Writing the model data to a file-like object. Must be implemented by
        subclasses to be useful, as otherwise will raise NotImplementedError if called.
        :parameter file: A file-like object to which to write the model data.
        :parameter filetype: A string indicating the type of file (e.g., 'json', 'xml', etc.).
        :return: None
        """
        raise NotImplementedError("Subclasses must implement writeModelToFile(...) method.")
        return None




