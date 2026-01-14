"""
This module provides Observer and Subject classes that can be a parent of classes that implement an Observer design pattern.

Exported Classes:
    Observer -- Base class for all objects that will be an Observer in an Observer design pattern.
        All Observer child classes must implement the update(...) method.
    Subject -- Base class for all objects that will be a Subject in an Observer design pattern.
        Subjects should attach(...) and detach(...) Observers, and notify() them of changes in state.

Exported Exceptions:
    None
 
Exported Functions:
    None
"""


class Observer:
    """
    Base class for all objects that will be an Object in an Observer design pattern.

    Child classes must implement the update(...) method.
    """
    def __init__(self):
        pass

    def update(self, subject):
        """
        Interface method called by Subject to notify observer of a change in state. Must be implemented by children.
        Will raise NotImplementedError if called.
        :parameter subject: Which Subject instance is notifying the Observer instance?
        :return None:
        """
        raise NotImplementedError
        return None


class Subject:
    """
    Base class for all objects that will a Subject in an Observer design pattern.
    """
    def __init__(self) -> None:
        """
        """
        self._observers = []

    def attach(self, observer=None):
        """
        Attach an observer to the subject.
        :parameter observer: Observer object, instance of Observer class 
        :return None:
        """
        if observer:
            assert(isinstance(observer, Observer))
            self._observers.append(observer)
        return None

    def detach(self, observer=None):
        """
        Detach an observer from the subject.
        :parameter observer: Observer object, instance of Observer class 
        :return None:
        """
        if observer:
            self._observers.remove(observer)
        return None

    def notify(self):
        """
        Call update(...) on all observers.
        :return None:
        """
        for o in self._observers:
            o.update(self)
        return None
