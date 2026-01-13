# /usr/bin/env pyhthon
# !/usr/bin/env python
import sys
from select import select
from signal import SIGUSR1
import os


class Stdin():
	def __init__(s,**k):
		# super().__init__()
		s.term = s.term = k.get('term')
		s._buffer = []
		s._event = True
		s._count = 0

	@property
	def event(s):
		s._event = select([s.term.fd], [], [], 0)[0] != []
		return s._event

	def read(s):
		ret = None
		if s.event:
			while s.event:
				s._buffer += [sys.stdin.read(1)]
			ret = ''.join(s._buffer)
			s.flush()
			s._count += 1
		return ret

	@property
	def counted(s):
		return s._count

	def getch(s):
		if len(s.buffer) != 0:
			c = s.buffer[-1]
			s.flush()

	def flush(s):
		s._buffer = []
		sys.stdin.flush()



