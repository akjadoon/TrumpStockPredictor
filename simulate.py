import pandas as pd
from datetime import date, time, timedelta

STOCKS = [
    {'name': 'SSE' , 'data':pd.read_csv('data\\000001.SS.csv'),'open': time(9, 30), 'close':time(15, 00)},
    {'name': 'HSI' , 'data':pd.read_csv('data\\HSI.csv'),'open': time(9, 15),'close':time(16, 30)},
    {'name': 'N225' , 'data':pd.read_csv('data\\N225.csv'),'open':time(9, 45),'close':time(16, 15)},
    {'name': 'KS11' , 'data':pd.read_csv('data\\KS11.csv'),'open': time(10, 00),'close': time(16, 45)},
    {'name': 'BSESN' , 'data':pd.read_csv('data\\BSESN.csv'),'open': time(6, 15),'close': time(12, 30)},
    {'name': 'MICEX', 'data': pd.read_csv('data\\MICEX.csv'), 'open': time(14, 00),'close': time(23, 30)},
    {'name': 'STOXX50E', 'data': pd.read_csv('data\\STOXX50E.csv'), 'open': time(14,00), 'close': time(23,30)},
    {'name': 'EUR_USD', 'data': pd.read_csv('data\\EUR_USD_new.csv'), 'open': time(0,1), 'close': time(23,59)},
    {'name': 'CAD_USD', 'data': pd.read_csv('data\\CAD_USD_new.csv'), 'open': time(0,1), 'close': time(23,59)},
    {'name': 'DAX', 'data': pd.read_csv('data\\DAX.csv'), 'open': time(12,00), 'close': time(23,59)},
    {'name': 'FORD', 'data': pd.read_csv('data\\FORD.csv'), 'open': time(12,00), 'close': time(23,59)}
]

CURRENCIES=[]

ORDER_VAL = 50000
START_CASH = 500000
FINAL_DATE = date(2018, 8, 4)

# Given a data frame with tweets and a series with one number to optimize on,
# simulate a trade with the data given
def normalize(df, colName):
    for index, row in df.iterrows():
        if row[colName] < 0:
            df.at[index, colName] = row[colName]/abs(df[colName].min())
        elif row[colName] > 0:
            df.at[index, colName] = row[colName]/df[colName].max()

def preprocessDf(df):
    df.Date = [pd.to_datetime(d) for d in df.Date]
    dates = [pd.to_datetime(d) for d in df.Date] 
    normalize(df, 'SentimentNorm')
    df.reset_index(drop=True, inplace=True)

def getStock(name):
    for stock in STOCKS:
        if stock['name'] == name:
            return stock
#Returns a list of date objects
def getTradingDates(tweetDf, hold):
    numDaysToTrade =( tweetDf.Date[len(tweetDf.Date) -1].date() + timedelta(days=hold+5) - tweetDf.Date[0].date() ).days
    simulation_dates = [tweetDf.Date[0].date() + timedelta(days=d) for d in range(0, numDaysToTrade )]

    return simulation_dates

def getMarketStatus(timestamp, stock):
    t = timestamp.time()
    
    #Check if time is within Trading hours
    if timestamp.weekday() >= 5 or str(timestamp.date()) not in set(stock['data'].Date):
        return "holiday"
    elif t < stock['open']:
        return "opening"
    elif t > stock['close']:
        return "closed"
    else:
        return "open"

def openPrice(date, stock):
    if str(date) not in set(stock['data'].Date):
        return openPrice(date + timedelta(days=1), stock)
    else:
        return stock['data'][stock['data'].Date == str(date)].iloc[0].Open
def closePrice(date, stock):
    if str(date) not in set(stock['data'].Date):
        return closePrice(date + timedelta(days=1), stock)
    else:
        if stock['name'] not in ['EUR_USD', "CAD_USD"]:
            return stock['data'][stock['data'].Date == str(date)].iloc[0].Close 
        else:
            return openPrice(date + timedelta(days=1), stock)


def buy(simData, tstamp, hold, stock):
    status = getMarketStatus(tstamp, stock)
    index = simData['Date'].index(tstamp.date())
    
    if status != "holiday" and status != 'closed':
        simData['Value'][index] -= ORDER_VAL
        simData["totalBuys"] += 1
        if status == "opening" :
            stock_bought = ORDER_VAL / openPrice(tstamp.date(), stock)
            sell_val = stock_bought * openPrice(tstamp.date() + timedelta(days=hold), stock)
            simData['Value'][index + hold] += sell_val
        elif status == "open":
            stock_bought = ORDER_VAL / closePrice(tstamp.date(), stock)
            sell_val = stock_bought * closePrice(tstamp.date() + timedelta(days=hold), stock)
            simData['Value'][index + hold] += sell_val 
        
        if sell_val > ORDER_VAL:
            simData['goodBuys'] += 1
    #if market is closed, try trading the next day       
    else: 
        buy(simData, tstamp.replace(hour=5, minute=0) + timedelta(days=1), hold, stock )

