Taiwan Stock Crawler Usage
========

Import Taiwan Stock Crawler
--------

```python
from taiwan_stock import crawler
```

Function Usage
--------

#### 獲取台灣股市股票列表 ####

股票列表是爬取 https://isin.twse.com.tw/isin/C_public.jsp?strMode=2 而得，函數使用方法如下：

```python
crawler.getStockList()
```

呼叫該函式後會把爬取的股票列表儲存至 `./output/股票列表/stockList.csv`，並且該表格的格式如下：

| 股票代號 | 股票名稱 | ISIN Code | 上市日 | 市場別 | 產業別 | 類型 |
| --- | --- | --- | --- | --- | --- | --- |
| 0050 | 元大台灣50 | TW0000050004 | 2003/06/30 | 上市 |  | ETF |

#### 獲取所有股票歷史紀錄 ####

函式使用方法如下：

```python
markets = ['上市', '上櫃']
types = ['股票', '臺灣存託憑證(TDR)', 'ETF', 'ETN', '特別股', '受益證券-不動產投資信託', '受益證券-資產基礎證券']
crawler.getAllStockHistories(markets, types)
```

其參數市場別(markets)分為上市、上櫃；而類型(types)分為股票、台灣存託憑證(TDR)、ETF、ETN、特別股、受益證券-不動產投資信託、受益證券-資產基礎證券，你可以自行選擇需要抓取的項目去設定參數。舉例來說，若你需要抓取所有"上市上櫃股票"的歷史紀錄可以這樣寫：

```python
markets = ['上市', '上櫃']
types = ['股票']
crawler.getAllStockHistories(markets, types)
```

此外，該函式抓的歷史紀錄是從 2000/01/01 到呼叫函式的當天，而歷史紀錄的格式如下：

| Date | High | Low | Open | Close | Volume | Adj Close |
| --- | --- | --- | --- | --- | --- | --- |
| 2000-01-04 | 114.1729965209961 | 109.66600036621094 | 111.54399871826172 | 114.1729965209961 | 57504806.0 | 106.16334533691406 |
| 2000-01-05 | 121.68399810791016 | 117.92900085449219 | 118.68000030517578 | 121.68399810791016 | 114795057.0 | 113.14742279052734 |