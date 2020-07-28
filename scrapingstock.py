import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas_datareader import data
from datetime import date
from dfvaluetoint import format
from pytrends.request import TrendReq
import time
import datetime as dt
import pygsheets
import yfinance as yf
from pymongo import MongoClient

client = MongoClient('mongodb://192.168.1.115')
table=client['dow_jones_dbs']['dow_jones_table']
data = pd.DataFrame(list(table.find()))
del data['_id']


# access to gsheets
gc = pygsheets.authorize(service_account_file='stock-info-center-e644b7e86ffd.json')
spreadsheet = gc.open('My stock info page')

def getbettermentlist():
    dictlist=[]
    dictlist.append({'value':'VTI', 'label':'U.S. Total stock Market (VTI)'})
    dictlist.append({'value':'VEA', 'label':'International Developed Stocks (VEA)'})
    dictlist.append({'value':'VWO', 'label':'Emerging Market Stocks (VWO)'})
    dictlist.append({'value':'SHV', 'label':'Short-Term Treasuries (SHV)'})
    dictlist.append({'value':'SHY', 'label':'iShares 1-3 Year Treasury Bond ETF (SHY)'})
    dictlist.append({'value':'TLT', 'label':'iShares 20+ Year Treasury Bond ETF (TLT)'})
    dictlist.append({'value':'IEF', 'label':'iShares 7-10 Year Treasury Bond ETF (IEF)'})
    dictlist.append({'value':'IAU', 'label':'iShares Gold Trust (IAU)'})
    dictlist.append({'value':'VNQ', 'label':'Vanguard Real Estate ETF (VNQ)'})
    dictlist.append({'value':'DBC', 'label':'Invesco DB Commodity Index Tracking Fund (DBC)'})
    return dictlist

