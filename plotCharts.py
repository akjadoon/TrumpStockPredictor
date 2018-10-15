import pandas as pd 
from datetime import date, time, timedelta

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

from simulate import simulateTrade, getStock
from extract_topic import KEYWORDS, extractTweets

sentDfs = []
tweetDf = pd.read_csv('data\\topical_tweet_data.csv')

gcloudDf = pd.read_csv('gcloud.csv')
gcloudDf['SentimentNorm'] =  ((np.abs(gcloudDf['magnitude'] * gcloudDf['score'])).pow(1./2)) * ((gcloudDf['score'] > 0)*2 -1)
sentDfs.append({'name':'gcloud', 'data': gcloudDf})

textblobDf = pd.read_csv('textblob.csv')
textblobDf['SentimentNorm'] = textblobDf['sentiment']
sentDfs.append({'name': 'textblob','data' : textblobDf})

aylienDf = pd.read_csv('aylien.csv')
aylienDf['SentimentNorm'] = aylienDf['sentiment']
sentDfs.append({'name': 'aylien', 'data': aylienDf})

def plotHeatmap(tweetDf, stock, abs_sent_min, abs_sent_max, hold_max, showRates=False, save=False, analyzer=None):


    print(len(tweetDf))
    print(stock['name'])
    
    
    SENT_STEP = 0.1
    #Number of values of input vars to plot for
    sent_num = int((abs_sent_max-abs_sent_min)/SENT_STEP+1)
    

    #Axis Tick Lables
    x_labels = list(reversed([str(abs_sent_min + SENT_STEP*x) for x in range(0, sent_num)])) + [str(-(abs_sent_min + SENT_STEP*x)) for x in range(0, sent_num)]

    y_labels = [str(x+1) for x in range(0, hold_max)]

    #Array of performance metric %age correct trades
    results = np.zeros(shape=(sent_num*2, hold_max))
    #Strings of good trades / total trades
    rates = [[""] * hold_max for i in range(sent_num*2)]

    sent_thresh = abs_sent_min
    hold = 1

    ########### Simulate Trades for different param vals ##############
    for x in range(0, sent_num): 
        for y in range(0, hold_max):
            sim = simulateTrade(tweetDf, stock, hold, sent_thresh, -sent_thresh)
            goodBuyPercentage = math.floor(100* sim['goodBuys']/float(sim['totalBuys']))
            goodShortPercentage = math.floor(100* sim['goodShorts']/float(sim['totalShorts']))
            results[sent_num + x][y] = goodBuyPercentage
            results[sent_num -1 -x][y] = goodShortPercentage
            rates[sent_num + x][y] = "(" + str(sim['goodBuys']) + "/" + str(sim['totalBuys']) + ")"
            rates[sent_num -1 -x][y] = "(" + str(sim['goodShorts']) + "/" + str(sim['totalShorts']) + ")"
            hold += 1

        hold = 1    
        sent_thresh += SENT_STEP
    
    #reverse the result arrays so that the data is plotted from min to max sentiment on y_axis
    results = results[::-1]
    rates = list(reversed(rates))

    #############  Plot the heatmap ###############
    fig, ax = plt.subplots()
    fig.set_size_inches(12,10)
 
    im = ax.imshow(results, cmap='copper')

    ax.set_xticks(np.arange(len(y_labels)))
    ax.set_yticks(np.arange(len(x_labels)))

    ax.set_xticklabels(y_labels)
    ax.set_yticklabels(x_labels)

    ax.tick_params(axis='y', length= 0)
    ax.set_ylabel('Tweet Sentiment')
    ax.set_xlabel('Hold Days')


    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")

    for i in range(len(x_labels)):
        for j in range(len(y_labels)):
            string = str(results[i, j]) + "%\n" 
            if showRates:
                string +=  rates[i][j]
            text = ax.text(j, i, string,
                       ha="center", va="center", color="w", size="x-small")

    # ax.set_title("Sentiment Threshold vs Hold days heat map for " + stock['name'])
    fig.tight_layout()

    if save:
        plt.savefig(analyzer + "//" + stock['name'] + '.png')

    plt.show()

def plotFundsOverTime(stock,tweetDf,abs_sent_max, hold_max, plotStockPrice=False):
    plt.figure()
    plt.xlabel('Date')
    plt.ylabel('Funds')

    colors=['red', 'green', 'blue','purple', 'black', 'grey', 'orange']
    for i in range(1, hold_max+1):
        tradeSim = simulateTrade(tweetDf, stock, i, abs_sent_max, -abs_sent_max )
        plt.plot(tradeSim['Date'], tradeSim['Value'], c=colors[i] , label="Hold=" +str(i)+ " Days")

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
            ncol=2, mode="expand", borderaxespad=0.)
    # plt.plot(dates_ci, df_chinaindex.Open)
    plt.show()

