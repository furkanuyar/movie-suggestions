# -*- coding: utf-8 -*-

import re
import random
from urllib.request import urlopen
import requests
from config import MOVIE_QUOTE_SOURCE, imdb, oauth
from bs4 import BeautifulSoup
from twitter_media_upload import async_upload
import logic
from settings import constants
import sys


def get_quote_and_movie_name():
    """
    Finds a random movie quote and returns with movie name

    """
    html_content = urlopen(MOVIE_QUOTE_SOURCE).read().decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    results = soup.find_all(attrs={'class': 'col-xs-9 col-lg-10'})
    quote_regex = re.compile('<blockquote>(.*?)</blockquote>')
    movie_regex = re.compile('</strong>(.*?)</span>')
    movie_em_regex = re.compile('<em>(.*?)</em>')
    movie_regex_second = re.compile('</strong>(.*?)</a>')
    last_results = []

    for result in results:

        quote_line = str(result.find('blockquote')).replace('\n', '')
        quote = quote_regex.findall(quote_line)[0].strip()
        movie_line = str(result.find_all(attrs={'class': 'source'})[0])
        try:
            movie_name = movie_regex.findall(movie_line)[0].strip()
        except:
            movie_name = movie_regex_second.findall(movie_line)[0].strip()
        if '<em>' in movie_name:
            movie_name = movie_em_regex.findall(movie_name)[0].strip()

        last_results.append((quote, movie_name))

    return random.choice(last_results)


def get_movie_poster_url(movie_name):
    """
    Finds movie from movie name and returns movie's poster url

    """
    result = imdb.search_for_title(movie_name)
    imdb_id = result[0]['imdb_id']
    movie = imdb.get_title_auxiliary(imdb_id)

    return movie['image']['url']


def download_poster(movie_poster_url):
    """
    Downloads movie's poster

    """
    logic.prepare_poster(movie_poster_url)
    return constants.POSTER_FILE_NAME, "image"


def send_tweet(media_id, tweet):
    """
    Sends tweet with movie details

    """
    request_data = {
        'status': tweet,
        'media_ids': media_id
    }

    requests.post(url=constants.POST_TWEET_URL, data=request_data, auth=oauth)


class Quote:
    def sending_process(self, quote, movie_poster_url):
        """
        Media uploading and sending tweet process

        """
        file_name, file_type = download_poster(movie_poster_url)
        media_upload = async_upload.VideoTweet(file_name, oauth)
        media_id = media_upload.upload_init(file_type)
        media_upload.upload_append()
        try:
            media_upload.upload_finalize()
        except Exception as e:
            print('Media Upload Error', str(e))
            return self.run()

        send_tweet(media_id, quote)

    def run(self):
        """
        Finds quote and send tweet with related movie poster

        """
        logic.remove_movie_medias()
        (quote, movie_name) = get_quote_and_movie_name()
        print('Chosen movie: {}'.format(movie_name))
        movie_poster_url = get_movie_poster_url(movie_name)
        self.sending_process(quote, movie_poster_url)
        logic.remove_movie_medias()
        sys.exit()


if __name__ == '__main__':
    Quote().run()
