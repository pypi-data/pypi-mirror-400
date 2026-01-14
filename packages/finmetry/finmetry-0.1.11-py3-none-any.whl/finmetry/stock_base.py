"""Module consisting of base class of stock
"""

import os as _os
import datetime as _dtm
import numpy as _np
import pandas as _pd

from .utils import *

from typing import TypeVar, Union


class Stock:
    def __init__(
        self,
        symbol: str,
        exchange: str = "N",
        exchange_type: str = "C",
        store_local: bool = False,
        local_data_foldpath: str = None,
    ) -> None:
        """Manages the data for list of stocks.

        Parameters
        ----------
        Parameters
        ----------
        symbol : str
            Stock symbol as available online.
        exchange : str
            Stock Exchange. can be N, B, M for Nifty, BSE and MCX respectively. By default N
        exchange_type : str
            Type of Stock Exchange. can be C, D or U for Cash, Derivative or Currency respectively. By default C.
        store_local : bool, optional
            whether to store the historical or any downloaded data to local directory, by default True
        local_data_foldpath : str, optional
            path to folder where local data will be stored. Inside this folder, multiple folders of individual stocks are created and inside that stock folder, historical data and other data is stored. If None then path returned by _os.getcwd() is used, given that store_local is True. by default None
        """
        self.symbol = symbol
        if exchange in ["N", "B", "M"]:
            self.exchange = exchange
        else:
            raise ValueError(
                'exchange can be only "N" for Nifty, "B" for BSE or "M" for MCX, in Upper case.'
            )

        if exchange_type in ["C", "D", "U"]:
            self.exchange_type = exchange_type
        else:
            raise ValueError(
                'exchange_type can be only "C" for Cash or "D" for Derivative, in Upper case.'
            )

        self.foldname = self.exchange + "_" + self.exchange_type + "_" + self.symbol
        self.store_local = store_local
        if self.store_local:
            if local_data_foldpath is not None:
                self.local_data_foldpath = _os.path.join(
                    local_data_foldpath, self.foldname
                )
            else:
                self.local_data_foldpath = _os.path.join(_os.getcwd(), self.foldname)
            make_dir(self.local_data_foldpath)

    def __repr__(self):
        return f"{self.symbol} stock class"

    def save_historical_data(
        self,
        data: _pd.DataFrame,
        interval: str,
        overwrite:bool=False,
    ) -> None:
        """saves the historical stock data.

        Multiple files, each for saparate month data is created.

        Parameters
        ----------
        data : _pd.DataFrame
            Data to be saved.
        interval : str
            time interval of the data
        overwrite : bool
            wheather to overwrite the existing file or just append the new data. default False. If True then it will overwrite the present data.
        """
        self.data = data

        if self.store_local is False:
            return data

        start_time = data.index[0]
        end_time = data.index[-1]

        for y in range(start_time.year, end_time.year + 1):
            f1 = data.index.year == y
            data1 = data[f1]
            st1 = data1.index[0]
            se1 = data1.index[-1]
            for m in range(st1.month, se1.month + 1):
                f1 = data1.index.month == m
                data2 = data1[f1]
                filename = f"{y}{str(m).zfill(2)}_{interval}.pickle"
                filepath = _os.path.join(self.local_data_foldpath, filename)
                if overwrite:
                    print('Overwriting:-',filepath)
                    data.to_pickle(filepath)
                else:
                    append_it(data2, filepath=filepath)
        return

    def load_historical_data(
        self,
        interval: str,
        start: Union[str, _dtm.datetime],
        end: Union[str, _dtm.datetime],
        append_pseudo_data: bool = False,
    ) -> _pd.DataFrame:
        """Loads the data from local_directory

        Parameters
        ----------
        interval : str
            time interval of data. it should be within [1m,5m,10m,15m,30m,60m,1d]
        start : Union[str, _dtm.datetime]
            start date of the data. The data for this date will be downloaded
        end : Union[str, _dtm.datetime]
            end date of the data. The data for this date will be downloaded
        append_pseudo_data : bool, Default is False
            It appends extra data for any day on which the data is not available. Say for Feb, there is no 31/02....so if this argument is True then the data for this date is created by copying the same data of the previous available date.

        Returns
        -------
        _pd.DataFrame
            data

        Raises
        ------
        ValueError
            if no data is found
        """

        if type(start) is str:
            start = _dtm.datetime.strptime(start, "%Y-%m-%d")
        if type(end) is str:
            end = _dtm.datetime.strptime(end, "%Y-%m-%d")

        ### converting the date to specific integer for comparision
        start_val = start.year * 100 + start.month
        end_val = end.year * 100 + end.month
        ### data of each month will be stored here
        datas = []
        ### the value of each month will be stored. This is done to sort the data in ascending order. Sorting can be performed here directly instead over the large dataframe.
        dates = []
        files = get_file_name(self.local_data_foldpath)
        for fname in files:
            if interval in fname:
                nm = fname.split("_")
                dt1 = _dtm.datetime.strptime(nm[0], "%Y%m")
                dt_val = dt1.year * 100 + dt1.month
                ### if this integer lies between the start and end date integer then read this file.
                if (dt_val >= start_val) and (dt_val <= end_val):
                    data1 = _pd.read_pickle(_os.path.join(self.local_data_foldpath, fname))
                    datas.append(data1)
                    dates.append(dt_val)

        if dates == []:
            raise ValueError("No data found in given time period or time frame")

        ### sorting and concatenating
        dates = _np.array(dates)
        idx = _np.argsort(dates)
        ans = _pd.DataFrame()
        for i in idx:
            ans = _pd.concat([ans, datas[i]])

        ### after this the data will be filtered with date
        f1 = (ans.index.date >= start.date()) & (ans.index.date <= end.date())
        return ans[f1]
    

    @property
    def scrip_filepath(self) -> str:
        """filepath of scrip

        Returns
        -------
        str
            filepath
        """
        return _os.path.join(self.local_data_foldpath, "scrip.pickle")

    @property
    def scrip(self) -> _pd.DataFrame:
        """scrip for client 5paisa.

        Returns
        -------
        _pd.DataFrame
            scrip data.
        """
        if self.store_local:
            return _pd.read_pickle(self.scrip_filepath)
        else:
            return self._scrip

    @scrip.setter
    def scrip(self, data: _pd.DataFrame) -> None:
        """saves the scrip

        Parameters
        ----------
        data : _pd.DataFrame
            scrip data. This can be optained by ScripMaster.get_scrip() method.
        """
        if self.store_local:
            data.to_pickle(self.scrip_filepath)
        else:
            self._scrip = data
        return

    @property
    def option_chain_filepath(self) -> str:
        """filepath of option chain

        Returns
        -------
        str
            filepath
        """
        return _os.path.join(self.local_data_foldpath, "option_chain.pickle")

    @property
    def option_chain(self) -> _pd.DataFrame:
        """option chain for stock

        Returns
        -------
        _pd.DataFrame
            scrip data.
        """
        return _pd.read_pickle(self.option_chain_filepath)

    @option_chain.setter
    def option_chain(self, data: _pd.DataFrame) -> None:
        """saves the option chain

        Parameters
        ----------
        data : _pd.DataFrame
            option_chain data.
        """
        if self.store_local:
            data.to_pickle(self.option_chain_filepath)
        return

    ############################################################################################
    ############################################################################################
    ############################################################################################
    ### market depths related functions

    @property
    def available_market_depths(self) -> list[str]:
        """gets the dates of available market depths data. The returned dates are in the form YYYYMMDD.

        Returns
        -------
        list[str]
            list of dates.
        """
        dates = []
        files = get_file_name(self.local_data_foldpath)
        for fname in files:
            if "market_depth" in fname:
                nm = fname.split("_")
                dates.append(nm[0])
        return dates

    def load_market_depths(self, dates: list[str]) -> _pd.DataFrame:
        """returns the market_depth data for provided list of dates in single pandas dataframe. The dates should be in YYYYMMDD format.

        Parameters
        ----------
        dates : list[str]
            list of dates for market depths data. Dates for available data can be obtained from available_market_depths property.

        Returns
        -------
        _pd.DataFrame
            market_depth data
        """
        dt_int = [int(x) for x in dates]
        dt_int.sort(reverse=False)
        ans = _pd.DataFrame()
        for dt in dt_int:
            fname = str(dt) + "_market_depth.pickle"
            fpath = _os.path.join(self.local_data_foldpath, fname)
            ans = _pd.concat([ans, _pd.read_pickle(fpath)])
        return ans

    @property
    def available_expiries(self) -> dict:
        """returns the expiry dates for which the market depth data is available. Also gives the dates of market_depths for those expiry.

        Returns
        -------
        dict
            key indicates the expiry date and list of values indicated the available market_depth dates.
        """
        nms = get_dir_name(self.local_data_foldpath)
        exps = []
        for nm in nms:
            if f"N_D_{self.symbol}" in nm:
                exp = " ".join(nm.split(" ")[1:4])
                if exp not in exps:
                    exps.append(exp)

        ans = {}
        for exp in exps:
            dates = []
            for nm in nms:
                if exp in nm:
                    fp1 = _os.path.join(self.local_data_foldpath, nm)
                    fnames = get_file_name(fp1)
                    for fname in fnames:
                        if "market_depth" in fname:
                            nm = fname.split("_")
                            if nm[0] not in dates:
                                dates.append(nm[0])
            ans[exp] = dates
        return ans

    def load_op_data(
        self, date: str, expiry: str
    ) -> tuple[_pd.DataFrame, _pd.DataFrame, _pd.DataFrame]:
        """loads the market_depths_data for all strikes for given date and expiry.

        The user has to check the available date and expiry for the underlying from self.available_expiries and then provide the according combination of date and expiry.

        Parameters
        ----------
        date : str
            date in YYYYMMDD format
        expiry : str
            expiry in DD MON YYYY format. eg. 10 AUG 2023.

        Returns
        -------
        _pd.DataFrame, _pd.DataFrame, _pd.DataFrame
            underlying, CE and PE data respectively
        """
        nms = get_dir_name(self.local_data_foldpath)
        ans_ce = {}
        ans_pe = {}
        # ans[self.symbol] = self.load_market_depths(dates=[date])
        for nm in nms:
            if expiry in nm:
                fp1 = _os.path.join(self.local_data_foldpath, nm)
                f_nms = get_file_name(fp1)
                for fnms in f_nms:
                    if date in fnms:
                        fp2 = _os.path.join(fp1, fnms)
                        op_name = nm.split(" ")
                        strike = float(op_name[-1])
                        if op_name[-2] == "CE":
                            ans_ce[strike] = _pd.read_pickle(fp2)
                        elif op_name[-2] == "PE":
                            ans_pe[strike] = _pd.read_pickle(fp2)

        ### only appending those strikes where full data is available.
        shapes1 = []
        for ky in ans_ce:
            shapes1.append(ans_ce[ky].shape[0])
        shape1 = max(shapes1)
        ans_ce1 = {}
        for ky in ans_ce:
            if ans_ce[ky].shape[0] == shape1:
                ans_ce1[ky] = ans_ce[ky]

        shapes1 = []
        for ky in ans_pe:
            shapes1.append(ans_pe[ky].shape[0])
        shape1 = max(shapes1)
        ans_pe1 = {}
        for ky in ans_pe:
            if ans_pe[ky].shape[0] == shape1:
                ans_pe1[ky] = ans_pe[ky]

        
        d1_CE = _pd.concat(ans_ce1.values(), axis=1, keys=ans_ce1.keys()).swaplevel(
            0, axis=1
        )
        d1_PE = _pd.concat(ans_pe1.values(), axis=1, keys=ans_pe1.keys()).swaplevel(
            0, axis=1
        )

        bnf = self.load_market_depths(dates=[date])
        d1_CE["OpenInterest"] = d1_CE["OpenInterest"].astype("int")
        d1_PE["OpenInterest"] = d1_PE["OpenInterest"].astype("int")
        for ky in d1_CE["LastTradedPrice"].keys():
            strike = ky
            arr1 = bnf["LastTradedPrice"] - strike
            f1 = arr1 < 0
            arr1[f1] = 0
            d1_CE["BasicValue", ky] = arr1
            d1_CE["ExpectedValue", ky] = d1_CE["LastTradedPrice", ky] - arr1

            arr1 = strike - bnf["LastTradedPrice"]
            f1 = arr1 < 0
            arr1[f1] = 0
            d1_PE["BasicValue", ky] = arr1
            d1_PE["ExpectedValue", ky] = d1_PE["LastTradedPrice", ky] - arr1
        self.bnf, self.d1_CE, self.d1_PE = bnf.sort_index(), d1_CE.sort_index(), d1_PE.sort_index()
        return self.bnf, self.d1_CE, self.d1_PE
