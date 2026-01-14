from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class SearchOptions (SpireObject) :
    """
    Document search options.
    """

    def __init__(self):
        """
        Initializes a new instance of the SearchOptions class with no params.
        """

        GetDllLibDoc().SearchOptions_CreateSearchOptions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().SearchOptions_CreateSearchOptions)
        super(SearchOptions, self).__init__(intPtr)

    @property
    def IgnoreOfficeMath(self)->bool:
        """
        Gets or sets a value indicating whether to ignore officeMath when finding or replacing.
        The default is true.
        """
        GetDllLibDoc().SearchOptions_get_IgnoreOfficeMath.argtypes=[c_void_p]
        GetDllLibDoc().SearchOptions_get_IgnoreOfficeMath.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().SearchOptions_get_IgnoreOfficeMath,self.Ptr)
        return ret

    @IgnoreOfficeMath.setter
    def IgnoreOfficeMath(self, value:bool):
        GetDllLibDoc().SearchOptions_set_IgnoreOfficeMath.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().SearchOptions_set_IgnoreOfficeMath,self.Ptr, value)

    @property
    def MatchCase(self)->bool:
        """
        Gets or sets a value indicating whether the match is case-sensitive.
        """
        GetDllLibDoc().SearchOptions_get_MatchCase.argtypes=[c_void_p]
        GetDllLibDoc().SearchOptions_get_MatchCase.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().SearchOptions_get_MatchCase,self.Ptr)
        return ret

    @MatchCase.setter
    def MatchCase(self, value:bool):
        GetDllLibDoc().SearchOptions_set_MatchCase.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().SearchOptions_set_MatchCase,self.Ptr, value)

    @property
    def FindWholeWordsOnly(self)->bool:
        """
        Gets or sets a value indicating whether the search should match whole words only.
        """
        GetDllLibDoc().SearchOptions_get_FindWholeWordsOnly.argtypes=[c_void_p]
        GetDllLibDoc().SearchOptions_get_FindWholeWordsOnly.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().SearchOptions_get_FindWholeWordsOnly,self.Ptr)
        return ret

    @FindWholeWordsOnly.setter
    def FindWholeWordsOnly(self, value:bool):
        GetDllLibDoc().SearchOptions_set_FindWholeWordsOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().SearchOptions_set_FindWholeWordsOnly,self.Ptr, value)