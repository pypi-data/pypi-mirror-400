"""Module consisting of class object for stock list.
"""

import os as _os
import datetime as _dtm
import numpy as _np
import pandas as _pd

from .utils import *

from typing import TypeVar, Union

from .stock_base import Stock



class StockList:
    """Class to handle the dunctionalities related to multiple stocks.
    """

    def __init__(self, stocklist:list[Stock]) -> None:
        """generates the StockList class

        Parameters
        ----------
        stocklist : list[Stock]
            list of already initialized Stock objects.
        """

        self.sl1 = stocklist
        self.scrip = _pd.DataFrame()
        for s1 in self.sl1:
            self.scrip = _pd.concat([self.scrip, s1.scrip])

    def __repr__(self) -> str:
        return f'StockList object with {len(self.sl1)} Stocks'
    
    def __type__(self) -> str:
        return 'StockList'

    def __getitem__(self, index):
        return self.sl1[index]
    
    def __len__(self):
        return len(self.sl1)
    
    

