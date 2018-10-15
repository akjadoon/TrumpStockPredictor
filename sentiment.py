#General libraries for data processing
import pandas as pd 
import re
from tqdm import tqdm
import json
import time 

from watson_developer_cloud import ToneAnalyzerV3
from textblob import TextBlob

from aylienapiclient import textapi

#GCLoud libraries
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


df = pd.read_csv('data\\topical_tweet_data.csv')
#----- Sort Values by Date

#-------Perform sentiment analysis on tweets with different libraries ----
#   Store resulting data in a csv, thik about all the parameteres the analysis
#   gives back and store as a number or mood or something, ideally a single number

### TextBlob

def textBlobAnalyzer():
    dfResult = df.copy()
    dfResult['sentiment'] = 0.0
    
    for index, row in df.iterrows():
        sentiment = TextBlob(row['Text']).sentiment.polarity

        df.at[index, 'sentiment'] = sentiment
        #Gives 2 values, sentimenet polarity 

    df.to_csv('textblob.csv', index=False)


#### GCloud API
def gCloudAnalyzer():
    dfResult = df.copy()
    dfResult['score'] = 0.0
    dfResult['magnitude'] = 0.0

    client = language.LanguageServiceClient()

    for index, row in tqdm(dfResult.iterrows()):
        tweet = row['Text']
        document = types.Document(
            content=tweet,
            type=enums.Document.Type.PLAIN_TEXT
        )

        response = client.analyze_sentiment(document=document, encoding_type='UTF32')

        dfResult.at[index, 'score'] = response.document_sentiment.score
        dfResult.at[index, 'magnitude'] = response.document_sentiment.magnitude

    dfResult.to_csv('gcloud.csv', index=False)

##IBM Watson API
def watsonAnalyzer():
    dfResult = df.copy()
    dfResult['joy'] = 0.0
    dfResult['analytical']= 0.0
    dfResult['confident']=0.0
    dfResult['sadness']=0.0
    dfResult['anger']=0.0
    dfResult['tentative']=0.0

    #Set up Watson Tone API
    tone_analyzer = ToneAnalyzerV3(
        version ='2017-09-21',
        url= "https://gateway.watsonplatform.net/tone-analyzer/api",
        username= "9b29247b-ac9a-47f6-b9fe-cbb942c57b7b",
        password= "RnKsXCMQ0xKq"
    )

    content_type = 'application/json'
        
    # tweets= list(dfResult.Text)
    # tweets = map(lambda text: re.sub(r'http\S+', '', text), tweets)
    # tweets = map(lambda text: text.translate(None, '#@_\\$'), tweets)


    for index, row in tqdm(dfResult.iterrows()):
        text = row['Text']
        response = tone_analyzer.tone({"text": text},content_type,sentences=False)

        time.sleep(1.3)
        for tone in response['document_tone']['tones']:
            dfResult.at[index, tone['tone_id']] =  tone['score']

        
        
    dfResult.to_csv('watson.csv', index=False)

def aylienAnalyzer():
    dfResult = df.copy()
    dfResult['sentiment'] = 0.0

    client = textapi.Client("06de78ad", "4c23ba7a810d74648ac8d00ead55ddaa")

    for index, row in tqdm(dfResult.iterrows()):
        tweet = row['Text']
        response = client.Sentiment({'text': tweet})

        if response['polarity'] == 'negative':
            dfResult.at[index, 'sentiment'] = -response['polarity_confidence']
        elif response['polarity'] == 'positive':
             dfResult.at[index, 'sentiment'] = response['polarity_confidence']
        time.sleep(1.3)
    dfResult.to_csv('aylien.csv', index=False)
   

