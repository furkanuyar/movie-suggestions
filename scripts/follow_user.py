import tweepy
import random
import sys
import os

#sys.path.append('../config')
#sys.path.append('../settings')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import api
from settings import constants

trend_topics = [trend['name'].encode('ascii', 'ignore') for trend in api.trends_place(1)[0]['trends']]
hashtags = filter(lambda trend_topic: len(trend_topic) > constants.TREND_TOPIC_LENGTH_LIMIT, trend_topics)
hashtag = random.choice(hashtags)
print 'Chosen hashtag:', hashtag

tweets = tweepy.Cursor(api.search, q=hashtag).items(constants.SEARCH_TWEET_LIMIT)

suitable_users = filter(
    lambda record:
    record.user.friends_count > constants.MIN_FRIENDS_LIMIT
    and record.user.followers_count > constants.MIN_FOLLOWERS_LIMIT
    and record.user.followers_count < constants.MAX_FOLLOWERS_LIMIT, tweets)
print 'Suitable user count:', len(suitable_users)

suitable_user_ids = map(lambda record: record.user.id, suitable_users)
user_id = random.choice(suitable_user_ids)
api.create_friendship(user_id)
print('Followed user_id', user_id)
