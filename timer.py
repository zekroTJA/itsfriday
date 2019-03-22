import time
import datetime
from typing import NamedTuple


class StructTime(NamedTuple):
    tm_wday: int
    tm_hour: int
    tm_min: int
    tm_sec: int


class Timer:
    _trigger_at: StructTime
    _cb = None

    def __init__(self, wday: int, t: str, cb):
        if wday < 0 or wday > 6:
            raise Exception("wday must be in range [0, 6]")
        t_split = t.split(':')
        if len(t_split) == 3:
            self._trigger_at = StructTime(
                wday, int(t_split[0]), int(t_split[1]), int(t_split[2]))
        elif len(t_split) == 2:
            self._trigger_at = StructTime(
                wday, int(t_split[0]), int(t_split[1]), 0)
        elif len(t_split) == 1:
            self._trigger_at = StructTime(
                wday, int(t_split[0]), 0, 0)
        else:
            raise Exception("wrong format for t. Must be hh(:mm(:ss)) (parantheses means optional).")
        self._cb = cb

    def _calc_secs_until(self) -> int:
        today = now = datetime.datetime.today()
        today = datetime.datetime(today.year, today.month, today.day)
        wdays = self._trigger_at.tm_wday-now.weekday()
        then = datetime.timedelta(seconds=self._trigger_at.tm_sec,
            minutes=self._trigger_at.tm_min,
            hours=self._trigger_at.tm_hour,
            days=(7 if wdays == 0 else wdays))
        return (then + today - now).total_seconds()

    def start_blocking(self):
        while True:
            until = self._calc_secs_until()
            print(until)
            time.sleep(until)
            if not self._cb == None:
                self._cb() 
            time.sleep(2)