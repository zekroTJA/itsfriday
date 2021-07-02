import logging
import os
import urllib
import requests
import tempfile
import mimetypes


class FileInfo:
    handler = None
    size: int = None
    mime_type: str = None
    file_name: str = None
    full_path: str = None
    from_url: bool = False

    def __init__(self, file_handler, full_media_path: str):
        self.handler = file_handler

        if full_media_path.startswith('http'):
            self.from_url = True
            self.full_path = urllib.parse.urlparse(full_media_path).path
        else:
            self.full_path = full_media_path
        self.file_name = os.path.basename(self.full_path)

        file_handler.seek(0, 2)
        self.size = file_handler.tell()
        try:
            file_handler.seek(0)
        except Exception as e:
            logging.error(e)
            pass

        self.mime_type = mimetypes.guess_type(self.file_name)[0]

    def close(self):
        self.handler.close()


class FileChunk:
    size: int = 0
    data = []
    index: int = 0

    def __init__(self, size: int, index: int, data):
        self.size = size
        self.index = index
        self.data = data


class Megabyte:
    _n: float = 0

    def __init__(self, n: float):
        self._n = n

    def __str__(self):
        return str(self._n)

    @property
    def n_bytes(self) -> int:
        return self._n * 1024 * 1024


def file_from_url(url: str):
    """
    file_from_url requests a file from an URL.
    Raises an exception if the request fails.

    Parameters
    ==========

    url : str
        The resource URL.

    Returns
    =======

    _TemporaryFileWrapper
        Requested file as temporary file handler. 
    """
    CHUNK_SIZE = 1024*1024

    file = tempfile.NamedTemporaryFile()
    res = requests.get(url, stream=True)

    if not res.ok:
        raise Exception(
            'request failed with status code {0}'.format(res.status_code))

    for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
        file.write(chunk)

    return file


def try_get_file(media: str) -> FileInfo:
    """
    try_get_file tries to get a file either by a
    local file path or by a HTTP(S) URL.

    Parameters
    ==========

    media : str
        A local file location or a HTTP(S) link
        to an online file resource.

    Returns
    =======

    FileInfo
        The FileInfo object of a file.
    """
    file_handler = None

    if media.startswith('http'):
        file_handler = file_from_url(media)
    else:
        media = os.path.realpath(media)
        file_handler = open(media, 'rb')

    return FileInfo(file_handler, media)


def chunk_file(file_info: FileInfo, chunk_size: int):
    """
    chunk_file splits a file by its size into chunks of
    the defined chunk_size. This function must be used
    as an interator.

        for chunk in chunk_file(file_info, 1024):
            # ...

    Parameters
    ==========

    file_info : FileInfo
        FileInfo instance of an open file which
        can be read from.

    chunk_size : int
        The byte-size of a single chunk.
    """
    n_chunks = int(file_info.size / chunk_size)
    rest = file_info.size - n_chunks * chunk_size

    for i in range(0, n_chunks):
        yield FileChunk(
            size=chunk_size,
            index=i,
            data=file_info.handler.read(chunk_size))

    if rest > 0:
        yield FileChunk(
            size=rest,
            index=n_chunks,
            data=file_info.handler.read(rest))


def sort_dict_alphabetically(d: dict) -> dict:
    """
    sort_dict_alphabetically sorts the content of
    a dictionary alphabetically by keys and returns
    the result as new dictionary.

    Parameters
    ==========

    d : dict
        Dictionary which should be sorted.

    Returns
    =======

    dict
        Alphabetically sorted dictionary.
    """
    out = {}
    keys = sorted(d.keys())
    for k in keys:
        out[k] = d[k]
    return out


def check_upload_compatibility(file_info: FileInfo) -> int:
    """
    check_upload_compatibility checks if the file can be
    uplaoded to Twitter. If the file is not compatible,
    an exception will be raised.

    Parameters
    ==========

    file_info : FileInfo
        FileInfo instance of a local or online file.

    Returns
    =======

    int
        If the check succeeds, the function will return
        the maximum ammount of files you can attach to
        a tweet.
    """
    IMAGE_TYPE_MAXSIZE = Megabyte(5)
    IMAGE_TYPES = (
        'image/jpeg',
        'image/png',
        'image/webp',
    )

    LARGE_IMAGE_TYPE_MAXSIZE = Megabyte(15)
    LARGE_IMAGE_TYPES = (
        'image/gif',
    )

    VIDEO_TYPE_MAXSIZE = Megabyte(512)
    VIDEO_TYPES = (
        'video/mp4',
        'video/quicktime',
    )

    if file_info.mime_type in IMAGE_TYPES:
        if file_info.size > IMAGE_TYPE_MAXSIZE.n_bytes:
            raise Exception('image file can not be larger than {0} MiB'
                            .format(str(IMAGE_TYPE_MAXSIZE)))
        return 3

    if file_info.mime_type in LARGE_IMAGE_TYPES:
        if file_info.size > LARGE_IMAGE_TYPE_MAXSIZE.n_bytes:
            raise Exception('image file can not be larger than {0} MiB'
                            .format(str(LARGE_IMAGE_TYPE_MAXSIZE)))

    if file_info.mime_type in VIDEO_TYPES:
        if file_info.size > VIDEO_TYPE_MAXSIZE.n_bytes:
            raise Exception('image file can not be larger than {0} MiB'
                            .format(str(VIDEO_TYPE_MAXSIZE)))

    return 1
