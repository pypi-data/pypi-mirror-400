from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc
import enum

class TableStyleOptions(enum.IntFlag):
    """
    Defines available table style options for formatting tables in a document.
    Each option represents a specific formatting behavior applied to rows, columns, or the entire table.
    """

    #No table style formatting is applied.
    none = 0
    #Applies conditional formatting to the first row.
    FirstRow = 32
    #Applies conditional formatting to the last row.
    LastRow = 64
    #Applies conditional formatting to the first column.
    FirstColumn = 128
    #Applies conditional formatting to the last column.
    LastColumn = 256
    #Applies row striping (alternating row colors) for visual distinction.
    RowStripe = 512
    #Applies column striping (alternating column colors) for visual distinction.
    ColumnStripe = 1024
    #Applies both row and column striping. This mimics Microsoft Word default behavior for older formats (DOC, WML, RTF).
    Default2003 = RowStripe | ColumnStripe
    #Applies Microsoft Word default table style: first row, first column, and row striping.
    Default = FirstRow | FirstColumn | RowStripe

