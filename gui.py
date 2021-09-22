from tkinter import *
from DirectionalBiasTool import directionalBias
from PriceDisplay import DisplayPrice
from Fibonacci import fibLevels
from TradeOrderSystem import myOrder
from positionsizer import Trade


root = Tk()


def stockClick(item):
    prices = DisplayPrice(item)
    prices.getPrice()

i=0


def DB_ButtonClick():
    x = 0
    y = 0

    for item in directionalBias():
        button = Button(root, text = item, command=lambda item = item: stockClick(item))
        button.grid(row=3, column=y)
        x += 1
        y += 1

    ticker = Entry(root, width=20)
    ticker.insert(0, "Enter Ticker")

    fibFloor = Entry(root, width=20)
    fibFloor.insert(0, "Enter Fib Floor")

    fibCeiling = Entry(root, width=20)
    fibCeiling.insert(0, "Enter Fib Ceiling")

    ticker.grid(row=4, column=0)
    fibFloor.grid(row=4, column=1)
    fibCeiling.grid(row=4, column=2)

    def placeTrade():
        myList = fibLevels(float(fibFloor.get()), float(fibCeiling.get()))
        SL = myList[0]
        OTE = myList[1]
        T1 = myList[2]
        T2 = myList[3]
        T3 = myList[4]

        trade1 = Trade(ticker.get(), T3, T2, T1, OTE, SL).get_trade_info()

        y = 7

        for item in trade1:
            label = Label(root, text=item)
            label.grid(row=y, column=0)
            y += 1
            root.update()

        activeTrade = myOrder(ticker.get(), SL, OTE, T1, T2, T3)
        activeTrade.PlaceTrade()

    fibLev_Button = Button(root, text="Place Trade", command=placeTrade)
    fibLev_Button.grid(row=6, column=0)



DB_Button = Button(root, text="Available Longs", command=DB_ButtonClick)
DB_Button.grid(row=0, column=0)





root.mainloop()