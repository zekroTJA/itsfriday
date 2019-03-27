import requests
import base64
import urllib
from requests_oauthlib import OAuth1, OAuth2
from typing import NamedTuple

import config
import utils


class RateLimitException(Exception):
    _MESSAGE = 'rate limit exceeded'

    def __init__(self):
        super().__init__(self._MESSAGE)


class Credentials:
    """
    TwitterCedentials contains the consumer_key
    and the comsumer_secret for creating an
    access token.

    If consumer_key or consumer_secret is None,
    an exception will be raised.
    """
    consumer_key: str        = None
    consumer_secret: str     = None
    access_token_key: str    = None
    access_token_secret: str = None

    def __init__(self, consumer_key: str, consumer_secret: str, access_token_key: str, access_token_secret: str):
        if consumer_key is None:
            raise Exception('consumer_key was None')
        if consumer_secret is None:
            raise Exception('consumer_secret was None')
        if access_token_key is None:
            raise Exception('access_token_key was None')
        if access_token_secret is None:
            raise Exception('access_token_secret was None')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret

    def to_oauth1(self) -> OAuth1:
        return OAuth1(self.consumer_key, self.consumer_secret,
            self.access_token_key, self.access_token_secret)


class Twitter:
    """
    Twitter wraps API requests to the
    Twitter API.

    Parameters
    ==========

    credentials : config.MapObject
        MapObject containing a value for 'consumer_key'
        and for 'consumer_secret'.
    """
    _API_ROOT_URI        = 'https://api.twitter.com'
    _API_VERSION         = '1.1'
    _API_UPLOAD_ROOT_URI = 'https://upload.twitter.com/1.1'
    _UPLOAD_CHUNK_SIZE   = 1024 * 1024 * 1024 # 1 MiB

    _access_token: str          = None
    _credentials: Credentials   = None
    _oauth: OAuth1              = None
    _user_context_oauth: OAuth2 = None
    _session: requests.Session  = None


    def __init__(self, credentials: config.MapObject):
        self._credentials = Credentials(
            credentials.get('consumer_key').val(),
            credentials.get('consumer_secret').val(),
            credentials.get('access_token_key').val(),
            credentials.get('access_token_secret').val()
        )
        self._oauth = self._credentials.to_oauth1()
        self._session = requests.Session()
        self._obtain_user_context_token()

    def _request(self, method: str, resource_path: str, **kwargs):
        """
        _request requests the Twitter API with the defined authentication
        credentials.

        This method raises an exception on failed authentication or request.

        Parameters
        ==========

        method : str
            Request method.
        resource_path : str
            Path to the requested resource (without root URI).
            Leading '/' will be cut off.
        **kwargs
            Optional arguments passed to request.request()

        Returns
        =======

        Object
            JSON-parsed response body.
        """
        res = self._session.request(
            auth=self._oauth,
            method=method,
            url='{0}/{1}/{2}'.format(self._API_ROOT_URI, self._API_VERSION,
                (resource_path[1:] if resource_path.startswith('/') else resource_path)),
            **kwargs)

        if res.status_code == 429:
            raise RateLimitException()

        print(res.headers)

        if not res.ok:
            raise Exception('request failed with status code {0} and message:'.format(res.status_code))

        return res.json()

    def _obtain_user_context_token(self):
        key = urllib.parse.quote_plus(self._credentials.consumer_key)
        secret = urllib.parse.quote_plus(self._credentials.consumer_secret)
        basic_token = base64.b64encode(
            '{0}:{1}'.format(key, secret).encode('utf8')).decode('utf8')
        
        res = self._session.post(
            url='{0}/oauth2/token'.format(self._API_ROOT_URI),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Authorization': 'Basic {0}'.format(basic_token),
            },
            data={
                'grant_type': 'client_credentials',
            })

        if res.status_code == 429:
            raise RateLimitException()
        if res.status_code != 200:
            raise Exception('request failed with status code {0}'.format(res.status_code))

        body = res.json()

        self._user_context_oauth = OAuth2(token=body)


    def _upload_media_request(self, command: str, params={}, **kwargs):
        params['command'] = command
        res = self._session.post(
            auth=self._oauth,
            url='{0}/media/upload.json'.format(self._API_UPLOAD_ROOT_URI),
            # url='{0}/media/upload.json?{1}'.format(self._API_UPLOAD_ROOT_URI, 
                # urllib.parse.urlencode(utils.sort_dict_alphabetically(params), safe='/')),
            headers={ 'Content-Type': 'multipart/form-data' },
            data=utils.sort_dict_alphabetically(params),
            **kwargs)

        if res.status_code == 429:
            raise RateLimitException()
        if res.status_code < 200 or res.status_code >= 300:
            print(res.json())
            print(res.request.headers)
            raise Exception('request failed with status code {0}'.format(res.status_code))

        return res

    def upload_media_cunked(self, media: str) -> str:
        file_info = utils.try_get_file(media)

        # --- INIT ------------------------------------------------------------
        res = self._upload_media_request(
            command='INIT',
            params={
                'total_bytes': file_info.size,
                'media_type': file_info.mime_type,
            })
        
        res_data = res.json()
        if 'media_id_string' not in res_data:
            raise Exception('"media_id_string" not contained in response body')
        media_id = res_data['media_id_string']

        # --- APPEND ----------------------------------------------------------
        for chunk in utils.chunk_file(file_info, self._UPLOAD_CHUNK_SIZE):
            self._upload_media_request(
                command='APPEND',
                params={
                    'media_id': media_id,
                    'media': chunk.data,
                    'segment_index': chunk.index,
                })

        # --- FINALIZE --------------------------------------------------------
        res = self._upload_media_request(
            command='FINALIZE',
            params={
                'media_id': media_id,
            })

        return res.json()
        
    def update(self, txt: str, img: str):
        data = {
            'status': txt,
        }
        self._request('POST', 'statuses/update.json', data=data)