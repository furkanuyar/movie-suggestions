import tweepy
import random
import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import api
from settings import constants


def get_suitable_users():
    trend_topics = [trend['name'] for trend in api.trends_place(1)[0]['trends']]
    trend_topics = list(filter(lambda hashtag: len(hashtag) == len(hashtag.encode('utf-8')), trend_topics))
    hashtag = random.choice(trend_topics)
    print('Chosen hashtag:', hashtag)

    tweets = tweepy.Cursor(api.search, q=hashtag).items(constants.SEARCH_TWEET_LIMIT)
    users = list(map(lambda record: record.user, tweets))
    suitable_users = list(
        filter(lambda user: user.friends_count > constants.MIN_FRIENDS_LIMIT
                            and constants.MIN_FOLLOWERS_LIMIT < user.followers_count < constants.MAX_FOLLOWERS_LIMIT
                            and re.match(constants.REAL_USER_PATTERN, user.name)
                            and not len(re.findall('\d', user.screen_name)) > constants.MIN_USERNAME_NUMBER_COUNT, users))

    print('Suitable user count:', len(suitable_users))

    suitable_user_ids = []

    for user in suitable_users:
        tweets = api.user_timeline(user.id)
        # checks user has any own tweet without retweet
        if any([not bool(tweet._json.get('retweeted_status', False)) for tweet in tweets]):
            suitable_user_ids.append(user.id)

    if not len(suitable_user_ids):
        return get_suitable_users()

    return suitable_user_ids


suitable_user_ids = get_suitable_users()
user_id = random.choice(suitable_user_ids)
api.create_friendship(user_id)
print('Followed user_id', user_id)
