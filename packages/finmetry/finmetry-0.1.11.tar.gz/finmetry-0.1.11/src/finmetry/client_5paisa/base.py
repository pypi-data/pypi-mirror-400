"""
This module contains the objects related to 5paisa client

@author: Rathod Darshan
"""


import os as _os
import py5paisa as _p5
import pandas as _pd
import websocket as _ws
import datetime as _dtm
import json as _json
from websocket import create_connection as _create_connection
import websocket as _websocket
from py5paisa.order import Order as _Order
from typing import Union


from .utils import *

from ..stock_base import Stock
from ..stock_list import StockList


class ScripMaster:
    """ScripMaster contains all the scipts of 5paisa client.

    To get the name and symbol of any script, this class needs to be accessed. This class just filters the data from single .csv.
    """

    def __init__(self, filepath: str = None) -> None:
        """Initializes the ScripMaster class.

        Loads the .csv file into data attribute.

        Parameters
        ----------
        filepath : str, optional
            filepath to .csv file. If filepath is given then it reads the file, else it will download the file. by default None
        """
        if filepath is not None:
            self.data = _pd.read_pickle(filepath)
        else:
            self.data = _pd.read_csv(
                "https://images.5paisa.com/website/scripmaster-csv-format.csv"
            )

        self.data["Expiry"] = _pd.to_datetime(
            self.data["Expiry"], format="%Y-%m-%d %H:%M:%S"
        )
        self.data["Name"] = self.data["Name"].apply(str.upper)
        self.data["Symbol"] = self.data["Name"]

    def __repr__(self):
        return f"scrip master data"

    def __call__(self):
        return self.data

    def save(self, filepath: str) -> None:
        """saves the scrip master data

        Parameters
        ----------
        filepath : str
            filepath with filename with .pkl extention

        Returns
        -------
        _type_
            None
        """
        return self.data.to_pickle(filepath)

    def get_scrip(self, stocklist: Union[list[Stock] , StockList]) -> _pd.DataFrame:
        """returns the scrips for list of stocks

        Parameters
        ----------
        stocklist : list[Stock]|StockList
            list of stocks or StockList type object

        Returns
        -------
        _pd.DataFrame
            Scrip data for given list of stocks.
        """
        try:
            return stocklist.scrip
        except:
            ls1 = []
            for s1 in stocklist:
                try:
                    ls1.append(s1.scrip)
                except:
                    d1 = self.data
                    f1 = (
                        (d1["Exch"] == s1.exchange)
                        & (d1["ExchType"] == s1.exchange_type)
                        & (d1["Symbol"] == s1.symbol)
                    )
                    f2 = (d1["Series"] == "EQ") | (d1["Series"] == "XX")
                    d2 = d1[f1 & f2]
                    if d2.empty:
                        raise ValueError(
                            f"No Scrip found for {s1.symbol} in scrip_master"
                        )
                    d2 = d2.set_index("Name")
                    s1.scrip = d2
                    ls1.append(d2)
            return _pd.concat(ls1)


