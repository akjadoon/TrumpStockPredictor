from twitter import Twitter
from tqdm import tqdm
from textblob import TextBlob
import csv
import json

SINCE_TWEET_ID = "806134244384899072"
twitter = Twitter(logs_to_cloud=False)

with open('all_ids.json') as f:
    OLD_TWEET_IDS = json.load(f)

def scrapeFromApi():
    tweets = twitter.get_tweets(SINCE_TWEET_ID)
    tweet_data = []

    #Collect Trump tweets about China
    for tweet in tqdm(tweets):
        text = twitter.get_tweet_text(tweet)
        if isAboutChina(text):
            tweet_data.append((getTweetSentiment(text), getTweetTimestamp(tweet)))

    
    headers = ("Sentiment", "Date")
    with open('sentiment.csv','wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',' )
        writer.writerow(headers)

        writer.writerows(tweet_data)

def scrapeFromTweetIds(TWEET_IDS):
    tweet_data = []

    for tweet_id in tqdm(TWEET_IDS):
        tweet = twitter.get_tweet(tweet_id)
        text = twitter.get_tweet_text(tweet)

        if isAboutChina(text):
            tweet_data.append((getTweetSentiment(text), str(getTweetTimestamp(tweet))))

    headers = ("Sentiment", "Date")
    with open('sentiment_old.csv','wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',' )
        writer.writerow(headers)

        writer.writerows(tweet_data)


def getTweetSentiment(tweet_text):
        sentiment = TextBlob(tweet_text).sentiment.polarity

        return sentiment
def getTweetTimestamp(tweet):
    return tweet["created_at"]

def saveTweetTextAndTstamp(TWEET_IDS):
    tweet_data = []
    tweets = twitter.get_tweets(SINCE_TWEET_ID)

    iters = 0 
    
    for tweet in tqdm(tweets):
        text = twitter.get_tweet_text(tweet)
        text = text.encode('ascii', 'ignore').decode('ascii')
        tweet_data.append((text, str(getTweetTimestamp(tweet))))


    for tweet_id in tqdm(TWEET_IDS):
        
        tweet = twitter.get_tweet(tweet_id)
        text = twitter.get_tweet_text(tweet)
        text = text.encode('ascii', 'ignore').decode('ascii')

        tweet_data.append((text, str(getTweetTimestamp(tweet))))

    headers = ("Text", "Date")
    with open('tweet_data.csv','wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',' )
        writer.writerow(headers)

        writer.writerows(tweet_data)

saveTweetTextAndTstamp(OLD_TWEET_IDS)