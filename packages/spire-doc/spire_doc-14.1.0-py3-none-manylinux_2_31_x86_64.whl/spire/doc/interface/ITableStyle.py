from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class ITableStyle (  IParagraphStyle, ICharacterStyle, IStyle) :
    """
    Represents the style that can be used to format a Table.
    """
    @property

    @abc.abstractmethod
    def HorizontalAlignment(self)->'RowAlignment':
        """

        """
        pass


    @HorizontalAlignment.setter
    @abc.abstractmethod
    def HorizontalAlignment(self, value:'RowAlignment'):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def VerticalAlignment(self)->'VerticalAlignment':
        """

        """
        pass


    @VerticalAlignment.setter
    @abc.abstractmethod
    def VerticalAlignment(self, value:'VerticalAlignment'):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def IsBreakAcrossPages(self)->bool:
        """

        """
        pass


    @IsBreakAcrossPages.setter
    @abc.abstractmethod
    def IsBreakAcrossPages(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def Bidi(self)->bool:
        """

        """
        pass


    @Bidi.setter
    @abc.abstractmethod
    def Bidi(self, value:bool):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def CellSpacing(self)->float:
        """

        """
        pass


    @CellSpacing.setter
    @abc.abstractmethod
    def CellSpacing(self, value:float):
        """

        """
        pass


    @property
    @abc.abstractmethod
    def LeftIndent(self)->float:
        """

        """
        pass


    @LeftIndent.setter
    @abc.abstractmethod
    def LeftIndent(self, value:float):
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Borders(self)->'Borders':
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Shading(self)->'Shading':
        """

        """
        pass


    @property

    @abc.abstractmethod
    def Paddings(self)->'Paddings':
        """

        """
        pass


    @property

    @abc.abstractmethod
    def ConditionalStyles(self)->'TableConditionalStyleCollection':
        """

        """
        pass


