# -*- coding: utf-8 -*-

import os
import re
import collections
import imageio
import youtube_dl
import requests
from settings import constants
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import numpy as np


def remove_movie_medias():
    """
    Removes movie medias if exist

    """
    os.system('rm -rf *.mp4 && rm -rf *.jpg && rm -rf *.jpeg && rm -rf *.png')


def start_operations():
    """
    Installs plugin if it is not available and removes movie medias

    """
    os.system("imageio_download_bin ffmpeg")
    remove_movie_medias()


def remove_invalid_signs(title):
    """
    Removes invalid signs from movie name for hashtag

    """
    for sign in constants.INVALID_SIGNS:
        if sign in title:
            title = title.replace(sign, '')

    return title


def get_hashtags(movie, director):
    """
    Gets movie hashtags

    """
    cast_list = [principle['name'] for principle in movie.principals[:constants.MAX_CAST_LIMIT]]
    genres = [genre.lower() for genre in movie.genres]
    total_movie_details = np.concatenate(([movie.title, director], cast_list, genres))
    total_flat_details = [remove_invalid_signs(detail) for detail in total_movie_details]
    movie_hashtags = ['#{}'.format(detail) for detail in total_flat_details]

    return movie_hashtags


def evaluate_hashtags(tweet_base, description, hashtag_list):
    if not len(hashtag_list):
        return description

    hashtags = ' '.join(hashtag_list)
    description_with_hashtags = '{} {}'.format(description, hashtags)
    tweet_with_all_details = '{} {}'.format(tweet_base, description_with_hashtags)

    if len(tweet_with_all_details) <= constants.TWEET_MAX_CHAR_LIMIT:
        return description_with_hashtags

    hashtag_list = hashtag_list[:-1]

    return evaluate_hashtags(tweet_base, description, hashtag_list)


def get_helper_details(movie, tweet_base, director):
    """
    Gets movie helper details

    """
    description = movie.plot['outline']['text']
    hashtag_list = get_hashtags(movie, director)
    tweet_with_description = '{} {}'.format(tweet_base, description)

    if len(tweet_with_description) <= constants.TWEET_MAX_CHAR_LIMIT:
        return evaluate_hashtags(tweet_base, description, hashtag_list)

    return ' '.join(hashtag_list)


def download_youtube_trailer(video_url, index=0):
    """
    Downloads youtube trailer by trying recursively
    from high quality to low quality

    """
    if len(constants.MP4_VIDEO_FORMATS) == index:
        raise Exception()

    video_url = video_url.strip()
    ydl_opts = {
        'format': constants.MP4_VIDEO_FORMATS[index],
        'keepvideo': True,
        'outtmpl': './{}'.format(constants.TRAILER_FILE_NAME)
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print('Download youtube trailer error', str(e))
        return download_youtube_trailer(video_url, index + 1)

    return constants.TRAILER_FILE_NAME


def prepare_tweet_base_with_movie_details(movie, director):
    """
    Prepares tweet base with movie's name, year, rating and director name details

    """
    return "{} {}  {} {}  {} {}  {} {}".format(
        constants.CLAPPER_BOARD_EMOJI, movie.title,
        constants.CALENDAR_EMOJI, movie.year,
        constants.DIRECTOR_EMOJI, director,
        constants.RATING_EMOJI, movie.rating
    )


def prepare_trailer(trailer_url):
    """
    Downloads trailer video and formats duration

    """
    downloaded_file_name = download_youtube_trailer(trailer_url)
    ffmpeg_extract_subclip(
        downloaded_file_name,
        constants.START_LIMIT,
        constants.DURATION_LIMIT,
        targetname=constants.OPTIMIZED_TRAILER_FILE_NAME)


def prepare_poster(poster_url):
    """
    Downloads movie poster

    """
    r = requests.get(poster_url, stream=True)
    with open(constants.POSTER_FILE_NAME, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def convert_unicode_to_string(data):
    """
    Converts unicode variables to string

    """
    if isinstance(data, basestring):
        try:
            return str(data)
        except UnicodeEncodeError:
            return str(data.encode('ascii', 'ignore').decode('ascii'))
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_to_string, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_to_string, data))
    else:
        return data


def get_movie_trailer_url(html_content):
    """
    Gets movie trailer url

    """
    embed_id = re.findall(constants.TRAILER_VIDEO_ID_PATTERN, html_content)[0]
    return '{}{}'.format(constants.VIDEO_URL_INITIAL, embed_id)


def is_movie_suitable(movie):
    """
    Checks chosen movie is suitable or not

    """
    if not movie.rating or (movie.rating and movie.rating < constants.LEAST_RATING):
        return False

    if movie.year < constants.YEAR_LIMIT:
        return False

    return True