class Client5paisa(_p5.FivePaisaClient):
    def __init__(
        self,
        loggedin_client: _p5.FivePaisaClient = None,
        email: str = None,
        password: str = None,
        dob: str = None,
        cred: dict = None,
        scrip_master: ScripMaster = None,
    ) -> None:
        """Logs into the 5paisa client.

        Parameters
        ----------
        email : str
            registered email id of the user
        password : str
            password of the user
        dob : str
            date of birth in "YYYYMMDD" format
        cred : dict
            user developer API credentials. can be found on https://tradestation.5paisa.com/apidoc
            First login to 5paisa. And in menu -> Developer's API -> Get API keys. API credentials can be found.
        scrip_master : ScripMaster
            ScripMaster instance. This will be used for generating required inputs for various data fatching methods.
        loggedin_client : _p5.FivePaisaClient
            If this is provided then this will be used as a super class.
            If True then you have to go to URL and input the response URL. By default False.
        """
        if loggedin_client is not None:
            self.__dict__ = loggedin_client.__dict__.copy()
        else:
            print('This is now depreciated method. However, if you want to use this then get py5paisa=0.7.0')
            _p5.FivePaisaClient.__init__(
                self, email=email, passwd=password, dob=dob, cred=cred
            )
            self.login()
            self.ws_feed = _create_connection(self._web_url1)

        self.scrip_master = scrip_master

    def __check_scrip_master(self) -> bool:
        """Checks if scrip_master is provided

        Returns
        -------
        bool
            True, if scrip_master is provided.

        Raises
        ------
        TypeError
            If scrip_master is None.
        """
        if self.scrip_master is None:
            raise TypeError(
                "scrip_master is None. Please provide ScripMaster instance."
            )
        else:
            return True

    def download_historical_data(
        self,
        stocklist: Union[list[Stock] , StockList],
        interval: str = "1d",
        start: Union[str, _dtm.datetime] = "2023-01-01",
        end: Union[str, _dtm.datetime] = "2023-03-30",
        overwrite: bool = False,
    ) -> None:
        """Downloads the historical data and saves it to local drive or in Stock.data variable.

        Parameters
        ----------
        stocklist : list[Stock]|StockList
            list of Stocks or StockList type object
        interval : str, optional
            time interval of data. it should be within [1m,5m,10m,15m,30m,60m,1d], by default "1d"
        start : Union[str, _dtm.datetime], optional
            start date of the data. The data for this date will be downloaded, by default "2023-01-01"
        end : Union[str, _dtm.datetime], optional
            end date of the data. The data for this date will be downloaded, by default "2023-03-30"
        overwrite : bool
            wheather to overwrite the existing file or just append the new data. default False. If True then it will overwrite the present data.
        """
        self.__check_scrip_master()
        scrip = self.scrip_master.get_scrip(stocklist)

        if type(start) is not str:
            start = start.strftime("%Y-%m-%d")
        if type(end) is not str:
            end = end.strftime("%Y-%m-%d")

        for s1 in stocklist:
            print(s1.symbol)
            df = self.historical_data(
                s1.exchange,
                s1.exchange_type,
                scrip.loc[s1.symbol, "Scripcode"],
                interval,
                start,
                end,
                )
            df.columns = ["Datetime", "Open", "High", "Low", "Close", "Volume"]
            df["Datetime"] = _pd.to_datetime(df["Datetime"])
            df = df.set_index("Datetime")
            ### saving
            s1.save_historical_data(
                df,
                interval=interval,
                overwrite=overwrite
            )

    @property
    def _web_url1(self):
        return f"wss://openfeed.5paisa.com/Feeds/api/chat?Value1={self.Jwt_token}|{self.client_code}"

    def get_market_depth(self, stocklist: Union[list[Stock] , StockList]) -> _pd.DataFrame:
        """Gets the market depth for given list of Stocks

        Parameters
        ----------
        stocklist : list[Stock]|StockList
            list of Stock class instances or StockList type object.

        Returns
        -------
        _pd.DataFrame
            Live Market Depth for all the Stocks in list.
        """
        a = self.scrip_master.get_scrip(stocklist)
        syms = a["Symbol"].values

        a = a.rename(columns={"Exch": "Exchange", "ExchType": "ExchangeType"})[["Exchange", "ExchangeType", "Symbol"]].to_dict(orient="records")
        d1 = _pd.DataFrame(self.fetch_market_depth_by_symbol(a)["Data"])

        # a = a.rename(
        #     columns={
        #         "Exch": "Exchange",
        #         "ExchType": "ExchangeType",
        #         "Scripcode": "ScripCode",
        #     }
        # )[["Exchange", "ExchangeType", "ScripCode"]].to_dict(orient="records")
        # d1 = _pd.DataFrame(self.fetch_market_depth(a)["Data"])

        d1["Datetime"] = _dtm.datetime.now()
        d1["Symbol"] = syms
        return d1

    def get_market_feed(self, stocklist: Union[list[Stock], StockList]) -> _pd.DataFrame:
        """Gets the market feed for given list of Stocks

        Parameters
        ----------
        stocklist : list[Stock]|StockList
            list of Stock class instances or StockList type object.

        Returns
        -------
        _pd.DataFrame
            Live Market Feed for all the Stocks in list.
        """
        # a = self.scrip_master.get_scrip(stocklist)
        # a = a[["Exch", "ExchType", "Symbol"]].to_dict(orient="records")
        # d1 = _pd.DataFrame(self.fetch_market_feed(a)["Data"])
        # d1["Datetime"] = _dtm.datetime.now()

        a = self.scrip_master.get_scrip(stocklist).rename(columns={"Scripcode": "ScripCode"})
        a = a[["Exch", "ExchType", "ScripCode"]].to_dict(orient="records")
        step = 50
        d1 = [_pd.DataFrame(self.fetch_market_feed_scrip(a[i:i+step])['Data']) for i in range(0,len(a),step)]
        d1 = _pd.concat(d1)
        d1["Datetime"] = _dtm.datetime.now()

        return d1

    def get_market_data(
        self, stocklist: Union[list[Stock] , StockList], feed_type: str = "md"
    ) -> _pd.DataFrame:
        """Fetches the market data.

        The data fetched contains bid and offer qty and prices, depending upon the type of data requested.

        Parameters
        ----------
        stocklist : list[Stock]|StockList
            list of Stocks or StockList type object
        feed_type : str, optional
            'md' or 'mf'. 'md' gives 5 depth but not LTP. 'mf' gives only single depth and LTP., by default 'md'

        Returns
        -------
        _pd.DataFrame
            Data
        """
        a = self.scrip_master.get_scrip(stocklist)
        a = a.rename(columns={"Scripcode": "ScripCode"})[
            ["Exch", "ExchType", "ScripCode"]
        ].to_dict(orient="records")
        mf_list = self.Request_Feed(feed_type, "s", a)

        self.ws_feed = _create_connection(self._web_url1)
        self.ws_feed.send(_json.dumps(mf_list))
        d1 = ""
        if feed_type == "md":
            for s in mf_list["MarketFeedData"]:
                d1 = d1 + ",{" + self.ws_feed.recv()[1:-1] + "}"
        if feed_type == "mf":
            for s in mf_list["MarketFeedData"]:
                d1 = d1 + "," + self.ws_feed.recv()[1:-1]
        self.ws_feed.close()
        d1 = "[" + d1[1:] + "]"
        return _pd.DataFrame(_json.loads(d1))

    def get_option_expiry(self, sym: str = "BANKNIFTY") -> _pd.DataFrame:
        """gets the option expiry for given symbol.

        Parameters
        ----------
        sym : str
            As the expiry for various options are different. You need to give symbol for which the expiry is required.

        Returns
        -------
        _pd.DataFrame
            Option expiry dates

        """
        d1 = self.get_expiry("N", sym)
        d1 = _pd.DataFrame(d1["Expiry"])
        d1["Timestamp"] = d1["ExpiryDate"].apply(
            lambda x: int(x.split("+")[0].split("(")[-1])
        )
        d1["Date"] = d1["Timestamp"].apply(lambda x: _dtm.date.fromtimestamp(x // 1000))
        return d1

    def get_option_chain(
        self,
        stock: Stock,
        expiry_date: Union[str, _dtm.datetime],
        update: bool = True,
        n_strikes: int = None,
    ) -> _pd.DataFrame:
        """gets the option chain data for the given stock

        Parameters
        ----------
        stock : Stock
            Stock
        expiry_date : Union[str, _dtm.datetime]
            expiry date of option chain
        update : bool, optional
            whether to update the option chain at local folder
        n_strikes : int, optional
            till what ITM and OTM depth the option chain is required. If None then full depth is returned. By default, full depth is returned. If n_strikes = 5, then 5 ITm and 5 OTM including ATM option chain is returned.

        Returns
        -------
        _pd.DataFrame
            option chain data
        """
        if type(expiry_date) is str:
            expiry_date = _dtm.datetime.strptime(expiry_date, "%Y-%m-%d").date()
        d1 = self.get_option_expiry(sym=stock.symbol)
        f1 = d1["Date"] == expiry_date
        ts = d1[f1]["Timestamp"].iloc[0]
        d2 = _pd.DataFrame(
            super().get_option_chain(stock.exchange, stock.symbol, ts)["Options"]
        )

        if n_strikes is not None:
            strike_rates = d2["StrikeRate"].unique()
            strike_rates.sort()
            ltp = self.get_market_depth([stock])["LastTradedPrice"].iloc[0]

            f1 = strike_rates <= ltp
            strike_rates1 = list(strike_rates[f1][-n_strikes:])
            f1 = strike_rates > ltp
            strike_rates1 += list(strike_rates[f1][:n_strikes])

            f1 = (d2["StrikeRate"] <= max(strike_rates1)) & (
                d2["StrikeRate"] >= min(strike_rates1)
            )
            d2 = d2[f1]

        if update:
            stock.option_chain = d2
        return d2