def saveSp500StocksInfo():
    soup = BeautifulSoup(requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies').text, 'lxml')
    tickers = []
    securities=[]
    gics_industries=[]
    gics_sub_industries=[]

    for row in soup.table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        security = row.findAll('td')[1].text
        gics_industry = row.findAll('td')[3].text
        gics_sub_industry = row.findAll('td')[4].text

        tickers.append(ticker.lower().replace("\n", " "))
        securities.append(security)
        gics_industries.append(gics_industry.lower())
        gics_sub_industries.append(gics_sub_industry.lower())

    stocks_info_df = pd.DataFrame({'tickers':tickers, 'securities': securities, 'gics_industries': gics_industries, 'gics_sub_industries':gics_sub_industries})

# Create a list of dict based on tickers and labels
    dictlist = []
    for index, row in stocks_info_df.iterrows():
         dictlist.append({'value':row["tickers"],'label':row["securities"]})
    return dictlist

# self append
def save_self_stocks_info():
    dictlist = []
    stklist=list('AAPL,UNH,HD,MSFT,GS,V,MCD,BA,MMM,JNJ,CAT,PG,IBM,WMT,TRV,DIS,NKE,AXP,JMP,CVX,MRK,RTX,INTC,VZ,CSCO,KO,XOM,WBA,DOW,PFE'.split(','))
    for stk in stklist:
        dictlist.append({'value':stk, 'label':stk})
    
    return dictlist

#table of critical values
# def getfinancialreportingdf(ticker):
#     urlfinancials = 'https://www.marketwatch.com/investing/stock/'+ticker+'/financials'
#     urlbalancesheet = 'https://www.marketwatch.com/investing/stock/'+ticker+'/financials/balance-sheet'

#     text_soup_financials = BeautifulSoup(requests.get(urlfinancials).text,"lxml") #read in
#     text_soup_balancesheet = BeautifulSoup(requests.get(urlbalancesheet).text,"lxml") #read in

#     #Income statement
#     titlesfinancials = text_soup_financials.findAll('td', {'class': 'rowTitle'})
#     epslist =[]
#     netincomelist = []
#     interestexpenselist = []
#     ebitdalist = []
#     yearlist = [2015, 2016, 2017, 2018, 2019]

#     for title in titlesfinancials:
#         if 'EPS (Basic)' in title.text:
#             epslist.append([td.text for td in title.findNextSiblings('td', {'class': 'valueCell'})])    
#         if 'Net Income' in title.text:
#             netincomelist.append([td.text for td in title.findNextSiblings('td', {'class': 'valueCell'})])
#         if 'Interest Expense' in title.text:
#             interestexpenselist.append([td.text for td in title.findNextSiblings('td', {'class': 'valueCell'})])
#         if 'EBITDA' in title.text:
#             ebitdalist.append([td.text for td in title.findNextSiblings('td', {'class': 'valueCell'})])
    
#     #take only the correct rows of data
#     eps = epslist[0]
#     epsgrowth = epslist[1]
#     netincome = netincomelist[1]
#     interestexpense = interestexpenselist[0]
#     ebitda = ebitdalist[0]

#     #Balance sheet
#     titlesbalance = text_soup_balancesheet.findAll('td', {'class': 'rowTitle'})
#     shareholdersquitylist = []
#     longtermdebtlist = []

#     for title in titlesbalance:
#         if 'Total Shareholders\' Equity' in title.text:
#             shareholdersquitylist.append([td.text for td in title.findNextSiblings('td', {'class': 'valueCell'})])
#         if 'Long-Term Debt' in title.text:
#             longtermdebtlist.append([td.text for td in title.findNextSiblings('td', {'class': 'valueCell'})])



#     shareholderquity = shareholdersquitylist[0]
#     longtermdebt = longtermdebtlist[0]
#     ROA = shareholdersquitylist[1]

#     df = pd.DataFrame({'EPS': eps, 'EPS Growth':epsgrowth, 'Net Income': netincome, 'Shareholder Equity':shareholderquity,'ROA': ROA, 'Long-Term Debt': longtermdebt, 'Interest Expense': interestexpense, 'EBITDA': ebitda}, index=yearlist)
#     df.index.name = 'Year'
#     return df

# def includecalcvariablesdf(ticker):
#     df = getfinancialreportingdf(ticker)
#     dftoint = df.apply(format)
#     dftoint['ROE'] = dftoint['Net Income']/dftoint['Shareholder Equity']
#     dftoint['Interest Coverage Ratio'] = dftoint['EBITDA']/dftoint['Interest Expense']
#     return dftoint

#get
# def getetfdf(ticker):
#     url="https://finance.yahoo.com/quote/"+ticker+"?p="+ticker
#     soup=BeautifulSoup(requests.get(url).text, 'lxml')

#     titlelist=[]
#     valuelist=[]

#     #get the titles wanted
#     titles=soup.findAll('td', class_="C($primaryColor)")
#     for i in titles: 
#         if "Volume"==i.text or "Net Assets"==i.text or "NAV"==i.text or "PE Ratio (TTM)"==i.text or "Inception Date"==i.text:
#             titlelist.append(i.text)
    
#     #get the values wanted
#     values=soup.findAll('td', class_="Ta(end) Fw(600) Lh(14px)")
#     for i in values:
#         valuelist.append(i.text)
#     #remove values that are not needed (e.g. value of Previous Close)
#     valuelist=[valuelist[6]]+valuelist[8:11]+[valuelist[-1]]

#     #create a dataframe
#     df = pd.DataFrame([valuelist], columns=titlelist)
#     df=df.set_index("Inception Date")
#     return df

# #get
# def getetfdf2(ticker):
#     url="https://finance.yahoo.com/quote/"+ticker+"?p="+ticker
#     soup=BeautifulSoup(requests.get(url).text, 'lxml')

#     titlelist=[]
#     valuelist=[]    

#     #get the titles wanted
#     titles=soup.findAll('td', class_="C($primaryColor)")
#     for i in titles: 
#         if "Yield"==i.text or "YTD Daily Total Return"==i.text or "Beta (5Y Monthly)"==i.text or "Expense Ratio (net)"==i.text:
#             titlelist.append(i.text)
    
#     #get the values wanted
#     values=soup.findAll('td', class_="Ta(end) Fw(600) Lh(14px)")
#     for i in values:
#         valuelist.append(i.text)

#     #remove values that are not needed (e.g. value of Previous Close)
#     valuelist=valuelist[11:15]

#     #create a dataframe
#     df = pd.DataFrame([valuelist], columns=titlelist)
#     df=df.set_index("Yield")
#     return df

def get_etf_df(ticker):
    etf_table=client['Dashboard']['get_etf_df']
    etf_df = pd.DataFrame(list(etf_table.find({'Ticker':{'$eq':'VEA'}})))
    del etf_df['_id']
    return etf_df

#get
def get_google_Trends_df(ticker):
    pytrends = TrendReq(hl = 'en-US', tz = 360)
    trend_df = pd.DataFrame()
    kw_list = [ticker]
    pytrends.build_payload(kw_list, timeframe = 'today 3-m')
    trend_df[ticker] = pytrends.interest_over_time()[ticker]
    time.sleep(1)

    trend_df.index = list(map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d'), list(trend_df.index)))
    trend_df.set_index(trend_df.index)
    return trend_df

def get_candlestick_df(ticker):
    global data
    stk_price_df = data[data["Ticker"] == ticker]
    return stk_price_df

#helper function for calculating rsi, https://tcoil.info/compute-rsi-for-stocks-with-python-relative-strength-index/
def computeRSI (data, time_window):
    diff = data.diff(1).dropna()        # diff in one field(one day)

    #this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]
    
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]
    
    # check pandas documentation for ewm
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    # values are related to exponential decay
    # we set com=time_window-1 so we get decay alpha=1/time_window
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    return rsi

def get_rsi_df(ticker):
    global data
    temp=data[data["Ticker"] == ticker]
    temp['RSI'] = computeRSI(temp['Adj Close'], 14)
    return temp

K=0
D=0
def get_kd_df(ticker):
    global data
    kd_df=data[data["Ticker"] == ticker].set_index('Date')
    kd_df.index = pd.to_datetime(kd_df.index)
    del kd_df['Volume']
    del kd_df['Adj Close']
    kd_df['9DAYMAX']=kd_df['High'].rolling('9D').max()
    kd_df['9DAYMIN']=kd_df['Low'].rolling('9D').min()
    kd_df['RSV']=100*(kd_df['Close']-kd_df['9DAYMIN'])/(kd_df['9DAYMAX']-kd_df['9DAYMIN'])
    #calc K
    def KValue(rsv):
        global K
        K = (2/3) * K + (1/3) * rsv
        return K
    kd_df['K'] = 0
    kd_df['K'] = kd_df['RSV'].apply(KValue)
    #calc D
    def DValue(k):
        global D
        D = (2/3) * D + (1/3) * k
        return D
    kd_df['D'] = 0
    kd_df['D'] = kd_df['K'].apply(DValue)
    return kd_df

def get_econ_event_df():
    time.sleep(2)
    ws = spreadsheet.worksheet_by_title('Sheet1')
    econeventdf = ws.get_as_df(start='A53', numerize=False, including_tailing_empty=False)
    
    return econeventdf

def get_stock_df(ticker):
    time.sleep(3)
    ws = spreadsheet.worksheet_by_title('Sheet1')
    ws.update_value('B4',ticker)
    stkdf = ws.get_as_df(start='A4',end=(6, 7), numerize=False, including_tailing_empty=False)
    return stkdf

#get
def get_investors_df(ticker):
    result=[]
    ticker.replace('-','.')
    soup=BeautifulSoup(requests.get('https://www.gurufocus.com/stock/'+ticker+'/guru-trades').text, 'html5lib')
    table = soup.find_all('table')[5]
    for i in range(1, len(soup.find_all('table')[4].find_all('tr'))):
        data = {'知名投資人': None,
                '調整日期': None,
                '持有股數': None,
                #'Per Outstand': None,
                '股權佔比': None,
                'Comment': None}

        data['知名投資人'] = soup.find_all('table')[4].find_all('tr')[i].find_all('td')[0].get_text().replace('\n','')
        data['調整日期'] = soup.find_all('table')[4].find_all('tr')[i].find_all('td')[1].get_text()
        data['持有股數'] = soup.find_all('table')[4].find_all('tr')[i].find_all('td')[2].get_text()
#        data['Per Outstand'] = soup.find_all('table')[4].find_all('tr')[i].find_all('td')[3].get_text()
        data['股權佔比'] = soup.find_all('table')[4].find_all('tr')[i].find_all('td')[4].get_text()
        data['評價與調整'] = soup.find_all('table')[4].find_all('tr')[i].find_all('td')[5].get_text()  
        
        result.append(data)


        # change from dictionary to DataFrame
    big_trader_df = pd.DataFrame.from_dict(result)
    return big_trader_df


#if __name__ == '__main__':
