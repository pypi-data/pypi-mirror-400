#!/usr/bin/env python
import io
import os
import termios
import atexit
import sys
from libTerm.term.types import Color, Size,Mode
from libTerm.term.cursor import  Cursor
from contextlib import suppress


# Indices for termios list.
IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6
TCSAFLUSH = termios.TCSAFLUSH
ECHO = termios.ECHO
ICANON = termios.ICANON

VMIN = 6
VTIME = 5


class TermAttrs():
	def __init__(s,**k):
		s.term=k.get('term')
		s.stack=[]
		s.active=s.term.tcgetattr()
		s.init=list([*s.active])
		s.stack+= [list(s.active)]
		s.staged=None

	def stage(s):
		s.staged=list(s.active)
	def update(s,new=None):
		if new is None:
			new=s.staged
		s.stack+=[list(s.active)]
		s.active=new
		s.staged=None
	def restore(s):
		if s.stack:
			s.staged=s.stack.pop()
		return s.staged

class TermColors():
	def __init__(s, **k):
		s.term = k.get('term')
		s._specs = {'fg': 10, 'bg': 11}
		s._ansi = '\x1b]{spec};?\a'
		s.fg = Color(255, 255, 255)
		s.bg = Color(0, 0, 0)
		s.__kwargs__(**k)
		s.init = s._update_()

	def __kwargs__(s, **k):
		s.term = k.get('term')

	@staticmethod
	def _ansiparser_():
		buf = ''
		try:
			for i in range(23):
				buf += sys.stdin.read(1)
			rgb = buf.split(':')[1].split('/')
			rgb = [int(i, base=16) for i in rgb]
			rgb = Color(*rgb, 16)
		except Exception as E:
			# print(E)
			rgb = None
		return rgb

	def _update_(s):
		for ground in s._specs:
			result = None
			while not result:
				result = s.term._ansi_(s._ansi.format(spec=s._specs[ground]), s._ansiparser_)
			s.__setattr__(ground, result)

		return {'fg': s.fg, 'bg': s.bg}


class Term():
	MODE=Mode
	def __init__(s,*a,**k):
		# super().__init__()
		s.pid       = os.getpid()
		s.ppid      = os.getpid()
		s.fd		= sys.__stdin__.fileno()
		with suppress(io.UnsupportedOperation):
			s.fd        = sys.stdin.fileno()
			s.tty       = os.ttyname(s.fd)

		s._mode     = Mode.NONE
		s.attr      = TermAttrs(term=s)
		s.cursor    = Cursor(term=s)
		atexit.register(s.mode,Mode.NORMAL)
		# s.vcursors  = {0:vCursor(s,s.cursor)}
		s.size      = Size(term=s)
		s.color     = TermColors(term=s)

	def tcgetattr(s):
		return termios.tcgetattr(s.fd)

	def tcsetattr(s,attr,when=TCSAFLUSH):
		termios.tcsetattr(s.fd,when,attr)

	def setraw(s, when=TCSAFLUSH):
		"""Put terminal into raw mode."""
		from termios import IGNBRK,BRKINT,IGNPAR,PARMRK,INPCK,ISTRIP,INLCR,IGNCR,ICRNL,IXON,IXANY,IXOFF,OPOST,PARENB,CSIZE,CS8,ECHO,ECHOE,ECHOK,ECHONL,ICANON,IEXTEN,ISIG,NOFLSH,TOSTOP
		s.attr.stage()
		# Clear all POSIX.1-2017 input mode flags.
		# See chapter 11 "General Terminal Interface"
		# of POSIX.1-2017 Base Definitions.
		s.attr.staged[IFLAG] &= ~(IGNBRK | BRKINT | IGNPAR | PARMRK | INPCK | ISTRIP | INLCR | IGNCR | ICRNL | IXON
								  | IXANY | IXOFF)
		# Do not post-process output.
		s.attr.staged[OFLAG] &= ~OPOST
		# Disable parity generation and detection; clear character size mask;
		# let character size be 8 bits.
		s.attr.staged[CFLAG] &= ~(PARENB | CSIZE)
		s.attr.staged[CFLAG] |= CS8
		# Clear all POSIX.1-2017 local mode flags.
		s.attr.staged[LFLAG] &= ~(ECHO | ECHOE | ECHOK | ECHONL | ICANON | IEXTEN | ISIG | NOFLSH | TOSTOP)
		# POSIX.1-2017, 11.1.7 Non-Canonical Mode Input Processing,
		# Case B: MIN>0, TIME=0
		# A pending read shall block until MIN (here 1) bytes are received,
		# or a signal is received.
		s.attr.staged[CC] = list(s.attr.staged[CC])
		s.attr.staged[CC][VMIN] = 1
		s.attr.staged[CC][VTIME] = 0
		s._update_(when)

	def setcbreak(s,when=TCSAFLUSH):
		"""Put terminal into cbreak mode."""
		# this code was lifted from the tty module and adapted for being a method
		s.attr.stage()
		# Do not echo characters; disable canonical input.
		s.attr.staged[LFLAG] &= ~(ECHO | ICANON)
		# POSIX.1-2017, 11.1.7 Non-Canonical Mode Input Processing,
		# Case B: MIN>0, TIME=0
		# A pending read shall block until MIN (here 1) bytes are received,
		# or a signal is received.
		s.attr.staged[CC] = list(s.attr.staged[CC])
		s.attr.staged[CC][VMIN] = 1
		s.attr.staged[CC][VTIME] = 0
		s._update_(when)

	def echo(s,enable=False):
		s.attr.stage()
		s.attr.staged[3] &= ~ECHO
		if enable:
			s.attr.staged[3] |= ECHO
		s._update_()

	def canonical(s,enable=True):
		s.attr.stage()
		s.attr.staged[3] &= ~ICANON
		if enable:
			s.attr.staged[3] |= ICANON
		s._update_()

	def mode(s, mode=Mode.NONE):
		def Normal():
			s.cursor.show(True)
			s.echo(True)
			s.canonical(True)
			s.tcsetattr(s.attr.init)
			s._mode = Mode.NORMAL

		def Ctl():
			s.cursor.show(False)
			s.echo(False)
			s.canonical(False)
			s._mode = Mode.CONTROL

		fmodi = {
			1   :  Normal,
			2   :  Ctl,
		}
		if mode is not None and mode != 0:
			fmodi.get(mode)()
		return s._mode
		
	def _update_(s, when=TCSAFLUSH):
		s.tcsetattr(s.attr.staged, when)
		s.attr.update(s.tcgetattr())

	def _ansi_(s, ansi, parser):
		s.setcbreak()
		try:
			sys.stdout.write(ansi)
			sys.stdout.flush()
			result = parser()
		finally:
			s.tcsetattr(s.attr.restore())
		return result
#
