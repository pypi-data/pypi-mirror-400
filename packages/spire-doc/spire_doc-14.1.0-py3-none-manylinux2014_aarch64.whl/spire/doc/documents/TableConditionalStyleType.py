from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class TableConditionalStyleType(Enum):
    """
    Represents the different types of conditional formatting styles that can be applied to a table.
    Each style type defines a specific region or row/column in the table (e.g., first row, odd rows, corner cells).
    These types are used to map conditional formatting rules to specific parts of the table layout.
    """
    
    #Applies conditional formatting to odd-numbered rows.
    #This is typically used for alternating row stripe formatting (e.g. light gray background on odd rows).
    OddRowStripe = 0
    
    #Applies conditional formatting to odd-numbered columns.
    #This is typically used for alternating column stripe formatting (e.g. light gray background on odd columns).
    OddColumnStripe = 1
    
    #Applies conditional formatting to even-numbered rows.
    #This is typically used for alternating row stripe formatting (e.g. light gray background on even rows).
    EvenRowStripe = 2
    
    #Applies conditional formatting to even-numbered columns.
    #This is typically used for alternating column stripe formatting (e.g. light gray background on even columns).
    EvenColumnStripe = 3
    
    #Applies conditional formatting to the first column of the table.
    FirstColumn = 4
    
    #Applies conditional formatting to the first row of the table.
    FirstRow = 5
    
    #Applies conditional formatting to the last column of the table.
    LastColumn = 6
    
    #Applies conditional formatting to the last row of the table.
    LastRow = 7
    
    #Applies conditional formatting to the top-right corner cell of the table.
    #This style targets the cell at the intersection of the first row and last column.
    TopRightCell = 8
    
    #Applies conditional formatting to the top-left corner cell of the table.
    #This style targets the cell at the intersection of the first row and first column.
    TopLeftCell = 9
    
    #Applies conditional formatting to the bottom-right corner cell of the table.
    #This style targets the cell at the intersection of the last row and last column.
    BottomRightCell = 10
    
    #Applies conditional formatting to the bottom-left corner cell of the table.
    #This style targets the cell at the intersection of the last row and first column.
    BottomLeftCell = 11

