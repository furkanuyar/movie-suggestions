# -*- coding: utf-8 -*-

import re
import sys
from urllib.request import urlopen
import requests
import logic
from twitter_media_upload import async_upload
from argparse import Namespace
from settings import constants
from config import MOVIE_SUGGESTION_SOURCE, imdb, oauth


class MovieSuggestion:

    def __init__(self):
        self.movie = None
        self.trailer_url = None

    def get_movie(self):
        """
        Finds a random movie from the movie source,
        gets movie's imdb details and trailer url

        """
        html_content = urlopen(MOVIE_SUGGESTION_SOURCE).read().decode('utf-8')
        imdb_id = re.findall(constants.IMDB_ID_PATTERN, html_content)[0]
        self.trailer_url = logic.get_movie_trailer_url(html_content)

        movie = imdb.get_title_auxiliary("tt{}".format(imdb_id))
        movie = Namespace(**movie)

        return movie

    def download_file(self):
        """
        Downloads movie's trailer but if there is an error
        downloads movie's poster as default

        """
        try:
            logic.prepare_trailer(self.trailer_url)
            return constants.OPTIMIZED_TRAILER_FILE_NAME, 'video'

        except Exception as e:
            print('Download Trailer Error', str(e))
            logic.prepare_poster(self.movie.image['url'])
            return constants.POSTER_FILE_NAME, "image"

    def prepare_tweet(self):
        """
        Prepares tweet with movie's genres, year, imdb rating and name

        """
        tweet_base = logic.prepare_tweet_base_with_movie_details(self.movie.title, self.movie.year, self.movie.rating)
        hashtags = logic.get_hashtags(self.movie.genres, self.movie.title)

        return '{} {}'.format(tweet_base, ' '.join(hashtags))

    def send_tweet(self, media_id):
        """
        Sends tweet with movie details

        """
        tweet = self.prepare_tweet()
        request_data = {
            'status': tweet,
            'media_ids': media_id
        }

        requests.post(url=constants.POST_TWEET_URL, data=request_data, auth=oauth)

    def sending_process(self):
        """
        Media uploading and sending tweet process

        """
        file_name, file_type = self.download_file()
        media_upload = async_upload.VideoTweet(file_name, oauth)
        media_id = media_upload.upload_init(file_type)
        media_upload.upload_append()
        try:
            media_upload.upload_finalize()
        except Exception as e:
            print('Media Upload Error', str(e))
            return self.run()

        self.send_tweet(media_id)

    def run(self):
        """
        Finds suitable movie and send tweet with details

        """
        logic.start_operations()
        self.movie = self.get_movie()
        print('Chosen movie: {} | Year: {}'.format(self.movie.title, self.movie.year))

        is_movie_suitable = logic.is_movie_suitable(self.movie)
        if not is_movie_suitable:
            return self.run()

        self.sending_process()
        print('Tweet sent successfully for that movie {}'.format(self.movie.title))
        logic.remove_movie_medias()
        sys.exit()


if __name__ == '__main__':
    MovieSuggestion().run()
