from typing import List
import logging
from os import path

class Queue:

    def __init__(self, file_loc: str):
        self.file_loc = file_loc
        if self.file_loc and not path.isfile(self.file_loc):
            open(self.file_loc, 'a').close()

    def next(self) -> List[str]:
        if not self.file_loc:
            return None
        try:
            with open(self.file_loc, 'r') as f:
                lines = f.read().splitlines(False)
                if len(lines) < 1:
                    return None
                d = lines[0].split(' ', 1)
            with open(self.file_loc, 'w') as f:
                f.write('\n'.join(lines[1:]))
            return None if len(d) < 1 else d
        except Exception as e:
            logging.error('Failed getting queue entry: ' + str(e)) 
            return None