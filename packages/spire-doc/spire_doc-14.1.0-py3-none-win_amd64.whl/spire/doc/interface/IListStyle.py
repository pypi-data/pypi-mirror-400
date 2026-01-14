from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class IListStyle (  IStyle) :
    """
    Represents a style that defines a list format, including a reference to a list definition.
    """
    @property

    @abc.abstractmethod
    def ListRef(self)->'ListDefinitionReference':
        """
        Gets the reference to a list definition.
        """
        pass


