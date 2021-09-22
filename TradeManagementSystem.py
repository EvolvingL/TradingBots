from datetime import datetime, time
import time
import yfinance as yf
import numpy as np
from itertools import tee, islice, chain
import pandas as pd
import holidays
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
import threading


today = datetime.today().date()
thisYear = datetime.today().year
now = datetime.today().now().time()

myTicker = "CTXS"

data = yf.download(
        tickers=myTicker,
        period="1d",
        interval="5m", )

def dailyHigh():
    prices = yf.Ticker(myTicker).history(period='15m', start=today, end=today)

    tdf = prices.loc[:]

    highPrice = tdf["High"].tolist()
    return highPrice



mylist = []

for i in data["Low"]:
    mylist.append(round(i, 2))

mylist = np.array(mylist, dtype=str)


# function outputs the last, current, and next price at a 15 minute interval
def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

swingLows = []

global current2LSL



# Identifies swing lows on a 15 minute chart, returning that number
def getSecondLastSL():
    for previous, item, nxt in previous_and_next(mylist[:-1]):
        if previous is not None and nxt is not None:
          if previous > item < nxt:
                swingLows.append(item)
    return swingLows[-2]




def isHoliday(Date):
    us_holidays = []
    for date in holidays.UnitedStates(years=thisYear).items():
        us_holidays.append(str(date[0]))
    if Date in us_holidays:
        return True
    else:
        return False



def ordersOnMarket():
    # Connects to TWS
    class IBapi(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)

    app = IBapi()
    app.connect('127.0.0.1', 7497, 123)
    if app.reqOpenOrders() is None:
        return False
    if app.reqOpenOrders() is not None:
        return True

    app.disconnect()

def getSL():
    for previous, item, nxt in previous_and_next(mylist[:-1]):
        if previous is not None and nxt is not None:
            if previous > item < nxt:
                swingLows.append(item)
    global x
    x = swingLows[-1]
    return x

datafile = open("StopID.txt", "r")
datafile.seek(0)
stopID = datafile.read()
datafile.close()

datafile = open("t1.txt", "r")
datafile.seek(0)
t1 = datafile.read()
datafile.close()

datafile = open("ticker.txt", "r")
datafile.seek(0)
ticker = datafile.read()
datafile.close()

datafile = open("IPS.txt", "r")
datafile.seek(0)
ideal_position_size = datafile.read()
datafile.close()




#Trade Management
def updateStop(SecondLastSL):
    class IBapi(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)

        def nextValidId(self, orderId: int):
            super().nextValidId(orderId)
            self.nextorderId = orderId
            print("The next valid order ID is: ", self.nextorderId)

        def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice,
                        clientId,
                        whyHeld, mktCapPrice):
            print('orderStatus - orderId:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
                  'lastFillPrice', lastFillPrice)

        def openOrder(self, orderId, contract, order, orderState):
            print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':',
                  order.action,
                  order.orderType, order.totalQuantity, orderState.status)

        def execDetails(self, reqId, contract, execution):
            print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
                  execution.orderId, execution.shares, execution.lastLiquidity)

    def run_loop():
        app.run()

    def stk_order(symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = "USD"
        return contract

    app = IBapi()
    app.connect('127.0.0.1', 7497, 123)

    app.nextorderId = None

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Check if the API is connected via orderId
    while True:
        if isinstance(app.nextorderId, int):
            print('connected')
            break
        else:
            print('waiting for connection')
            time.sleep(1)



    app.cancelOrder(stopID)

    stop_order = Order()
    stop_order.orderId = app.nextorderId + 1
    stop_order.action = 'SELL'
    stop_order.totalQuantity = ideal_position_size
    stop_order.orderType = 'STP'
    stop_order.auxPrice = SecondLastSL
    stop_order.transmit = False
    app.placeOrder(stop_order.orderId, stk_order(ticker), stop_order)



    time.sleep(3)
    app.disconnect()



#while ordersOnMarket() is False:
#    time.sleep(900)


firstTime = True

def firstTarget():
    while ordersOnMarket() is True:
        if dailyHigh() >= t1:

            if firstTime:
                updateStop(getSecondLastSL())
                firstTime = False


            current2LSL = getSecondLastSL()
            while current2LSL == getSecondLastSL():
                time.sleep(60)

            updateStop(getSecondLastSL())
            time.sleep(60)












