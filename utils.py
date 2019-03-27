import os
import urllib
import requests
import tempfile
import mimetypes


class FileInfo:
    handler        = None
    size: int      = None
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
        except:
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
        raise Exception('request failed with status code {0}'.format(res.status_code))

    for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
        file.write(chunk)

    return file


def try_get_file(media: str) -> FileInfo:
    file_handler = None

    if media.startswith('http'):
        file_handler = file_from_url(media)
    else:
        media = os.path.realpath(media)
        file_handler = open(media, 'rb')

    return FileInfo(file_handler, media)


def chunk_file(file_info: FileInfo, chunk_size: int):
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
    out = {}
    keys = sorted(d.keys())
    for k in keys:
        out[k] = d[k]
    return out