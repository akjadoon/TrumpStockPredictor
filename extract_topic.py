import pandas as pd 



KEYWORDS = {
    'China':['china','chinese', 'shanghai', 'beijing', 'shenzhen', 'president xi', 'jinping'],
    'Korea':['korea','korean','koreans', 'chairman kim', 'jong un', 'seoul', 'pyongyang', 'jae-in', 'president moon'],
    'Japan':['japan', 'japanese', 'tokyo', 'shinzo'],
    'Singapore':['singapore', 'singaporean','malaysia','halimah'],
    'India':['india', 'indian', 'delhi', 'modi', 'narendra'],
    'Russia':['russia', 'putin', 'vladimir', 'russian', 'moscow', 'russians'],
    'Europe': ['euro', 'europe', 'germany','german', 'merkel', 'eurozone','european', 'france', 'italy'],
    'Canada': ['canada', 'canadian', 'toronto', 'trudeau'],
    'Ford': ['ford']
}



def extractTweets(df, matchWords):
    dfResult=df.copy()
    dfResult = dfResult[dfResult.Text.str.contains('(?i)' + '|'.join(matchWords))]
    return dfResult
    


#Extract all relevant tweets
def getAllRelevantTweets(resultPath):
    dfSource = pd.read_csv('tweet_data.csv')
    allMatchWords=[]
    for key, word_list in KEYWORDS.iteritems():
        allMatchWords += word_list

    extractTweets(dfSource, allMatchWords).to_csv(resultPath, index=False)


getAllRelevantTweets('data\\topical_tweet_data.csv')


