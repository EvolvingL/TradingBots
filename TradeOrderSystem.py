# I will input order price and SL price, system will pull my portfolio balance, and, keeping risk per position to under
# 2% will return the necessary volumes of my 3 sub positions, and place these into the corresponding individual order
# Functions with the only work then needing to be done being entering target levels
# Programme will then place orders with corresponding order prices, stop losses and target prices for each sub position
# Once the market is closed.

#Position Divider will take inputs and spit corresponding position volumes, as well as OTE, SL, and targets for each
#into the programme

import positionsizer
from positionsizer import max_risk
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi import order
from pandas.core.arrays import ExtensionArray
import cv2
import pytesseract
from pytesseract import Output
import csv
import sys
import threading
import time
# I will manually enter ticker and past


class myOrder:
    def __init__(self, Ticker, StopLoss, Entry, firstTarget, secondTarget, thirdTarget ):
        self.Ticker = Ticker
        self.StopLoss = StopLoss
        self.Entry = Entry
        self.firstTarget = firstTarget
        self.secondTarget = secondTarget
        self.thirdTarget = thirdTarget



    def PlaceTrade(self):
        tick = self.Ticker




        # arranges list to match with corresponding price point
        t3 = self.thirdTarget
        t2 = self.secondTarget
        t1 = self.firstTarget
        ote = self.Entry
        sl = self.StopLoss


#        #Returns trade information from trade class in positionsizer
#        trade1 = positionsizer.Trade(tick, t3, t2, t1, ote, sl)
#        trade1.get_trade_info()

#        OrderLevels = "Check Order Levels: ", str(sl),  str(ote), str(t1), str(t2), str(t3)

        #requires user to hit enter before continuing to place orders
#        print("Press Enter to Check Connection")
#        sys.stdin.readline()



        cents_at_risk = ote - sl


        # calculate ideal position size and risk for trade in USD & % terms
        ideal_position_size = (max_risk / cents_at_risk) - 1

        # specifies volumes for trade 1, 2 and 3
        v1 = round(ideal_position_size * 0.3)
        v2 = round(ideal_position_size * 0.4)
        v3 = round(ideal_position_size * 0.3)

        if ideal_position_size < (v1 + v2 + v3):
            v3 = v3 - 1


        tradeSize = v1 + v2+ v3

        class IBapi(EWrapper, EClient):
            def __init__(self):
                EClient.__init__(self, self)

            def nextValidId(self, orderId: int):
                super().nextValidId(orderId)
                self.nextorderId = orderId
#                print("The next valid order ID is: ", self.nextorderId)

            def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                            whyHeld, mktCapPrice):
                print('orderStatus - orderId:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
                      'lastFillPrice', lastFillPrice)

            def openOrder(self, orderId, contract, order, orderState):
                print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
                      order.orderType, order.totalQuantity, orderState.status)

            def execDetails(self, reqId, contract, execution):
                print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
                      execution.orderId, execution.shares, execution.lastLiquidity)


        def run_loop():
            app.run()


        # Function to create Stocks Order contract
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

        #requires user to hit enter before continuing to place order
#        print("Press Enter to Place Orders")
#        sys.stdin.readline()

        #create object for order
        parent = Order()
        parent.orderId = app.nextorderId
        parent.action = 'BUY'
        parent.totalQuantity = tradeSize
        parent.orderType = 'LMT'
        parent.lmtPrice = ote
        parent.transmit = False

        # Create stop loss order object
        stop_order = Order()
        global stopID
        stopID = stop_order.orderId
        #Need to write this to a file so it's persistent, then I can read from elsewhere
        stopID = app.nextorderId + 1
        stop_order.action = 'SELL'
        stop_order.totalQuantity = tradeSize
        stop_order.orderType = 'STP'
        stop_order.auxPrice = sl
        stop_order.ParentId = parent.orderId
        stop_order.transmit = False

        # Create take profit order object
        tp_order = Order()
        tp_order.orderId = app.nextorderId + 2
        tp_order.action = 'SELL'
        tp_order.totalQuantity = v1
        tp_order.orderType = 'LMT'
        tp_order.lmtPrice = t1
        tp_order.ParentId = parent.orderId
        tp_order.transmit = False

        # Create take profit order object 2
        tp_order1 = Order()
        tp_order1.orderId = app.nextorderId + 3
        tp_order1.action = 'SELL'
        tp_order1.totalQuantity = v2
        tp_order1.orderType = 'LMT'
        tp_order1.lmtPrice = t2
        tp_order1.ParentId = parent.orderId
        tp_order1.transmit = False

        # Create take profit order object 3
        tp_order2 = Order()
        tp_order2.orderId = app.nextorderId + 4
        tp_order2.action = 'SELL'
        tp_order2.totalQuantity = v3
        tp_order2.orderType = 'LMT'
        tp_order2.lmtPrice = t3
        tp_order2.ParentId = parent.orderId
        tp_order2.transmit = False

        # Place orders
        app.placeOrder(parent.orderId, stk_order(tick), parent)
        app.placeOrder(stopID, stk_order(tick), stop_order)
        app.placeOrder(tp_order.orderId, stk_order(tick), tp_order)
        app.placeOrder(tp_order1.orderId, stk_order(tick), tp_order1)
        app.placeOrder(tp_order2.orderId, stk_order(tick), tp_order2)

        #Cancel order
        #print('cancelling order')
        #app.cancelOrder(app.nextOrderId)


        time.sleep(3)
        app.disconnect()

        datafile = open("StopID.txt", "w+")
        datafile.write(str(stopID))
        datafile.close()

        datafile = open("t1.txt", "w+")
        datafile.write(str(t1))
        datafile.close()

        datafile = open("ticker.txt", "w+")
        datafile.write(str(tick))
        datafile.close()

        datafile = open("IPS.txt", "w+")
        datafile.write(str(tradeSize))
        datafile.close()
