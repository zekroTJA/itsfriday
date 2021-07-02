import os
import re
from random import randint


_RE_URL = re.compile(r'https?:\/\/(www\.)?[\w\-\.]+\.\w{1,8}(:\d{1,5})?.*')


class FileManager:
    _locs: list = []
    _files: list = []

    def __init__(self, locations: list):
        self._locs = locations

    def index_files(self):
        self._files = []
        for loc in self._locs:
            if _RE_URL.match(loc):
                self._files.append(loc)
            elif os.path.isfile(loc):
                self._files.append(loc)
            elif os.path.isdir(loc):
                self._files.extend(["%s/%s" % (loc, f) for f in os.listdir(loc)
                                    if os.path.isfile(os.path.join(loc, f))])

    def get_rnd_file(self, index_before=True) -> str:
        if index_before:
            self.index_files()
        ln = len(self._files)
        if ln == 0:
            return None
        if ln == 1:
            return self._files[0]
        rand = randint(0, ln-1)
        return self._files[rand]
