from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class TableStyle (  Style, ITableStyle, IParagraphStyle, ICharacterStyle) :
    """
    Represents a style of table.
    """
    @property

    def ParagraphFormat(self)->'ParagraphFormat':
        """
        Gets the Paragraph format.
        """
        GetDllLibDoc().TableStyle_get_ParagraphFormat.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_ParagraphFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_get_ParagraphFormat,self.Ptr)
        from spire.doc.formatting.ParagraphFormat import ParagraphFormat
        ret = None if intPtr==None else ParagraphFormat(intPtr)
        return ret


    @property

    def CharacterFormat(self)->'CharacterFormat':
        """
        Gets the character format.
        """
        GetDllLibDoc().TableStyle_get_CharacterFormat.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_CharacterFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_get_CharacterFormat,self.Ptr)
        ret = None if intPtr==None else CharacterFormat(intPtr)
        return ret


    @property

    def BaseStyle(self)->'TableStyle':
        """
        Gets the base style of the table style, cast as a TableStyle.
        """
        GetDllLibDoc().TableStyle_get_BaseStyle.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_BaseStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_get_BaseStyle,self.Ptr)
        ret = None if intPtr==None else TableStyle(intPtr)
        return ret


    @property

    def StyleType(self)->'StyleType':
        """
        Gets the type of the style.
        """
        GetDllLibDoc().TableStyle_get_StyleType.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_StyleType.restype=c_int
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_StyleType,self.Ptr)
        objwraped = StyleType(ret)
        return objwraped

    @property

    def HorizontalAlignment(self)->'RowAlignment':
        """
        Gets or sets the horizontal alignment of the table style.
        """
        GetDllLibDoc().TableStyle_get_HorizontalAlignment.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_HorizontalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_HorizontalAlignment,self.Ptr)
        objwraped = RowAlignment(ret)
        return objwraped

    @HorizontalAlignment.setter
    def HorizontalAlignment(self, value:'RowAlignment'):
        GetDllLibDoc().TableStyle_set_HorizontalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibDoc().TableStyle_set_HorizontalAlignment,self.Ptr, value.value)

    @property
    def IsBreakAcrossPages(self)->bool:
        """
        Gets or sets whether the row allows a break across pages.
        """
        GetDllLibDoc().TableStyle_get_IsBreakAcrossPages.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_IsBreakAcrossPages.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_IsBreakAcrossPages,self.Ptr)
        return ret

    @IsBreakAcrossPages.setter
    def IsBreakAcrossPages(self, value:bool):
        GetDllLibDoc().TableStyle_set_IsBreakAcrossPages.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().TableStyle_set_IsBreakAcrossPages,self.Ptr, value)

    @property
    def Bidi(self)->bool:
        """
        Gets or sets the bidirectional text property of the table style.
        """
        GetDllLibDoc().TableStyle_get_Bidi.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_Bidi.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_Bidi,self.Ptr)
        return ret

    @Bidi.setter
    def Bidi(self, value:bool):
        GetDllLibDoc().TableStyle_set_Bidi.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().TableStyle_set_Bidi,self.Ptr, value)

    @property

    def Borders(self)->'Borders':
        """
        Gets the Borders object for table style.
        """
        GetDllLibDoc().TableStyle_get_Borders.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_Borders.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_get_Borders,self.Ptr)
        ret = None if intPtr==None else Borders(intPtr)
        return ret


    @property
    def CellSpacing(self)->float:
        """
        Gets or sets the cell spacing of the table style.
        """
        GetDllLibDoc().TableStyle_get_CellSpacing.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_CellSpacing.restype=c_float
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_CellSpacing,self.Ptr)
        return ret

    @CellSpacing.setter
    def CellSpacing(self, value:float):
        GetDllLibDoc().TableStyle_set_CellSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibDoc().TableStyle_set_CellSpacing,self.Ptr, value)

    @property
    def LeftIndent(self)->float:
        """
        Gets or sets the left indent of the row in points.
        """
        GetDllLibDoc().TableStyle_get_LeftIndent.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_LeftIndent.restype=c_float
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_LeftIndent,self.Ptr)
        return ret

    @LeftIndent.setter
    def LeftIndent(self, value:float):
        GetDllLibDoc().TableStyle_set_LeftIndent.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibDoc().TableStyle_set_LeftIndent,self.Ptr, value)

    @property
    def ColumnStripe(self)->int:
        """
        Gets or sets the column stripe size for the table's style.
        """
        GetDllLibDoc().TableStyle_get_ColumnStripe.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_ColumnStripe.restype=c_long
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_ColumnStripe,self.Ptr)
        return ret

    @ColumnStripe.setter
    def ColumnStripe(self, value:int):
        GetDllLibDoc().TableStyle_set_ColumnStripe.argtypes=[c_void_p, c_long]
        CallCFunction(GetDllLibDoc().TableStyle_set_ColumnStripe,self.Ptr, value)

    @property
    def RowStripe(self)->int:
        """
        Gets or sets the row stripe size, which defines the size of the row stripe in a table's styling.
        """
        GetDllLibDoc().TableStyle_get_RowStripe.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_RowStripe.restype=c_long
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_RowStripe,self.Ptr)
        return ret

    @RowStripe.setter
    def RowStripe(self, value:int):
        GetDllLibDoc().TableStyle_set_RowStripe.argtypes=[c_void_p, c_long]
        CallCFunction(GetDllLibDoc().TableStyle_set_RowStripe,self.Ptr, value)

    @property

    def Shading(self)->'Shading':
        """
        Gets the shading properties of the cell. If no shading is defined, a new Shading instance is created and added to the cell properties.
        """
        GetDllLibDoc().TableStyle_get_Shading.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_Shading.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_get_Shading,self.Ptr)
        ret = None if intPtr==None else Shading(intPtr)
        return ret


    @property

    def Paddings(self)->'Paddings':
        """
        Gets the paddings for the table style.
        """
        GetDllLibDoc().TableStyle_get_Paddings.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_Paddings.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_get_Paddings,self.Ptr)
        from spire.doc.formatting.Paddings import Paddings
        ret = None if intPtr==None else Paddings(intPtr)
        return ret


    @property

    def VerticalAlignment(self)->'VerticalAlignment':
        """
        Gets or sets the vertical alignment of the cell.
        The default value is <see cref="VerticalAlignment.Top"/>
        """
        GetDllLibDoc().TableStyle_get_VerticalAlignment.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_VerticalAlignment.restype=c_int
        ret = CallCFunction(GetDllLibDoc().TableStyle_get_VerticalAlignment,self.Ptr)
        objwraped = VerticalAlignment(ret)
        return objwraped

    @VerticalAlignment.setter
    def VerticalAlignment(self, value:'VerticalAlignment'):
        GetDllLibDoc().TableStyle_set_VerticalAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibDoc().TableStyle_set_VerticalAlignment,self.Ptr, value.value)

    @property

    def ConditionalStyles(self)->'TableConditionalStyleCollection':
        """
        Gets the collection of table conditional styles associated with the table styles.
        """
        GetDllLibDoc().TableStyle_get_ConditionalStyles.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_get_ConditionalStyles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_get_ConditionalStyles,self.Ptr)
        from spire.doc.collections.TableConditionalStyleCollection import TableConditionalStyleCollection
        ret = None if intPtr==None else TableConditionalStyleCollection(intPtr)
        return ret



    def Clone(self)->'TableStyle':
        """
        Creates a deep copy of the current instance.
        """
        GetDllLibDoc().TableStyle_Clone.argtypes=[c_void_p]
        GetDllLibDoc().TableStyle_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().TableStyle_Clone,self.Ptr)
        ret = None if intPtr==None else TableStyle(intPtr)
        return ret


