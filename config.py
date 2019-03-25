import json
from os import path
from enum import Enum

_DEFAULT_CONF = {
    'time': '9:00:00',
    'message': '👌',
    'twitter': {
        'consumer_key': '',
        'consumer_secret': '',
        'access_token_key': '',
        'access_token_secret': ''
    },
    'image_files': [
        "https://example.com/myimagefile.png",
        "/home/zekro/icon.png",
        "/home/zekro/img"
    ]
}


class MapValue:
    """
    MapValue wraps a generic type of value.
    """
    v = None
    
    def __init__(self, v):
        self.v = v

    def is_null(self) -> bool:
        """
        Returns if the inner value is
        equal to None.
        """
        return self.v == None

    def get(self, key: str):
        """
        MapValue also provides a get(key) function
        that chaining will not lead into an error.
        This function will always return the same
        current MapValue object.
        """
        return self

    def val(self):
        """
        val returns the inner value of this object.
        """
        return self.v


class MapObject:
    """
    MapObject implements a readonly map type object.
    """
    _m: dict = {}

    def __init__(self, m: dict):
        self._m = m

    def get(self, key: str) -> MapValue:
        """
        Gets the value of the key in the map, if 
        existent and wrap it into a MapValue object.
        If the key does not exist in the map, the
        inner value of the MapValue object will be
        None. THis function can safely be chained
        without throwing an error.
        """
        if key in self._m:
            v = self._m[key]
            if type(v) == dict:
                return MapObject(v)
            return MapValue(v)
        return MapValue(None)

    def val(self):
        """
        val returns the actual inner map of this object.
        """
        return self._m


def _create(loc: str):
    with open(loc, mode='w') as f:
        json.dump(_DEFAULT_CONF, f, indent='  ')


def init(loc: str) -> MapObject:
    """
    init opens a config file and wraps its content
    into a MapObject. If the config file does not
    exist, a new config file will be created at 
    this location and the function will return None.
    """
    if not path.isfile(loc):
        _create(loc)
        return None

    with open(loc, mode='r', encoding='utf8') as f:
        return MapObject(json.load(f))