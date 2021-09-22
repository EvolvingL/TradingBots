import yfinance as yf
import datetime
import mplfinance as fplt
from Fibonacci import fibLevels



class DisplayPrice:
    def __init__(self, Ticker):
        self.Ticker = Ticker



    def getPrice(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        data = yf.download(
            tickers=self.Ticker,
            period="3d",
            interval="1h")


        fplt.plot(
            data,
            type='candle',
            title=self.Ticker,
            ylabel='Price($)'
        )



#myDisplay = DisplayPrice('AAPL')

#myDisplay.getPrice()


#anchorLow = input("Enter Fib Anchor: ")
#anchorHigh = input("Enter Fib Ceiling: ")

#print(fibLevels(float(anchorLow), float(anchorHigh)))

