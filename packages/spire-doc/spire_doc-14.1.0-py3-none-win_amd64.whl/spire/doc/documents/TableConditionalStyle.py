from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class TableConditionalStyle (  DocumentSerializable) :
    """
    Represents a conditional style of table. 
    """
    @property

    def CharacterFormat(self)->'CharacterFormat':
        """
        Gets the character formatting of the table conditional style.
        """
        GetDllLibDoc().TableConditionalStyle_get_CharacterFormat.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_get_CharacterFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyle_get_CharacterFormat,self.Ptr)
        ret = None if intPtr==None else CharacterFormat(intPtr)
        return ret


    @property

    def ParagraphFormat(self)->'ParagraphFormat':
        """
        Gets the paragraph formatting of the table conditional style.
        """
        GetDllLibDoc().TableConditionalStyle_get_ParagraphFormat.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_get_ParagraphFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyle_get_ParagraphFormat,self.Ptr)
        ret = None if intPtr==None else ParagraphFormat(intPtr)
        return ret


    @property

    def Borders(self)->'Borders':
        """
        Gets the collection of default cell borders for the table conditional style.
        """
        GetDllLibDoc().TableConditionalStyle_get_Borders.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyle_get_Borders,self.Ptr)
        ret = None if intPtr==None else Borders(intPtr)
        return ret


    @property

    def Shading(self)->'Shading':
        """
        Gets the shading property for the cell properties.
        """
        GetDllLibDoc().TableConditionalStyle_get_Shading.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_get_Shading.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyle_get_Shading,self.Ptr)
        ret = None if intPtr==None else Shading(intPtr)
        return ret


    @property

    def Paddings(self)->'Paddings':
        """
        Gets the paddings for the cell properties.
        """
        GetDllLibDoc().TableConditionalStyle_get_Paddings.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_get_Paddings.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyle_get_Paddings,self.Ptr)
        ret = None if intPtr==None else Paddings(intPtr)
        return ret


    @property

    def Type(self)->'TableConditionalStyleType':
        """
        Gets the table conditional style type.
        """
        GetDllLibDoc().TableConditionalStyle_get_Type.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibDoc().TableConditionalStyle_get_Type,self.Ptr)
        objwraped = TableConditionalStyleType(ret)
        return objwraped

    @property
    def IsEmpty(self)->bool:
        """
        Gets a value indicating whether the object has no properties set.
        """
        GetDllLibDoc().TableConditionalStyle_get_IsEmpty.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_get_IsEmpty.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().TableConditionalStyle_get_IsEmpty,self.Ptr)
        return ret


    def Clone(self)->'TableConditionalStyle':
        """
        Creates a deep copy of the current TableConditionalStyle instance.
        """
        GetDllLibDoc().TableConditionalStyle_Clone.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableConditionalStyle_Clone,self.Ptr)
        ret = None if intPtr==None else TableConditionalStyle(intPtr)
        return ret


    def ClearFormatting(self):
        """
        Clears all formatting properties.
        """
        GetDllLibDoc().TableConditionalStyle_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibDoc().TableConditionalStyle_ClearFormatting,self.Ptr)

    def GetHashCode(self)->int:
        """
        Calculates hash code for this object.
        """
        GetDllLibDoc().TableConditionalStyle_GetHashCode.argtypes=[c_void_p]
        GetDllLibDoc().TableConditionalStyle_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibDoc().TableConditionalStyle_GetHashCode,self.Ptr)
        return ret


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current object.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibDoc().TableConditionalStyle_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibDoc().TableConditionalStyle_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().TableConditionalStyle_Equals,self.Ptr, intPtrobj)
        return ret

