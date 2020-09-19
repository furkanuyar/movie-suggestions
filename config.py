# -*- coding: utf-8 -*-

import os
import tweepy
from requests_oauthlib import OAuth1
from imdbpie import Imdb

imdb = Imdb()

MOVIE_SUGGESTION_SOURCE = os.environ.get('MOVIE_SUGGESTION_SOURCE')
MOVIE_QUOTE_SOURCE = os.environ.get('MOVIE_QUOTE_SOURCE')
TWITTER_PASSWORD = os.environ.get('TWITTER_PASSWORD')
GECKODRIVER_PATH = os.environ.get('GECKODRIVER_PATH')
oauth = OAuth1(os.environ.get('CONSUMER_KEY'),
               client_secret=os.environ.get('CONSUMER_SECRET'),
               resource_owner_key=os.environ.get('ACCESS_TOKEN'),
               resource_owner_secret=os.environ.get('ACCESS_TOKEN_SECRET'))

auth = tweepy.OAuthHandler(os.environ.get('CONSUMER_KEY'), os.environ.get('CONSUMER_SECRET'))
auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth, wait_on_rate_limit=True)

