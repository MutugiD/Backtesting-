from iexfinance.stocks import Stock 
from datetime import datetime, timedelta
from iexfinance.stocks import get_historical_data 
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.rcParams['figure.figsize'] = (7,3)

import seaborn as sns; 
sns.set(font_scale=1.5)
sns.set_style("whitegrid")

##enable sandbox
import os
os.environ['IEX_SANDBOX'] = 'enable'

#Input stock ticker and get info
ticker = input("Input symbol: ")
try:
    companyInfo = Stock(ticker, token = 'st_f30573882e64c4d19a8e43e3ad84c02eyye')
    stockPrice = companyInfo.get_price()
    print("Current stock price is: ", stockPrice)
except ValueError:
    print("Symbol not found.")

#historical period specification and 
#Input a period within last 5 years 
print("View Historical Information for the current stock {} ".format(ticker))
sy, sm, sd  = eval(input("Input start date as yyyy,m,d:"))
ey,em, ed = eval(input("Input end date as yyyy,m,d:"))


start= datetime(sy, sm, sd)
end= datetime(ey, em, ed)
historicalPrices = get_historical_data (ticker, start, end, 
                                        token = 'st_f30573882e64c4d19a8e43e3ad84c02eyye')
df = pd.DataFrame(historicalPrices).T

#specify storage location and name file
data_source = r'C:\Users\user\Desktop\Grad\PY Modules\Excel\IEXCloud\AAPL.xlsx'
df.to_excel(data_source)

#specify data_source and load file
df = pd.read_excel(r'C:\Users\user\Desktop\Grad\PY Modules\Excel\IEXCloud\AAPL.xlsx')
df = df.rename(columns={'Unnamed: 0': 'Date'})


#strategy definition - use of moving averages
class Strategy:
    def __init__(self): 
        self.t_name =  t_name 
        self.short_win = short_win
        self.long_win = long_win
        self.cond = df.index > self.long_win
        self.trade_price = df['open']
        self.close = df['close']
        
    def smav(self): 
        self.smav = np.where(Strategy().cond, Strategy().close.rolling(window =Strategy().short_win).mean(), 0)
        return self.smav
    
    def lmav(self): 
        self.lmav = np.where(Strategy().cond, Strategy().close.rolling(window =Strategy().long_win).mean(), 0)
        return self.lmav
    
    def trend_day(self): 
        self.trend_day = np.where(Strategy().lmav() > Strategy().smav(), 1, 
                            np.where(Strategy().lmav() < Strategy().smav(),-1,0))
        return self.trend_day
    
    def prev_trend_day (self):
        self.prev_trend_day = np.where(Strategy().cond, np.roll(Strategy().trend_day(), 1), 0)
        return self.prev_trend_day 
    def diff_trend_day (self): 
        self.diff_trend_day = Strategy().trend_day() + Strategy().prev_trend_day()
        return self.diff_trend_day
                                  
#global variable 
t_name = 'mav'
short_win = 5
long_win = 20

s= Strategy()

df ['smav'] = s.smav()
df ['lmav'] = s.lmav()
df ['trend_day'] = s.trend_day()
df['prev_trend_day'] = s.prev_trend_day()
df['diff_trend_day'] = s.diff_trend_day ()

#signal definition 
class Signal:
    def __init__(self):
        pass
    def trade_signal(self):
        self.trade_signal = np.where(Strategy().diff_trend_day() ==0, Strategy().trend_day(), 0)
        return self.trade_signal 
    def order (self): 
        self.order = np.where(Strategy().cond, np.roll(Signal().trade_signal(), 1), 0)
        return self.order 
        
ts = Signal()
    
df['trade_signal'] =  ts.trade_signal()
df['order'] = ts.order()

#portfolio definition 
class Portfolio:
    def __init__(self):
        self.lot_size_short = 1
        self.lot_size_long = 1
        self.contract_size = 1
        self.initial_cash = 10000
        self.short_amt = (1)* np.where (Signal().order()== -1, self.lot_size_short*
                                        self.contract_size*Strategy().trade_price, 0)
        self.long_amt = (-1)* np.where (Signal().order()==1, self.lot_size_long*
                                        self.contract_size*Strategy().trade_price, 0)
        
    def cash_delta(self): 
        self.cash_delta = Portfolio().long_amt + Portfolio().short_amt 
        return self.cash_delta
    def end_bal(self): 
        self.end_bal = Portfolio().initial_cash + Portfolio().cash_delta().cumsum()
        return self.end_bal
    def end_pos(self): 
        self.end_pos = Signal().order().cumsum()
        return self.end_pos 
              
p = Portfolio()
df['long_amt'] = p.long_amt
df['short_amt'] = p.short_amt
df['cash_delta'] = p.cash_delta()
df['end_bal'] = p.end_bal()
df['end_pos'] =  p.end_pos()

#profit n loss determination
df['pnl'] = df['end_bal'] + (Portfolio().end_pos() * Strategy().trade_price*Portfolio().contract_size)

#plots - close, smav, lmav 
import matplotlib.pyplot as plt
df1 = df.set_index('Date')
BBands = df1[['close','smav','lmav']].plot()

#profit/loss plot 
df1 = df.set_index('Date')
BBands = df1[['close','smav','lmav']].plot()

data_source = r'C:\Users\user\Desktop\Grad\PY Modules\Excel\IEXCloud\AAPLPnL.xlsx'
df1.to_excel(r'C:\Users\user\Desktop\Grad\PY Modules\Excel\IEXCloud\AAPLPnLL.xlsx')
