# -*- coding: utf-8 -*-

import os
import tweepy
from requests_oauthlib import OAuth1
from imdbpie import Imdb

imdb = Imdb()

MOVIE_SUGGESTION_SOURCE = os.environ['MOVIE_SUGGESTION_SOURCE']
TWITTER_PASSWORD = os.environ['TWITTER_PASSWORD']

oauth = OAuth1(os.environ['CONSUMER_KEY'],
               client_secret=os.environ['CONSUMER_SECRET'],
               resource_owner_key=os.environ['ACCESS_TOKEN'],
               resource_owner_secret=os.environ['ACCESS_TOKEN_SECRET'])

auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth, wait_on_rate_limit=True)
