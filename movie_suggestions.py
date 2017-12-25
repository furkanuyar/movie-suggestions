import re
import os
import sys
import urllib2
import requests
from requests_oauthlib import OAuth1
from twitter_media_upload import async_upload
from imdbpie import Imdb

POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

CONSUMER_KEY = 'your-consumer-key'
CONSUMER_SECRET = 'your-consumer-secret'
ACCESS_TOKEN = 'your-access-token'
ACCESS_TOKEN_SECRET = 'your-access-token-secret'

imdb = Imdb()
least_rating = 7

oauth = OAuth1(CONSUMER_KEY,
               client_secret=CONSUMER_SECRET,
               resource_owner_key=ACCESS_TOKEN,
               resource_owner_secret=ACCESS_TOKEN_SECRET)


class MovieSuggestion():
    def __init__(self):
        self.movie = None
        self.rating = None
        self.total_bytes = None
        self.media_id = None
        self.tweet = None
        self.duration = None

    def get_movie(self):
        """
        Gets a random movie from IMDB and suggestmovie.net
         
        """
        html_for_movie_id = urllib2.urlopen("http://suggestmovie.net").read()
        pattern = "http://www.imdb.com/title/tt(\\d+)"
        object_id = re.findall(pattern, html_for_movie_id)[0]
        movie = imdb.get_title_by_id("tt{}".format(object_id))
        if movie.type == 'tv_series':
            movie = self.get_movie()
        return movie

    def get_trailer_or_poster_url(self):
        """
        If a movie has a trailer, gets trailer, otherwise gets movie's poster.
          
        """
        movie = self.movie

        if not movie.trailers:
            return 'image', movie.poster_url

        return 'video', movie.trailers[0]['url']

    def download_file(self, url, file_name, file_type):
        """
        Downloads movie's poster or trailer.
         
        """
        print("File is downloading...")
        self.file_format = 'mp4' if file_type == 'video' else 'jpg'
        self.file_name = ('.').join([file_name, self.file_format])
        r = requests.get(url, stream=True)
        with open(self.file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        self.total_bytes = os.path.getsize(self.file_name)

    def prepare_tweet(self):
        """
        Prepare movie's tweet with movie's genres, year, imdb rating and name.

        """
        print("Tweet is being prepared.")
        movie = self.movie
        base = "\xF0\x9F\x8E\xA5: {0}   \xF0\x9F\x93\x85: {1}".format(movie.title, movie.year)
        option = "  #comingsoon" if not self.rating else "  \xE2\xAD\x90: {0}  ".format(movie.rating)
        genre_hashtags = ['#{0}'.format(genre.lower().replace('-', '')) for genre in movie.genres]
        removed_signs = ['-', ' ', ':', '\'']
        movie_name = movie.title
        for sign in removed_signs:
            if sign in movie_name:
                movie_name = movie_name.replace(sign, '')
        hashtags = ['#{}'.format(movie_name), '#movie']
        hashtags.extend(genre_hashtags)
        self.tweet = ' '.join([base, option, ' '.join(hashtags)])

    def send_tweet(self, media_id):
        """
        Sends tweet with movie's poster or trailer.
         
        """
        self.prepare_tweet()
        request_data = {
            'status': self.tweet,
            'media_ids': media_id
        }

        requests.post(url=POST_TWEET_URL, data=request_data, auth=oauth)
        os.remove(self.file_name)
        print("Tweet has sent successfully.")

    def sending_process(self, file_type=None, file_url=None):
        """
        Media uploading and sending tweet process.

        """

        file_type, file_url = self.get_trailer_or_poster_url() if not file_type else (file_type, file_url)
        print("Movie will be shared with {} ").format(file_type)
        movie_name = self.movie.title.lower().replace(' ', '_')
        self.download_file(file_url, movie_name, file_type)
        media_upload = async_upload.VideoTweet(self.file_name, oauth)
        media_id = media_upload.upload_init(file_type)
        media_upload.upload_append()
        try:
            media_upload.upload_finalize()
        except:
            self.sending_process(file_type='image', file_url=self.movie.poster_url)

        self.send_tweet(media_id)
        sys.exit()

    def run(self):
        """
        Runs and tweets one random movie with trailer or movie poster.
         
        """
        self.movie = self.get_movie()
        print("Movie Name: {}").format(self.movie.title)
        self.rating = bool(self.movie.rating)

        if self.rating and self.movie.rating < least_rating:
            print("Movie's rating({}) is less than least rating({})").format(self.movie.rating, least_rating)
            return self.run()

        self.sending_process()


if __name__ == '__main__':
    MovieSuggestion().run()

