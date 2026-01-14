from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class ICharacterStyle (  IStyle) :
    """
    Represents the formatting settings for characters within a paragraph.
    """
    @property

    @abc.abstractmethod
    def CharacterFormat(self)->'CharacterFormat':
        """
        Gets formatting of characters inside paragraph.
        """
        pass


