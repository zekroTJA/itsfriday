import time
import datetime
from typing import NamedTuple


class StructTime(NamedTuple):
	"""
	StructTime provides a simplified time struct
	for weekday, hour, minute and second of time.
	Also, it provides functions for calculating
	the delta between two of these objects in
	between a time span of 1 week.
	"""
	wday: int
	hour: int
	minute: int
	second: int

	@property
	def _max_secs(self) -> int:
		"""
		7 days in seconds.
		"""
		return 604800

	def _in_secs(self):
		"""
		Calculates the absolute ammount of
		seconds counted from Monday, 00:00:00.
		"""
		return (self.wday * 3600 * 24
			+ self.hour * 3600
			+ self.minute * 60
			+ self.second)

	def until(self, t) -> int:
		"""
		Calculates the ammount of seconds
		until rt in seconds.
		"""
		st = t._in_secs()
		sn = self._in_secs()
		d = st - sn
		if d < 0:
			d += self._max_secs
		return d
		

class Timer:
	"""
	Timer provides a simple, blocking timer
	which activates a callback when the current
	time hits the defined trigger time once a week.
	"""
	_trigger_at: StructTime
	_cb = None
	_cb_called = False

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

	def _get_time(self) -> StructTime:
		"""
		Get current time as StructTime.
		"""
		now = datetime.datetime.now()
		return StructTime(now.weekday(), now.hour, now.minute, now.second)

	def _get_until_trigger(self) -> int:
		"""
		Calculates the delta ammount of seconds 
		from now until the defined trigger time. 
		"""
		now = self._get_time()
		# return now.until(StructTime(5, 12, 20, 0))
		return now.until(self._trigger_at)
	
	def start_blocking(self):
		"""
		Starts a blocking timer loop which
		activates the passed callback function
		each time the current time hits
		the defined trigger time.
		"""
		while True:
			d = self._get_until_trigger()
			if d > 3600:
				self._cb_called = False
				time.sleep(600)
			elif d > 60:
				time.sleep(10)
			else:
				time.sleep(0.2)
				if d == 0 and not self._cb_called:
					self._cb_called = True
					self._cb()