def short(simData, tstamp, hold, stock):
    status = getMarketStatus(tstamp, stock)
    index = simData['Date'].index(tstamp.date())
    

    if status != "holiday" and status != "closed":
        simData['Value'][index] += ORDER_VAL
        simData["totalShorts"] += 1
        buy_val = 0
        if status == "opening":
            stock_sold = ORDER_VAL / openPrice(tstamp.date(),stock )
            buy_val = stock_sold * openPrice(tstamp.date() + timedelta(days=hold), stock)
            simData['Value'][index + hold] -= buy_val
        elif status == "open":
            stock_sold = ORDER_VAL / closePrice(tstamp.date(), stock) 
            buy_val = stock_sold * closePrice(tstamp.date() + timedelta(days=hold), stock)
            simData['Value'][index + hold] -= buy_val
        
        if buy_val < ORDER_VAL:
            simData['goodShorts'] += 1
    else: 
        short(simData, tstamp.replace(hour=5, minute=0) + timedelta(days=1), hold, stock)

def printResult(result, hold, threshhold):
    print "--------%AGE CORRECT--------" + "HOLD(" + str(hold) + "), THRESHHOLD: " + str(threshhold)
    print "BUYS: " + str(result['goodBuys']) + "  out of " + str(result['totalBuys'])
    print "SHORTS: " + str(result['goodShorts']) + "  out of " + str(result['totalShorts'])

def simulateTrade(tweetDf, stock, hold, buyThreshhold, shortThreshold):
    normalize(tweetDf, 'SentimentNorm')
    tweetDf.Date = [pd.to_datetime(d) for d in  tweetDf.Date]
    dates = [pd.to_datetime(d) for d in  tweetDf.Date] 
    tweetDf =tweetDf.sort_values(by='Date')
    tweetDf.reset_index(drop=True, inplace=True)

    simDates = getTradingDates(tweetDf, hold)
  
    result = {
        'Date': simDates,
        'Value': [0] * len(simDates),
        'Movement': [0] * len(simDates),
        'totalBuys': 0,
        'totalShorts' : 0,
        'goodBuys': 0,
        'goodShorts': 0
        
    }
    
    gt = 1.1
    gy = -0.8
    #For each tweet, checks if data indicates trade, 
    #sets predicted movement for that day and change in fund value 
    for index, row in tweetDf.iterrows():
        if (row['Date'].date() + timedelta(days=hold)) >= FINAL_DATE :
            continue

        if row['SentimentNorm'] >= gt and buyThreshhold>gt-0.1:
            print "Sentiment: " + str(row['SentimentNorm'])
            print row['Text']

        if row['SentimentNorm'] <= gy and shortThreshold>gy+0.1:
            print "Sentiment: " + str(row['SentimentNorm'])
            print row['Text']

        if row['SentimentNorm'] > buyThreshhold:
            #Buy stock 
            result['Movement'][result['Date'].index(row['Date'].date())] = 1
            buy(result, row['Date'], hold, stock)

        elif row['SentimentNorm'] < shortThreshold:
            #Short Stock
            result['Movement'][result['Date'].index(row['Date'].date())] = -1
            short(result, row['Date'], hold, stock)

    for i in range(1, len(result['Value'])):
        result['Value'][i] += result['Value'][i-1]
    
    return result


# tweetDf = pd.read_csv('gcloud.csv')
# tweetDf['SentimentNorm'] = tweetDf['score']*tweetDf['magnitude']
# tweetDf['SentimentNorm']=(tweetDf['SentimentNorm']-tweetDf['SentimentNorm'].mean())/tweetDf['SentimentNorm'].std()

# result = simulateTrade(tweetDf, STOCKS[0], 4, 0.8, -0.7 )
# for i in range(0,len(result['Date'])): 
#     print "Date: " + str(result['Date'][i]) + ' Value: ' + str(result['Value'][i]) + "Move: " + str(result['Movement'][i])

# print "Buys: " + str(result['goodBuys'])  + " / "  + str(result['totalBuys']) 
# print "Shorts: " + str(result['goodShorts'])  + " / "  + str(result['totalShorts']) 
# print sum(result['Value'])


