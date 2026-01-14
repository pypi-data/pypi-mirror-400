from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class IParagraphStyle (  ICharacterStyle, IStyle) :
    """
    Represents a paragraph style.
    """
    @property

    @abc.abstractmethod
    def ParagraphFormat(self)->'ParagraphFormat':
        """

        """
        pass


