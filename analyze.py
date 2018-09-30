#2Q358NIIGNCMQME0

from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import sys
import csv
import pandas as pd
import statistics
from re import sub
from decimal import Decimal
from dateutil.parser import parse
from itertools import count
from datetime import timedelta
import matplotlib.pyplot as plt


#pd.read_csv('revenue.csv').T.to_csv('revenue.csv',header=False)
index = {}
stockstickers = ["TOL", "DHI", "LEN", 	"NVR",	"PMH", 	 "TMHC"	, "AVHI" , "BZH" , "CVCO", "CCS", "GBRK" ,"HOV"	, "KBH"	, "LGIH" , "WLH", "MHO"	,"MDC",	"MTH", "TPH"]
revenue = {}
stockPrices = {}



def standardizeDate(vals , listOfData):

    stdev = statistics.stdev(vals)
    mean = statistics.mean(vals)
    i =0;
    for row in listOfData:
        money = listOfData[row]
        value = float(sub(r'[^\d.]', '', money))
        listOfData[row] = (value - mean)/stdev


for stock in stockstickers:
    revenue[stock] = {}
    stockPrices[stock] = {}

with open('index.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    vals = []
    for row in reader:
        index[row['\xef\xbb\xbfDate']] = row['Index']
        vals.append(float (row['Index']))
    standardizeDate(vals, index)

with open('cleanRevenue.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        for stockTicker in stockstickers:
            if row[stockTicker] != '' :
                lookUpVal = 'Date_' + stockTicker
                revenue[stockTicker][row[lookUpVal]] = row[stockTicker]

with open('stockPrices.csv') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        for stockTicker in stockstickers:
            if row[stockTicker] != '' :
                lookUpVal = '\xef\xbb\xbfDate_' + stockTicker
                if lookUpVal in row:
                    stockPrices[stockTicker][row[lookUpVal]] = row[stockTicker]
                else:
                    lookUpVal = 'Date_' + stockTicker
                    stockPrices[stockTicker][row[lookUpVal]] = row[stockTicker]

def analysis (symbol):

    # Normalize the values and store it into an array

    vals  = []
    for data in revenue[symbol]:
        money = revenue[symbol][data]
        value = float(sub(r'[^\d.]', '', money))
        vals.append(value)

    standardizeDate(vals, revenue[symbol])

    # calculate differences and store that into an array
    diff = {}
    d = []
    for data in revenue[symbol]:
        indexMonth= data.split('/')[0]
        indexYear = data.split('/')[2]
        indexLookUp = indexMonth + '/' + '1' + '/' + indexYear
        diff[data] = index[indexLookUp] -revenue[symbol][data]
        d.append(index[indexLookUp] - revenue[symbol][data] )


    trading_stdev = statistics.stdev(d)
    trading_mean = statistics.stdev(d)



    # generate a 1 0 dict for every date

    money = 10000
    quarters = 0

    x = []
    y = []

    for differnece in diff:
        x.append(quarters)
        y.append(((money/float(10000))-1) )
        quarters = quarters + 1
        print differnece
        if diff[differnece] > trading_stdev+ trading_mean :
            money = money +  -1 * returns(differnece, symbol, money)
        elif diff[differnece] < trading_mean - trading_stdev :
            money = money + 1 * returns(differnece, symbol, money)

    print str((float(money/10000) ))
    annualizedReturn = ((pow(float(money/10000) ,4/ float(quarters)) -1 ) )
    temp = statistics.stdev(y)
    sharpe = (annualizedReturn - 0.02)/temp
    print sharpe

    # get stock price and trade
    plt.scatter(x,y, color='k', s=25, marker="o")

    plt.xlabel('quarters passed')
    plt.ylabel('revenue')
    plt.title('$10000 invested in ' + symbol)
    plt.legend()
    #plt.show()




def returns(date, symbol, money):

    newDate = parse(date)

    before = parse(date) - timedelta(days=5)
    after = parse(date) + timedelta(days=5)

    formatedYear = before.year%100
    if (formatedYear < 10):
        formatedYear = "0" + str(formatedYear)
    formatedYear = str(formatedYear)

    lookUpBefore = str(before.month) + "/" + str(before.day) + "/" + formatedYear
    lookUpAfter = str(after.month ) + "/" + str(after.day) + "/" + formatedYear

    first = 0
    second = 0

    if lookUpAfter in stockPrices[symbol]:
        first = stockPrices[symbol][lookUpAfter]
    else:
        after = after +  timedelta(days=2)
        lookUpAfter = str(after.month ) + "/" + str(after.day) + "/" + formatedYear
        if lookUpAfter in stockPrices[symbol]:
            first = stockPrices[symbol][lookUpAfter]


    if lookUpBefore in stockPrices[symbol]:
        second = stockPrices[symbol][lookUpBefore]
    else:
        before = before - timedelta(days=2)
        lookUpBefore = str(before.month) + "/" + str(before.day) + "/" + formatedYear
        if lookUpBefore in stockPrices[symbol]:
            second = stockPrices[symbol][lookUpBefore]

    if  not float(first) or not float(second):
        return 0

    return (float(first) - float(second))* (money/float(second))


    #if date in stockPrices[symbol] :

def main():
    for stock in stockstickers:
        analysis(stock)

if __name__ == "__main__":
    main()
