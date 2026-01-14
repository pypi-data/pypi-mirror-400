"""
This module provides the HelpModel class, which represents the "business logic" of an application for viewing help

Exported Classes:
    HelpModel -- This class represents the help content, and is a Model in the MVC pattern.

Exported Exceptions:
    None    
 
Exported Functions:
    None.
"""

# standard imports

# local imports
from tkAppFramework.model import Model


class HelpModel(Model):
    """
    This class represents the "business logic" of help content, and is a Model in the MVC pattern.
        _help_file: Path to the help file to be opened and displayed initially, string
    """
    def __init__(self, help_file='') -> None:
        """
        :parameter help_file: Path to the help file to be opened and displayed initially, string
        """
        super().__init__()
        self.help_file = help_file

    @property
    def help_file(self):
        return self._help_file

    @help_file.setter
    def help_file(self, value):
        assert(type(value) is str)
        self._help_file = value
        self.notify()


