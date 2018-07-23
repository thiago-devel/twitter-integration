import requests
import jprops
import datetime
import json
from dateutil import parser

def datetimeJsonConverter(obj):
    if isinstance(obj, datetime.datetime):
        return "{}-{}-{}T{}:{}:{}.{}{}".format(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond, obj.tzinfo)       

def loadProperties():
    with open('../resources/config.properties') as fp:
        properties = jprops.load_properties(fp)
    return properties

def encodeHashtags(properties):
    return (
        (
            str(properties['tweeter.api.endpoint.search.query.hashtags'])
        ).replace('#','%23')
    ).replace(',', '%20OR%20')
    
def prepareRequestUrl(properties):        
    return 'https://' + str(properties['tweeter.api.host']) + ':' + str(properties['tweeter.api.port'])    \
        + str(properties['tweeter.api.baseurl'])    \
        + str(properties['tweeter.api.endpoint.search'])    \
        + '?q=' \
        + encoded_hashtags  \
        + '&result_type=' + str(properties['tweeter.api.endpoint.search.result_type'])  \
        + '&include_entities=' + str(properties['tweeter.api.endpoint.search.include_entities'])    \
        + '&count=' + str(properties['tweeter.api.endpoint.search.count'])    

def loadHashtags(properties):    
    pre_hashtags = str(properties['tweeter.api.endpoint.search.query.hashtags']).split(',')
    hashtags = []
    for tag in pre_hashtags:
        stag = list(tag)
        del(stag[0])
        hashtags.append("".join(stag))
    return hashtags

def loadFilteredTweetsData(twitter_search_response, hashtags):
    filtered_tweets_data = {}
    statuses = []
    tweets = []
    for status in twitter_search_response['statuses']:
        for hashtag in status['entities']['hashtags']:
            if hashtag['text'] in hashtags:
                tweet = {}
                ds = status['created_at']
                date = parser.parse(ds)
                tweet['created_at'] = date
                tweet['id'] = status['id']
                tweet['id_str'] = status['id_str']
                tweet['text'] = status['text']
                tweet['retweet_count'] = status['retweet_count']
                tweet['user_id'] = int(status['user']['id'])
                tags = []
                for tag in status['entities']['hashtags']:
                    tags.append(tag['text'])    
                tweet['hashtags'] = tags
                tweets.append(tweet)
                status['created_at'] = date
                statuses.append(status)
    
    filtered_tweets_data['tweets'] = tweets            
    filtered_tweets_data['statuses'] = statuses            
    filtered_tweets_data['search_metadata'] = twitter_search_response['search_metadata']
    return filtered_tweets_data

def loadUserTweets(statuses, tweets):
    user_tweets = []
    for status in statuses:
        user = {}
        user_id = int(status['user']['id'])
        user['id'] = user_id
        user['id_str'] = status['user']['id_str']
        user['description'] = status['user']['description']
        user['name'] = status['user']['name']
        user['screen_name'] = status['user']['screen_name']
        user['locaion'] = status['user']['location']
        user['verified'] = status['user']['verified']
        user['lang'] = status['user']['lang']
        user['followers_count'] = status['user']['followers_count']
        user['friends_count'] = status['user']['friends_count']
        user['statuses_count'] = status['user']['statuses_count']
        user['favourites_count'] = status['user']['favourites_count']
        user['profile_image_url_https'] = status['user']['profile_image_url_https']
        tws = []
        for tweet in tweets:
            if user_id == tweet['user_id']:
                tws.append(tweet)
        user['tweets'] = tws
        user_tweets.append(user)
    return user_tweets

def retrieveFiveMostFollowedUsers(user_tweets):
    data_of_five_most_followed_users = []
    users = {}
    for ut in user_tweets:
        counts = int(ut['followers_count'])
        users[counts] = ut
    
    i = 0    
    for key in sorted(users, reverse=True):
        if (i > 4):
            break
        else:
            #print "%s: %s" % (key, users[key])
            data_of_five_most_followed_users.insert(i, users[key])
            i += 1
    return data_of_five_most_followed_users


properties = loadProperties()
encoded_hashtags = encodeHashtags(properties)
now = datetime.datetime.now()
url = prepareRequestUrl(properties)
twitter_search_response = requests.get(url, headers={"authorization":str(properties['tweeter.api.endpoint.header.authorization'])}).json()
hashtags = loadHashtags(properties)
filtered_tweets_data = loadFilteredTweetsData(twitter_search_response, hashtags)
tweets = filtered_tweets_data['tweets']
statuses = filtered_tweets_data['statuses']
user_tweets = loadUserTweets(statuses, tweets)  
data_of_five_most_followed_users = retrieveFiveMostFollowedUsers(user_tweets)
#print 'All the retrieved data: ' + (json.dumps(filtered_tweets_data))
            
    
#print (json.dumps(user_tweets))

#print 'Data of the most fallowed users: ' + (json.dumps(data_of_five_most_followed_users, default=json_util.default))
print 'Data of the most fallowed users: '
print (json.dumps(data_of_five_most_followed_users, indent=4, sort_keys=False, default=datetimeJsonConverter))
