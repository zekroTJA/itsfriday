import twitter
from typing import NamedTuple

import config


class Twitter:
    _credentials: config.MapObject
    _client: twitter.Api

    def __init__(self, credentials: config.MapObject):
        self._credentials = credentials
        self._client = twitter.Api(
            self._credentials.get("consumer_key").val(),
            self._credentials.get("consumer_secret").val(),
            self._credentials.get("access_token_key").val(),
            self._credentials.get("access_token_secret").val())
        self._client.VerifyCredentials()

    def update(self, txt: str, img: str):
        self._client.PostUpdate(txt, img)