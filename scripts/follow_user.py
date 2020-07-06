import tweepy
import random
import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import api
from settings import constants


def get_user_details(tweets):
    own_tweet_status = None
    hashtags = []
    for tweet in tweets:
        if not own_tweet_status:
            own_tweet_status = not bool(tweet._json.get('retweeted_status', False))
        text = tweet.retweeted_status.full_text if tweet._json.get('retweeted_status', False) else tweet.full_text
        tweet_hashtags = re.findall('#(\w+)', text)
        hashtags.extend(tweet_hashtags)

    return own_tweet_status, hashtags


def get_hashtag_weights(hashtags):
    tweet_hashtag_weights = {}
    for hashtag in hashtags:
        tweet_hashtag_weights[hashtag] = \
            tweet_hashtag_weights[hashtag] + 1 if tweet_hashtag_weights.get(hashtag, None) else 1

    return tweet_hashtag_weights


def get_suitable_user_ids(suitable_users):
    suitable_user_ids = []

    for user in suitable_users:
        tweets = api.user_timeline(user.id, tweet_mode='extended')
        # checks user has any own tweet without retweet
        own_tweet_status, hashtags = get_user_details(tweets)
        tweet_hashtag_weights = get_hashtag_weights(hashtags)
        max_weight = max(tweet_hashtag_weights.values()) if len(tweet_hashtag_weights.values()) else None

        if not max_weight or max_weight and max_weight < constants.MAX_SAME_HASHTAG_USAGE_LIMIT and own_tweet_status:
            suitable_user_ids.append(user.id)

    return suitable_user_ids


def filter_suitable_users(users):
    return list(
        filter(lambda user: user.friends_count > constants.MIN_FRIENDS_LIMIT
                            and constants.MIN_FOLLOWERS_LIMIT < user.followers_count < constants.MAX_FOLLOWERS_LIMIT
                            and user.description and not user.default_profile_image
                            and re.match(constants.REAL_USER_PATTERN, user.name)
                            and not len(re.findall('\d', user.screen_name)) > constants.MIN_USERNAME_NUMBER_COUNT,
               users))


def get_suitable_users():
    trend_topics = [trend['name'] for trend in api.trends_place(1)[0]['trends']]
    trend_topics = list(filter(lambda hashtag: len(hashtag) == len(hashtag.encode('utf-8')), trend_topics))
    hashtag = random.choice(trend_topics)
    print('Chosen hashtag:', hashtag)

    tweets = tweepy.Cursor(api.search, q=hashtag).items(constants.SEARCH_TWEET_LIMIT)
    users = list(map(lambda record: record.user, tweets))
    suitable_users = filter_suitable_users(users)
    print('Suitable user count:', len(suitable_users))

    suitable_user_ids = get_suitable_user_ids(suitable_users)

    if not len(suitable_user_ids):
        return get_suitable_users()

    return suitable_user_ids


suitable_user_ids = get_suitable_users()
user_id = random.choice(suitable_user_ids)
api.create_friendship(user_id)
print('Followed user_id', user_id)
