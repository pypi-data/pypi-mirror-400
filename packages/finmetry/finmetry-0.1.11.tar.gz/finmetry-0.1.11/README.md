# Finmetry

This is the project on stock market data analysis using modern data anlysis tools, AI and ML.

In depth tests on various stock market tools are conducted.

# Importing and initiating


```python
%load_ext autoreload

%autoreload 2
import finmetry as fm

import pandas as pd
pd.set_option('display.max_rows', 5)
pd.set_option('display.max_columns', 20)
import numpy as np
import datetime as dtm
```

The API has `Stock` class which helps in managing the data related to any security. Clients are classes of various data providing external libraries such as `py5paisa, yfinance ` etc. finmetry API has the class based of the python API of such external libraries for ease of use with `Stock` class. This version of finmetry is mainly developed around client `py5paisa`, as it provieds enough data for in-depth market analysis.

## Initializing Stock

`Stock` class API provides handy tools for managing various data provided by clients. The `Stock` instance is provided to various clients which will then download the data for those stocks. There are multiple clients which provide variety of data on security. Further information on these can be found on specific module or through help of specific methods. The information about intializing Client5paisa can be found [here](#Client5paisa).

The `Stock` class consists of various methods to get historical data and managing the local storage of data. If the `store_local` is `False` then no local storage is done. It is advisable to keep a folder for market data which can be provided to `Stock` class for proper handling. Also, if the historical data is already downloaded then this helps in directly accesing offline data instead of downloading it again.


```python
from finmetry import Stock

market_foldpath = r"D:\Finmetry\local_data"

s1 = Stock(
    symbol="RELIANCE",
    exchange="N",
    exchange_type="C",
    store_local=True,
    local_data_foldpath=market_foldpath,
)
```

As `store_local = True`, Folder with name `RELIANCE` is created. Now all the historical and other types of data will be stored in this folder. If there is already some historical data downloaded then API would directly access that data.

## <a id="Client5paisa"></a>Intitalizing Client5paisa

`Client5paisa` is the class derived from `py5paisa.FivePaisaClient`. This is done to ease the data handling process.

First, we will initialize `Client5paisa` which will be used for data downloading for various stocks. For this the user needs 5paisa account and the API keys. User can refer to [py5paisa](https://github.com/5paisa/py5paisa) for further details on getting API credentials. User need, API credentials (`cred`), email-id (`email`), password (`password`) of 5paisa account and date of birth (`dob`). Here, the credentials are already loaded on variables and not shown for security reasons.


```python
c_5p = fm.client_5paisa.Client5paisa(email=email, password=password, dob=dob, cred=cred)
```

     19:32:23 | Logged in!!
    

### ScripMaster

py5paisa provides the .csv file containing symbols and other information of majority of the Indian securities. The file is around 40Mb (while writing this and may vary in future) which may take about few seconds to download depending upon the internet speed. It is advisable to save it offline and use that .csv again for faster intialization. The local file should be updated often for any changes in .csv file, if any.

#### Downloading the file


```python
scrip_master = fm.client_5paisa.ScripMaster()
```

#### Save the file locally


```python
scrip_master_filepath = r"D:\Finmetry\local_data\scrip_master.csv"
scrip_master.save(scrip_master_filepath)
```

#### Loading from local file


```python
scrip_master_filepath = r"D:\Finmetry\local_data\scrip_master.csv"
scrip_master = fm.client_5paisa.ScripMaster(filepath=scrip_master_filepath)
scrip_master.data
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Exch</th>
      <th>ExchType</th>
      <th>Scripcode</th>
      <th>Name</th>
      <th>Series</th>
      <th>Expiry</th>
      <th>...</th>
      <th>Multiplier</th>
      <th>Underlyer</th>
      <th>Root</th>
      <th>TickSize</th>
      <th>CO BO Allowed</th>
      <th>Symbol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>B</td>
      <td>C</td>
      <td>199117</td>
      <td>SETFN50INAV</td>
      <td>EQ</td>
      <td>1980-01-01 00:00:00</td>
      <td>...</td>
      <td>1</td>
      <td>NaN</td>
      <td>SETFN50INAV</td>
      <td>0.01</td>
      <td>N</td>
      <td>SETFN50INAV</td>
    </tr>
    <tr>
      <th>1</th>
      <td>B</td>
      <td>C</td>
      <td>199118</td>
      <td>MOHEALTINAV</td>
      <td>EQ</td>
      <td>1980-01-01 00:00:00</td>
      <td>...</td>
      <td>1</td>
      <td>NaN</td>
      <td>MOHEALTINAV</td>
      <td>0.01</td>
      <td>N</td>
      <td>MOHEALTINAV</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>202732</th>
      <td>M</td>
      <td>D</td>
      <td>256029</td>
      <td>NATURALGAS 23 JUN 2023 CE 130.00              ...</td>
      <td></td>
      <td>2023-06-23 23:59:59</td>
      <td>...</td>
      <td>1</td>
      <td>23 Jun 2023</td>
      <td>NATURALGAS</td>
      <td>0.05</td>
      <td>Y</td>
      <td>NATURALGAS 23 JUN 2023 CE 130.00              ...</td>
    </tr>
    <tr>
      <th>202733</th>
      <td>M</td>
      <td>D</td>
      <td>256030</td>
      <td>NATURALGAS 23 JUN 2023 PE 130.00              ...</td>
      <td></td>
      <td>2023-06-23 23:59:59</td>
      <td>...</td>
      <td>1</td>
      <td>23 Jun 2023</td>
      <td>NATURALGAS</td>
      <td>0.05</td>
      <td>Y</td>
      <td>NATURALGAS 23 JUN 2023 PE 130.00              ...</td>
    </tr>
  </tbody>
</table>
<p>202734 rows × 20 columns</p>
</div>



User can repeat the process of downloading and saving to update the local file. This `scrip_master` will be used for generating various inputs for data fatching methods. The `Exch, ExchType, Scripcode` are some of the parameters required to get the market data of various securities. Hence this `scrip_master` should be provided to client_5paisa instance (i.e, `c_5p`).

#### Provide scrip_master to Client5paisa


```python
c_5p.scrip_master = scrip_master
```

User can also provide the `scrip_master` instance during initialization of `Client5paisa` class.


```python
c_5p = fm.client_5paisa.Client5paisa(
    email=email, password=password, dob=dob, cred=cred, scrip_master=scrip_master
)
```

## Historical data

Historical data for list of stocks can be downloaded using `c_5p.download_historical_data`. If `Stock.store_local is True` then the data will be stored locally with separate file for each months data.


```python
syms = ["RELIANCE", "ITC", "TCS"]
sl1 = []
for sym in syms:
    s1 = Stock(
        symbol=sym.upper(),
        exchange="N",
        exchange_type="C",
        store_local=True,
        local_data_foldpath=market_foldpath,
    )
    sl1.append(s1)
```


```python
c_5p.download_historical_data(
    stocklist=sl1, interval="1m", start="2019-04-1", end="2019-04-30"
)
```

### Accessing local data

Stock class has the method to access the data stored locally.


```python
s1 = sl1[0]
data = s1.load_historical_data(interval="1m", start="2019-04-1", end="2019-04-30")
data
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Open</th>
      <th>High</th>
      <th>Low</th>
      <th>Close</th>
      <th>Volume</th>
    </tr>
    <tr>
      <th>Datetime</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2019-04-01 09:15:00</th>
      <td>1371.00</td>
      <td>1373.15</td>
      <td>1369.50</td>
      <td>1370.10</td>
      <td>73889</td>
    </tr>
    <tr>
      <th>2019-04-01 09:16:00</th>
      <td>1370.30</td>
      <td>1370.75</td>
      <td>1368.90</td>
      <td>1369.00</td>
      <td>45357</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2019-04-30 15:29:00</th>
      <td>1392.15</td>
      <td>1393.00</td>
      <td>1391.00</td>
      <td>1393.00</td>
      <td>33141</td>
    </tr>
    <tr>
      <th>2019-04-30 15:30:00</th>
      <td>1392.45</td>
      <td>1392.45</td>
      <td>1392.45</td>
      <td>1392.45</td>
      <td>25</td>
    </tr>
  </tbody>
</table>
<p>7137 rows × 5 columns</p>
</div>



## Live Market Data

Various live market data is provided by py5paisa, like Market Depth and Market Feed.

### Market Depth


```python
d1 = c_5p.get_market_depth(sl1)
d1
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>AverageTradePrice</th>
      <th>BuyQuantity</th>
      <th>Close</th>
      <th>Exchange</th>
      <th>ExchangeType</th>
      <th>High</th>
      <th>LastQuantity</th>
      <th>LastTradeTime</th>
      <th>LastTradedPrice</th>
      <th>Low</th>
      <th>...</th>
      <th>Open</th>
      <th>OpenInterest</th>
      <th>ScripCode</th>
      <th>SellQuantity</th>
      <th>TotalBuyQuantity</th>
      <th>TotalSellQuantity</th>
      <th>UpperCircuitLimit</th>
      <th>Volume</th>
      <th>Datetime</th>
      <th>Symbol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2342.62</td>
      <td>0</td>
      <td>2352</td>
      <td>N</td>
      <td>C</td>
      <td>2359</td>
      <td>1</td>
      <td>/Date(1681986517000)/</td>
      <td>2346.05</td>
      <td>2332.1</td>
      <td>...</td>
      <td>2354.1</td>
      <td>0</td>
      <td>2885</td>
      <td>0</td>
      <td>0</td>
      <td>783</td>
      <td>2587.20</td>
      <td>3233882</td>
      <td>2023-04-20 19:37:00.123152</td>
      <td>RELIANCE</td>
    </tr>
    <tr>
      <th>1</th>
      <td>400.07</td>
      <td>0</td>
      <td>398.75</td>
      <td>N</td>
      <td>C</td>
      <td>402.65</td>
      <td>5</td>
      <td>/Date(1681986598000)/</td>
      <td>400.30</td>
      <td>397.7</td>
      <td>...</td>
      <td>400</td>
      <td>0</td>
      <td>1660</td>
      <td>0</td>
      <td>279</td>
      <td>0</td>
      <td>438.60</td>
      <td>6667781</td>
      <td>2023-04-20 19:37:00.123152</td>
      <td>ITC</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3094.25</td>
      <td>0</td>
      <td>3089.6</td>
      <td>N</td>
      <td>C</td>
      <td>3113</td>
      <td>11</td>
      <td>/Date(1681986560000)/</td>
      <td>3104.80</td>
      <td>3078</td>
      <td>...</td>
      <td>3090</td>
      <td>0</td>
      <td>11536</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>3398.55</td>
      <td>2419999</td>
      <td>2023-04-20 19:37:00.123152</td>
      <td>TCS</td>
    </tr>
  </tbody>
</table>
<p>3 rows × 23 columns</p>
</div>



### Market Feed


```python
c_5p.get_market_feed(sl1)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Chg</th>
      <th>ChgPcnt</th>
      <th>Exch</th>
      <th>ExchType</th>
      <th>High</th>
      <th>LastRate</th>
      <th>Low</th>
      <th>PClose</th>
      <th>Symbol</th>
      <th>TickDt</th>
      <th>Time</th>
      <th>Token</th>
      <th>TotalQty</th>
      <th>Datetime</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-5.95</td>
      <td>-0.252976</td>
      <td>N</td>
      <td>C</td>
      <td>2359.00</td>
      <td>2346.05</td>
      <td>2332.1</td>
      <td>2352.00</td>
      <td>RELIANCE</td>
      <td>/Date(1681986517000+0530)/</td>
      <td>35917</td>
      <td>2885</td>
      <td>3233882</td>
      <td>2023-04-20 19:37:03.343834</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1.55</td>
      <td>0.388715</td>
      <td>N</td>
      <td>C</td>
      <td>402.65</td>
      <td>400.30</td>
      <td>397.7</td>
      <td>398.75</td>
      <td>ITC</td>
      <td>/Date(1681986598000+0530)/</td>
      <td>35998</td>
      <td>1660</td>
      <td>6667781</td>
      <td>2023-04-20 19:37:03.343834</td>
    </tr>
    <tr>
      <th>2</th>
      <td>15.20</td>
      <td>0.491973</td>
      <td>N</td>
      <td>C</td>
      <td>3113.00</td>
      <td>3104.80</td>
      <td>3078.0</td>
      <td>3089.60</td>
      <td>TCS</td>
      <td>/Date(1681986560000+0530)/</td>
      <td>35960</td>
      <td>11536</td>
      <td>2419999</td>
      <td>2023-04-20 19:37:03.343834</td>
    </tr>
  </tbody>
</table>
</div>



### Market Data

For `feed_type='md'`, user gets the data for Buyers and seller for 5 depth. Here, Last traded price is not there.


```python
d1 = c_5p.get_market_data(sl1,feed_type='md')
d1
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Exch</th>
      <th>ExchType</th>
      <th>Token</th>
      <th>TBidQ</th>
      <th>TOffQ</th>
      <th>Details</th>
      <th>TimeStamp</th>
      <th>Time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>N</td>
      <td>C</td>
      <td>2885</td>
      <td>0</td>
      <td>783</td>
      <td>[{'Quantity': 0, 'Price': 0, 'NumberOfOrders':...</td>
      <td>0</td>
      <td>/Date(1681986590946)/</td>
    </tr>
    <tr>
      <th>1</th>
      <td>N</td>
      <td>C</td>
      <td>1660</td>
      <td>279</td>
      <td>0</td>
      <td>[{'Quantity': 279, 'Price': 400.3, 'NumberOfOr...</td>
      <td>0</td>
      <td>/Date(1681986598666)/</td>
    </tr>
    <tr>
      <th>2</th>
      <td>N</td>
      <td>C</td>
      <td>11536</td>
      <td>0</td>
      <td>14</td>
      <td>[{'Quantity': 0, 'Price': 0, 'NumberOfOrders':...</td>
      <td>0</td>
      <td>/Date(1681986591595)/</td>
    </tr>
  </tbody>
</table>
</div>



for `feed_type='mf'`, user gets the data for nearest bid and offer and the last traded price.


```python
d1 = c_5p.get_market_data(sl1,feed_type='mf')
d1
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Exch</th>
      <th>ExchType</th>
      <th>Token</th>
      <th>LastRate</th>
      <th>LastQty</th>
      <th>TotalQty</th>
      <th>High</th>
      <th>Low</th>
      <th>OpenRate</th>
      <th>PClose</th>
      <th>AvgRate</th>
      <th>Time</th>
      <th>BidQty</th>
      <th>BidRate</th>
      <th>OffQty</th>
      <th>OffRate</th>
      <th>TBidQ</th>
      <th>TOffQ</th>
      <th>TickDt</th>
      <th>ChgPcnt</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>N</td>
      <td>C</td>
      <td>2885</td>
      <td>2346.05</td>
      <td>1</td>
      <td>3233882</td>
      <td>2359.00</td>
      <td>2332.1</td>
      <td>2354.1</td>
      <td>2352.00</td>
      <td>2342.62</td>
      <td>35918</td>
      <td>0</td>
      <td>0.0</td>
      <td>783</td>
      <td>2346.05</td>
      <td>0</td>
      <td>783</td>
      <td>/Date(1681986518000)/</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>N</td>
      <td>C</td>
      <td>1660</td>
      <td>400.30</td>
      <td>5</td>
      <td>6667781</td>
      <td>402.65</td>
      <td>397.7</td>
      <td>400.0</td>
      <td>398.75</td>
      <td>400.07</td>
      <td>35999</td>
      <td>279</td>
      <td>400.3</td>
      <td>0</td>
      <td>0.00</td>
      <td>279</td>
      <td>0</td>
      <td>/Date(1681986599000)/</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>N</td>
      <td>C</td>
      <td>11536</td>
      <td>3104.80</td>
      <td>11</td>
      <td>2419999</td>
      <td>3113.00</td>
      <td>3078.0</td>
      <td>3090.0</td>
      <td>3089.60</td>
      <td>3094.25</td>
      <td>35961</td>
      <td>0</td>
      <td>0.0</td>
      <td>14</td>
      <td>3104.80</td>
      <td>0</td>
      <td>14</td>
      <td>/Date(1681986561000)/</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



## Getting Option Chain data

For getting option chain data, user needs the expiry date for the option chain. Available expiry dates can be weekly or monthly depending upon the type of security. For indices, the options can have weekly expiry and for all of the stocks the expiry is monthly.


```python
dates1 = c_5p.get_monthly_option_expiry()
dates1 = c_5p.get_weekly_option_expiry()
dates1
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Exch</th>
      <th>ExchType</th>
      <th>ExpiryDate</th>
      <th>Timestamp</th>
      <th>Date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>N</td>
      <td>D</td>
      <td>/Date(1681981200000+0530)/</td>
      <td>1681981200000</td>
      <td>2023-04-20</td>
    </tr>
    <tr>
      <th>1</th>
      <td>N</td>
      <td>D</td>
      <td>/Date(1682586000000+0530)/</td>
      <td>1682586000000</td>
      <td>2023-04-27</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>5</th>
      <td>N</td>
      <td>D</td>
      <td>/Date(1685005200000+0530)/</td>
      <td>1685005200000</td>
      <td>2023-05-25</td>
    </tr>
    <tr>
      <th>6</th>
      <td>N</td>
      <td>D</td>
      <td>/Date(1688029200000+0530)/</td>
      <td>1688029200000</td>
      <td>2023-06-29</td>
    </tr>
  </tbody>
</table>
<p>7 rows × 5 columns</p>
</div>




```python
c_5p.get_option_chain(sl1[0],'2023-04-27')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>CPType</th>
      <th>ChangeInOI</th>
      <th>EXCH</th>
      <th>ExchType</th>
      <th>LastRate</th>
      <th>Name</th>
      <th>OpenInterest</th>
      <th>Prev_OI</th>
      <th>PreviousClose</th>
      <th>ScripCode</th>
      <th>StrikeRate</th>
      <th>Volume</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>CE</td>
      <td>0</td>
      <td>N</td>
      <td>D</td>
      <td>0.0</td>
      <td>RELIANCE 27 APR 2023 CE 1160.00</td>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>55506</td>
      <td>1160</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>PE</td>
      <td>0</td>
      <td>N</td>
      <td>D</td>
      <td>0.0</td>
      <td>RELIANCE 27 APR 2023 PE 1160.00</td>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>55507</td>
      <td>1160</td>
      <td>0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>232</th>
      <td>CE</td>
      <td>0</td>
      <td>N</td>
      <td>D</td>
      <td>0.0</td>
      <td>RELIANCE 27 APR 2023 CE 3480.00</td>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>41363</td>
      <td>3480</td>
      <td>0</td>
    </tr>
    <tr>
      <th>233</th>
      <td>PE</td>
      <td>0</td>
      <td>N</td>
      <td>D</td>
      <td>0.0</td>
      <td>RELIANCE 27 APR 2023 PE 3480.00</td>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>41366</td>
      <td>3480</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>234 rows × 12 columns</p>
</div>



---
---
