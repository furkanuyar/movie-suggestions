# -*- coding: utf-8 -*-
import collections


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
