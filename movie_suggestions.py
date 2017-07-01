import urllib2
import re
import requests
import os
from imdb import IMDb
from requests_oauthlib import OAuth1
from twitter_media_upload import async_upload

POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

CONSUMER_KEY = 'your_consumer_key'
CONSUMER_SECRET = 'your_consumer_secret'
ACCESS_TOKEN = 'your_access_token'
ACCESS_TOKEN_SECRET = 'your_access_token_secret'

base_url = "http://www.imdb.com/"
imdb = IMDb()
least_rating = 6
duration_limit = 220

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
        Gets a random movie from IMDB.
         
        """
        random_url = "{}random/title".format(base_url)
        movie_id_pattern = "app-argument=imdb:///title/tt(\d+)\?src=mdot"
        html_for_movie_id = urllib2.urlopen(random_url).read()
        object_id = re.findall(movie_id_pattern, html_for_movie_id)[0]
        object = imdb.get_movie(object_id)
        if not object['kind'] == 'movie':
            object = self.get_movie()
        return object

    def has_rating(self):
        """
        Determines a movie is new or not. If movie has not imdb rating, it's new, otherwise not.
         
        """
        self.rating = False if 'rating' in self.movie.data else True

    def get_trailer_or_poster_url(self):
        """
        If a movie has a trailer, gets trailer, otherwise gets movie's poster.
          
        """
        movie = self.movie
        trailer_id_pattern = "/video/imdb/vi(\d+)\?ref_=ttvi_vi_imdb_1"
        video_gallery_url = "{0}title/tt{1}/videogallery/content_type-trailer?sort=duration" \
                            "&sortDir=asc".format(base_url, movie.movieID)
        html_for_trailer_id = urllib2.urlopen(video_gallery_url).read()
        trailer = re.findall(trailer_id_pattern, html_for_trailer_id)
        if not trailer:
            return 'image', movie['full-size cover url']
        trailer_id = trailer[0]
        video_pattern = "vi%s\":{\"aggregateUpVotes\":.*?duration\":\"([\d:\d]*).*?" \
                        "videoUrl\":\"(.*?)\"},{\"definition" % trailer_id
        video_url = "http://www.imdb.com/title/tt{0}/videoplayer/vi{1}".format(movie.movieID,
                                                                               trailer_id)
        html_video = urllib2.urlopen(video_url).read()
        duration, video_link = re.findall(video_pattern, html_video)[0]
        self.duration = False if int(duration.replace(':', '')) > duration_limit else True
        if not self.duration:
            print("Trailer's duration is({}) more than accepted duration(2:20)").format(duration)

        return 'video', video_link

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
        base = "\xF0\x9F\x8E\xA5: {0}   \xF0\x9F\x93\x85: {1}".format(movie['title'], movie['year'])
        option = "  #comingsoon" if self.rating else "  \xE2\xAD\x90: {0}  ".format(
            movie['rating'])
        genre_hashtags = ['#{0}'.format(genre.lower().replace('-', '')) for genre in
                          movie['genres']]
        removed_signs = ['-', ' ', ':', '\'']
        movie_name = movie['title'].title()
        for sign in removed_signs:
            if sign in movie_name:
                movie_name = movie_name.replace(sign, '')
        hashtags = ['#{}'.format(movie_name), '#movie']
        hashtags.extend(genre_hashtags)
        self.tweet = self.control_character_limit(' '.join([base, option, ' '.join(hashtags)]))

    def control_character_limit(self, tweet):
        """
        Controls tweet's character, if it's more than 140 character, last hashtag is removed 
        and controlled again.

        """
        if len(tweet) <= 140:
            return tweet
        split_list = tweet.split(' ')
        del split_list[-1]
        tweet = ' '.join(split_list)
        return self.control_character_limit(tweet)

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

    def run(self):
        """
        Runs and tweets one random movie with trailer or movie poster.
         
        """
        self.movie = self.get_movie()
        print("Movie Name: {}").format(self.movie['title'])
        self.has_rating()
        if not self.rating and self.movie['rating'] < least_rating:
            print("Movie's rating({}) is less than least rating({})").format(self.movie['rating'],
                                                                             least_rating)
            return self.run()
        file_type, file_url = self.get_trailer_or_poster_url()
        if file_type == 'video' and not self.duration:
            return self.run()
        print("Movie will be shared with {} ").format(file_type)
        movie_name = self.movie['title'].lower().replace(' ', '_')
        self.download_file(file_url, movie_name, file_type)
        media_upload = async_upload.VideoTweet(self.file_name, oauth)
        media_id = media_upload.upload_init(file_type)
        media_upload.upload_append()
        media_upload.upload_finalize()
        self.send_tweet(media_id)
        return


if __name__ == '__main__':
    MovieSuggestion().run()
