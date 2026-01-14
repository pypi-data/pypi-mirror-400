from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class TableConditionalStyleCollection (  OwnerHolder, IEnumerable) :
    """
    A collection of conditional styles associated with a table.
    This class implements <see cref="IEnumerable{TableConditionalStyle}"/> to allow enumeration over the styles.
    """
    def ClearFormatting(self):
        """
        Clears all conditional styles from the collection, excluding first and last row/column styles.
        """
        GetDllLibDoc().TableConditionalStyleCollection_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_ClearFormatting,self.Ptr)

#
#    def GetEnumerator(self)->'IEnumerator1':
#        """
#
#        """
#        GetDllLibDoc().TableConditionalStyleCollection_GetEnumerator.argtypes=[c_void_p]
#        GetDllLibDoc().TableConditionalStyleCollection_GetEnumerator.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_GetEnumerator,self.Ptr)
#        ret = None if intPtr==None else IEnumerator1(intPtr)
#        return ret
#


    @dispatch

    def get_Item(self ,type:TableConditionalStyleType)->TableConditionalStyle:
        """
        Retrieves a conditional style based on the provided ConditionalStyleType.
        """
        enumtype:c_int = type.value

        GetDllLibDoc().TableConditionalStyleCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibDoc().TableConditionalStyleCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_Item,self.Ptr, enumtype)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @dispatch

    def get_Item(self ,index:int)->TableConditionalStyle:
        """
        Retrieves a conditional style based on the provided index.
        """
        
        GetDllLibDoc().TableConditionalStyleCollection_get_ItemI.argtypes=[c_void_p ,c_int]
        GetDllLibDoc().TableConditionalStyleCollection_get_ItemI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_ItemI,self.Ptr, index)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
        Gets the number of conditional styles in the collection.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_Count.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_Count,self.Ptr)
        return ret

    @property

    def FirstRow(self)->'TableConditionalStyle':
        """
        Gets the conditional style for the first row.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_FirstRow.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_FirstRow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_FirstRow,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def FirstColumn(self)->'TableConditionalStyle':
        """
        Gets the conditional style for the first column.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_FirstColumn.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_FirstColumn.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_FirstColumn,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def LastRow(self)->'TableConditionalStyle':
        """
        Gets the conditional style for the last row.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_LastRow.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_LastRow.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_LastRow,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def LastColumn(self)->'TableConditionalStyle':
        """
        Gets the conditional style for the last column.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_LastColumn.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_LastColumn.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_LastColumn,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def OddRowStripe(self)->'TableConditionalStyle':
        """
        Gets the conditional style for odd row banding.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_OddRowStripe.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_OddRowStripe.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_OddRowStripe,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def OddColumnStripe(self)->'TableConditionalStyle':
        """
        Gets the conditional style for odd column banding.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_OddColumnStripe.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_OddColumnStripe.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_OddColumnStripe,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def EvenRowStripe(self)->'TableConditionalStyle':
        """
        Gets the conditional style for even row banding.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_EvenRowStripe.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_EvenRowStripe.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_EvenRowStripe,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def EvenColumnStripe(self)->'TableConditionalStyle':
        """
        Gets the conditional style for even column banding.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_EvenColumnStripe.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_EvenColumnStripe.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_EvenColumnStripe,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def TopLeftCell(self)->'TableConditionalStyle':
        """
        Gets the conditional style for the top-left cell.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_TopLeftCell.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_TopLeftCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_TopLeftCell,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def TopRightCell(self)->'TableConditionalStyle':
        """
        Gets the conditional style for the top-right cell.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_TopRightCell.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_TopRightCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_TopRightCell,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def BottomLeftCell(self)->'TableConditionalStyle':
        """
        Gets the conditional style for the bottom-left cell.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_BottomLeftCell.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_BottomLeftCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_BottomLeftCell,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    @property

    def BottomRightCell(self)->'TableConditionalStyle':
        """
        Gets the conditional style  for the last row and last cell.
        """
        GetDllLibDoc().TableConditionalStyleCollection_get_BottomRightCell.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyleCollection_get_BottomRightCell.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyleCollection_get_BottomRightCell,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