def plotMovement(tweetDf,stock, abs_sent, hold):
    plt.figure()
    plt.xlabel('Date')
    plt.ylabel('Movement')
    
    tradeSim = simulateTrade(tweetDf, stock, hold, abs_sent, -abs_sent)
    plt.plot(tradeSim['Date'],tradeSim['Movement'])


    norm_open = (stock['data']["Open"] - stock['data']["Open"].min())/(stock['data']["Open"].max()- stock['data']["Open"].min()) * 2 -1


    dates = [pd.to_datetime(d) for d in  stock['data']["Date"]] 
    plt.plot(dates,norm_open , c='red')


def simTradeForAllParams(tweetDf, stock, max_sent, rates=False):
    HOLD_VALS = 5
    SENT_VALS = int(max_sent*10) -1
    result = [[""] * SENT_VALS for i in range(HOLD_VALS)]

    for i in range(0, HOLD_VALS):
        for j in range(0, SENT_VALS):
            sim = simulateTrade(tweetDf, stock, i + 1, 0.2 + j*0.1, -0.2-j*0.1)
            performanceString = str(sim['goodBuys']+sim['goodShorts']) + "/" + str(sim['totalBuys']+sim['totalShorts'])
            if rates:
                if sim['totalBuys'] + sim['totalShorts'] > 0 :
                   performanceString += "(" + str(int((float(sim['goodBuys']+sim['goodShorts']))/(sim['totalBuys']+sim['totalShorts'])*100)) + "%)"
                else:
                    performanceString += "(0/0)"
            result[i][j] = performanceString

    return result


def makeSingleSummary(stock, max_sent):
    row_names = []
    col_names = [str(x*0.1 + 0.2) for x in range(0, int(max_sent*10)-1) ]
    cell_text = []
    
    for sent_analyzer in sentDfs:
        for i in range(5):
            row_names.append(sent_analyzer['name'] + "H=" + str(i+1))

        if stock['name'] == 'SSE' or stock['name'] == 'HSI':
            matchWords= KEYWORDS['China']
        elif stock['name'] == 'N225':
            matchWords= KEYWORDS['Japan']
        elif stock['name'] == 'KS11':
            matchWords= KEYWORDS['Korea']
        elif stock['name'] == 'BSESN':
            matchWords= KEYWORDS['India']
        elif stock['name'] == 'MICEX':
            matchWords= KEYWORDS['Russia']
        elif stock['name'] in ['STOXX50E', 'EUR_USD', 'DAX']:
            matchWords=KEYWORDS['Europe']
        elif stock['name'] == ['CAD_USD']:
            matchWords=KEYWORDS['Canada']
        elif stock['name'] == ['FORD']:
            matchWords=KEYWORDS['Ford']


        tweetDf = extractTweets(sent_analyzer['data'], matchWords)
        cell_text += simTradeForAllParams(tweetDf, stock, max_sent)

    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False) 
    ax.yaxis.set_visible(False)
    

    row_labels = row_names
    col_tweetDf


    plt.subplots_adjust(left=0.5, right=0.7, top=0.5, bottom=0.2)
    the_table = plt.table(cellText=cell_text,
    colWidths = [0.5]*len(col_labels),
    rowLabels=row_labels, colLabels=col_labels,
    loc='center' , label='name', fontsize=30)
    plt.title(stock['name'], y=1.88)
    plt.show()

# makeSingleSummary(getStock('SSE'), 0.9)

# makeSingleSummary(getStock('HSI'), 0.9)
# makeSingleSummary(getStock('KS11'), 0.9)

# makeSingleSummary(getStock('BSESN'), 0.9)
sentDfNum= 2
analyzer='aylien'
tweetDf = extractTweets(sentDfs[sentDfNum]['data'], KEYWORDS['Europe'])
plotHeatmap(tweetDf,getStock('STOXX50E'), 0.1, 0.9, 5,  showRates=True, save=True, analyzer=analyzer)
plotHeatmap(tweetDf,getStock('EUR_USD'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)
plotHeatmap(tweetDf,getStock('DAX'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)

tweetDf = extractTweets(sentDfs[sentDfNum]['data'], KEYWORDS['Canada'])
plotHeatmap(tweetDf,getStock('CAD_USD'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)

tweetDf = extractTweets(sentDfs[sentDfNum]['data'], KEYWORDS['Ford'])
plotHeatmap(tweetDf,getStock('FORD'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)

tweetDf = extractTweets(sentDfs[sentDfNum]['data'], KEYWORDS['China'])
plotHeatmap(tweetDf,getStock('SSE'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)
plotHeatmap(tweetDf,getStock('HSI'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)

tweetDf = extractTweets(sentDfs[sentDfNum]['data'], KEYWORDS['Russia'])
plotHeatmap(tweetDf,getStock('MICEX'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)

tweetDf = extractTweets(sentDfs[sentDfNum]['data'], KEYWORDS['Korea'])
plotHeatmap(tweetDf,getStock('KS11'), 0.1, 0.9, 5, showRates=True, save=True, analyzer=analyzer)