import yfinance as yf
import pandas as pd
import numpy as np
import datetime

def directionalBias():
    #Needs improving but does the job
    
    # Defines time parameters
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    start_date = today - datetime.timedelta(weeks=13)
    
    # opens up my shortlist of antisocial stocks and removes \n from end of each string
    df = (open('Antisocial.csv').read().splitlines())
    
    
    
    length = len(df)
    
    # loops through each stock and calculates directional bias
    # downloads ticker closing prices data before calculating 18 and 9 period ema's
    # final step is to compare the two, issuing a statement for both possibilities

    myList = []

    for i in range(length):
        tickerSymbol = df[i]
        tickerData = yf.Ticker(tickerSymbol)
        tickerDf = tickerData.history(period='1d', start=start_date, end=yesterday)
    
        tdf = tickerDf.loc[:]
    
        index_list = tdf.index.tolist()
    
        close_prices = tdf["Close"].tolist()
    
        def ExpMovingAverage9(values, window):
            weights = np.exp(np.linspace(-1., 0., window))
            weights /= weights.sum()
    
            a = np.convolve(values, weights)[:len(values)]
            a[:window] =a[window]
            return a
    
        ema_9 = (ExpMovingAverage9(close_prices, 9))
    
        def ExpMovingAverage18(values, window):
            weights = np.exp(np.linspace(-1., 0., window))
            weights /= weights.sum()
    
            b = np.convolve(values, weights)[:len(values)]
            b[:window] =b[window]
            return b

        ema_18 = (ExpMovingAverage18(close_prices, 18))
    
    # Returns list of all stocks that are suitable for a buy
        if (ema_9[-1]) > (ema_18[-1]):
            myList.append(df[i])
    
    return myList



# The below is how you can check on ema data

# for (st, lt) in zip(ema_9, ema_18):
#    if st >= lt:
#        print("Bullish")
#    if st < lt:
#       print("Bearish")
