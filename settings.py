from argparse import Namespace

constants = {
    'POST_TWEET_URL': 'https://api.twitter.com/1.1/statuses/update.json',
    'LEAST_RATING': 7,
    'START_LIMIT': 0,
    'DURATION_LIMIT': 140,
    'YEAR_LIMIT': 1980,
    'BEST_VIDEO_QUALITY_FORMAT': 'bestvideo/best',
    'TRAILER_FILE_NAME': 'trailer.mp4',
    'OPTIMIZED_TRAILER_FILE_NAME': 'optimized.mp4',
    'POSTER_FILE_NAME': "poster.jpg",
    'IMDB_ID_PATTERN': "https://www.imdb.com/title/tt(\\d+)",
    'TRAILER_VIDEO_ID_PATTERN': 'src="https://www.youtube.com/embed/(.*)?" ',
    'VIDEO_URL_INITIAL': "https://www.youtube.com/embed/",
    'CAMERA_EMOJI': '\xF0\x9F\x8E\xA5',
    'CALENDAR_EMOJI': '\xF0\x9F\x93\x85',
    'RATING_EMOJI': '\xE2\xAD\x90',
    'USER_NAME': 'suggests_movie',
    'TREND_TOPIC_LENGTH_LIMIT': 5,
    'SEARCH_TWEET_LIMIT': 300,
    'MIN_FRIENDS_LIMIT': 75,
    'MIN_FOLLOWERS_LIMIT': 50,
    'MAX_FOLLOWERS_LIMIT': 400,
    'SCROLL_HEIGHT_LIMIT': 400,
    'SCROLL_PAUSE_TIME': 2,
    'LOGIN_SCREEN_WAIT_TIME': 3,
    'TWITTER_LOGIN_URL': 'https://twitter.com/login',
    'TWITTER_FOLLOWING_URL': 'https://twitter.com/following',
    'UNFOLLOW_NOT_APPLY_LIMIT': 50,
    'UNFOLLOW_SLEEP_TIME_RANGE': [1, 5],
    'UNFOLLOW_APPLY_SLEEP_TIME_RANGE': [5, 10],
    'LOGIN_BUTTON_XPATH': '//*[@id="react-root"]/div/div/div[2]/main/div/div/form/div/div[3]',
    'UNFOLLOW_APPLY_BUTTON_XPATH':
        '//*[@id="react-root"]/div/div/div[1]/div[2]/div/div/div/div[2]/div[2]/div[3]/div[2]/div/span/span'
}

constants = Namespace(**constants)
