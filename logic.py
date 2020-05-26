# -*- coding: utf-8 -*-

import os
import re
import collections
import imageio
import youtube_dl
import requests
from settings import constants
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def remove_movie_medias():
    """
    Removes movie medias if exist

    """
    os.system('rm -rf *.mp4 && rm -rf *.jpg && rm -rf *.jpeg && rm -rf *.png')


def start_operations():
    """
    Installs plugin if it is not available and removes movie medias

    """
    imageio.plugins.ffmpeg.download()
    remove_movie_medias()


def get_hashtags(genres, title):
    """
    Gets movie hashtags

    """
    genre_hashtags = ['#{0}'.format(genre.lower().replace('-', '')) for genre in genres]
    removed_signs = ['-', ' ', ':', '\'', '.']
    for sign in removed_signs:
        if sign in title:
            title = title.replace(sign, '')
    movie_hashtags = ['#{}'.format(title), '#movie']
    movie_hashtags.extend(genre_hashtags)

    return movie_hashtags


def download_youtube_trailer(video_url, index=0):
    """
    Downloads youtube trailer

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
    except:
        return download_youtube_trailer(video_url, index + 1)

    return constants.TRAILER_FILE_NAME


def prepare_tweet_base_with_movie_details(title, year, rating):
    """
    Prepares tweet base with movie's title, year and rating details

    """
    return "{} {}   {} {}   {} {}".format(
        constants.CAMERA_EMOJI, title, constants.CALENDAR_EMOJI, year, constants.RATING_EMOJI, rating)


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
