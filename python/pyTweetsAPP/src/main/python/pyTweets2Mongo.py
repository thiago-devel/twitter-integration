import requests
import jprops
import datetime
import json
from dateutil import parser

with open('../resources/config.properties') as fp:
    properties = jprops.load_properties(fp)

encoded_hashtags = (
    (
        str(properties['tweeter.api.endpoint.search.query.hashtags'])
    ).replace('#','%23')
).replace(',', '%20OR%20')

now = datetime.datetime.now()

'''
url =   'https://' + str(properties['tweeter.api.host']) + ':' + str(properties['tweeter.api.port'])    \
        + str(properties['tweeter.api.baseurl'])    \
        + str(properties['tweeter.api.endpoint.search'])    \
        + '?q=' \
        + encoded_hashtags  \
        + '&result_type=' + str(properties['tweeter.api.endpoint.search.result_type'])  \
        + '&until=' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) \
        + '&include_entities=' + str(properties['tweeter.api.endpoint.search.include_entities'])    \
        + '&count=' + str(properties['tweeter.api.endpoint.search.count'])
'''        
url =   'https://' + str(properties['tweeter.api.host']) + ':' + str(properties['tweeter.api.port'])    \
        + str(properties['tweeter.api.baseurl'])    \
        + str(properties['tweeter.api.endpoint.search'])    \
        + '?q=' \
        + encoded_hashtags  \
        + '&result_type=' + str(properties['tweeter.api.endpoint.search.result_type'])  \
        + '&include_entities=' + str(properties['tweeter.api.endpoint.search.include_entities'])    \
        + '&count=' + str(properties['tweeter.api.endpoint.search.count'])

twitter_search_response = requests.get(url, headers={"authorization":str(properties['tweeter.api.endpoint.header.authorization'])}).json()

pre_hashtags = str(properties['tweeter.api.endpoint.search.query.hashtags']).split(',')
hashtags = []
for tag in pre_hashtags:
    stag = list(tag)
    del(stag[0])
    hashtags.append("".join(stag))
    
tweets = []
statuses = []
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
                tags.append(tag)    
            tweet['hashtags'] = tags
            tweets.append(tweet)
            status['created_at'] = date
            statuses.append(status)

result_dicio = {}
result_dicio['statuses'] = statuses            
result_dicio['search_metadata'] = twitter_search_response['search_metadata']

#print 'All the retrieved data: ' + (json.dumps(result_dicio))
            
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
    
#print (json.dumps(user_tweets))
    
users = {}
for ut in user_tweets:
    counts = int(ut['followers_count'])
    users[counts] = ut

i = 0    
data_of_five_most_followed_users = []
for key in sorted(users, reverse=True):
    if (i > 4):
        break
    else:
        #print "%s: %s" % (key, users[key])
        data_of_five_most_followed_users.insert(i, users[key])
        i += 1
        
#print 'Data of the most fallowed users: ' + (json.dumps(data_of_five_most_followed_users, default=json_util.default))
print 'Data of the most fallowed users: '
print (json.dumps(data_of_five_most_followed_users, indent=4, sort_keys=False, default=str))




