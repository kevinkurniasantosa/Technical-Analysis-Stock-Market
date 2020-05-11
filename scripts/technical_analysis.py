from pandas_datareader import data   
from pandas_datareader._utils import RemoteDataError
import pandas as pd
import numpy as np 
from datetime import datetime, timedelta, date
# For filtering warnings
from warnings import simplefilter
# For calculating the technical analysis indicators
import talib 
# For plotting the stock price and indicators
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc 
from matplotlib.pylab import date2num
from matplotlib.pylab import rcParams

### SETUP THE FIGURE SIZE FOR PLOT
rcParams['figure.figsize'] = 12,6

### TO IGNORE FUTURE WARNINGS
simplefilter(action='ignore', category=FutureWarning)

### DEFINE TODAY'S DATE 
today_date = date.today().strftime('%Y-%m-%d')
print('SCRIPT RUN ON ' + today_date)
print('================================')

###################################
########################################## CONFIGURATION REQUIRED ##########################################
### Please check/change the parameters below before running

## INITIALIZE THE TIME FRAME, FORMAT: YYYY-MM-DD
start_date = '2018-05-11'
end_date = str(datetime.now().strftime('%Y-%m-%d'))

## DEFINE THE STOCK SYMBOL
uk_stock = ''
us_stock = 'AAPL'

## DEFINE THE MOVING AVERAGE PERIOD
ma_period1 = 10 # Short term MA
ma_period2 = 20 # Mid term MA
ma_period3 = 180 # Long term MA (for indicating trend bias)
ema_period1 = 10
ema_period2 = 20

## PLOT FILENAME SPECIFICATIONS
plot_chart_filename = '{}_technical_indicators'.format(us_stock)

##################################################################
##################################################################

## For data collection
def get_data(ticker):
    try:
        stock_data = data.DataReader(ticker, 'yahoo', start_date, end_date)

        ## The format of this data is High, Low, Open, Close, Volume, Adj Close
        ## Hence, change it to the default OHLC structure first -> Open, High, Low, Close, Adj Close, Volume
        column_titles = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        stock_data = stock_data.reindex(columns=column_titles)

        print('== PREVIEW STOCK DATA == ')
        print(stock_data)
    except RemoteDataError:
        print('No data found for {}'.format(ticker))

    return stock_data

## For setup the technical indicators that are going to be used
def get_technical_indicators(data):
    ## Simple Moving Average (SMA)
    data['ma{}'.format(ma_period1)] = talib.MA(data['Close'], timeperiod=ma_period1)
    data['ma{}'.format(ma_period2)] = talib.MA(data['Close'], timeperiod=ma_period2)
    # data['ma{}'.format(ma_period3)] = talib.MA(data['Close'], timeperiod=ma_period3)

    ## Exponential Moving Average (EMA)
    # data['ema{}'.format(ema_period1)] = talib.EMA(data['Close'], timeperiod=ema_period1)
    # data['ema{}'.format(ema_period2)] = talib.EMA(data['Close'], timeperiod=ema_period2)

    ## Relative Strenght Indicator (RSI)
    data['rsi'] = talib.RSI(data['Close'])

    ## Moving Average Convergence Divergence (MACD)
    data['macd'], data['macd_signal'], data['macd_hist'] = talib.MACD(data['Close'])

    return data

## For plotting the chart
def plot_stock_chart(data):
    ## Create fgiure and set axes for subplots
    fig = plt.figure()
    fig.set_size_inches((16,12))
    ax_candlestick = fig.add_axes((0, 0.72, 1, 0.32))
    ax_rsi = fig.add_axes((0, 0.48, 1, 0.2), sharex=ax_candlestick)
    ax_macd = fig.add_axes((0, 0.24, 1, 0.2), sharex=ax_candlestick)
    ax_vol = fig.add_axes((0, 0, 1, 0.2), sharex=ax_candlestick)

    ## Format x-axis ticks as dates
    ax_candlestick.xaxis_date()

    ## Get nested list of date, open, high, low and close prices
    ohlc = []
    for date, row in data.iterrows():
        openp, highp, lowp, closep = row[:4]
        ohlc.append([date2num(date), openp, highp, lowp, closep])
 
    ## Plot candlestick chart
    ax_candlestick.plot(data.index, data["ma{}".format(ma_period1)], color='orangered', label="SMA {}-period".format(ma_period1))
    ax_candlestick.plot(data.index, data["ma{}".format(ma_period2)], color='dodgerblue', label="SMA {}-period".format(ma_period2))
    # ax_candlestick.plot(data.index, data["ma{}".format(ma_period3)], label="SMA {}-period".format(ma_period3))
    # ax_candlestick.plot(data.index, data["ema{}".format(ema_period1)], label="EMA {}-period".format(ema_period1))
    # ax_candlestick.plot(data.index, data["ema{}".format(ema_period2)], label="EMA {}-period".format(ema_period2))
    candlestick_ohlc(ax_candlestick, ohlc, colorup="springgreen", colordown="r", width=0.8)
    ax_candlestick.legend()
    
    ## Plot RSI, Above 70% = overbought, below 30% = oversold
    ax_rsi.set_ylabel("(%)")
    ax_rsi.plot(data.index, data["rsi"], color='darkorchid', label="RSI")
    ax_rsi.plot(data.index, [70] * len(data.index), 'g--', linewidth=2, label="Overbought")
    ax_rsi.plot(data.index, [30] * len(data.index), 'r--', linewidth=2, label="Oversold")
    ax_rsi.legend()

    ## Plot MACD
    ax_macd.plot(data.index, data["macd"], label="MACD line")
    ax_macd.bar(data.index, data["macd_hist"] * 3, color='navy', linewidth=2, label="Histogram")
    ax_macd.plot(data.index, data["macd_signal"], color='orangered', linewidth=2, label="Signal line")
    ax_macd.legend()
    
    ## Show volume in millions
    ax_vol.bar(data.index, data["Volume"] / 1000000)
    ax_vol.set_ylabel("(Million)")
   
    ## Save the chart as PNG
    fig.savefig('../charts/' + plot_chart_filename + ".png", bbox_inches="tight")
    
    plt.show()

## MAIN FUNCTION
def main():
    STOCK_DATA = get_data(us_stock)
    STOCK_DATA_WITH_INDICATORS = get_technical_indicators(STOCK_DATA)
    plot_stock_chart(STOCK_DATA_WITH_INDICATORS)
    
if __name__ == '__main__':
    main()