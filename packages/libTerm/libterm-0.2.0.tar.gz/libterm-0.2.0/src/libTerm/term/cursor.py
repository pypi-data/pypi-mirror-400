import sys
import re
from enum import Enum
from dataclasses import dataclass
from collections import namedtuple
from time import time_ns
from libTerm.term.types import Coord,Store


@dataclass()
class Move(str,Enum):
	abs= '\x1b[{Y};{X}H'
	up= '\x1b[{Y}A'
	down= '\x1b[{Y}B'
	right= '\x1b[{X}C'
	left= '\x1b[{X}D'
	prev= '\x1b[{Y}E'
	next= '\x1b[{Y}F'
	col= '\x1b[{X}G'

	def __str__(s):
		return s.value
	def __repr__(s):
		return repr(s.value)
	def __call__(s, *a, **k):
		X=k.get('X')
		Y=k.get('Y')
		if 'X' in str(s.value):
			if X is None:
				X = 1
				if (len(a)>0):
					X=a[0]

		if 'Y' in str(s.value):
			if Y is None:
				Y=1
				if (len(a)==1):
					if not 'X' in str(s.value):
						Y=a[0]
				if (len(a) > 1):
					Y=a[1]
		tplvars={'X':X,'Y':Y}
		print(str(s.value).format(**tplvars),end='',flush=True)

@dataclass()
class ANSI_Cursor(str, Enum):
	show = '\x1b[?25h'
	hide = '\x1b[?25l'
	scrup= '\x1bM'
	getxy= '\x1b[6n'
	# savxy= '7','[s'
	# rstxy= '8','[u'

	def __str__(s):
		return s.value
	def __repr__(s):
		return repr(s.value)
	def __call__(s):
		print(str(s.value), end='', flush=True)

class Cursor():
	def __init__(s, term):
		super().__init__()
		s.term    = term
		s.ansi    = ANSI_Cursor
		s.move    = Move
		s.re      = re.compile(r"^.?\x1b\[(?P<Y>\d*);(?P<X>\d*)R", re.VERBOSE)
		s._xy     = Coord(0,0)
		s.store   = Store()
		s.visible = True
		s.hidden  = False
		#TODO:		s.stamp=time_ns()
		#TODO:		s.moved=False
		#TODO:		s._history = [*(None,) * 64]
		s.init    = s.__update__()

	@property
	def xy(s):
		return s.__update__()

	@xy.setter
	def xy(s,coord):
		print('\x1b[{y};{x}H'.format(**coord), end='', flush=True)
		s.__update__()

	def stored(s):
		return s.store.stored

	def __update__(s):
		def Parser():
			buf = ' '
			while buf[-1] != "R":
				buf += sys.stdin.read(1)
			# reading the actual values, but what if a keystroke appears while reading
			# from stdin? As dirty work around, getpos() returns if this fails: None
			try:
				groups = s.re.search(buf).groupdict()
				result = Coord(int(groups['X']), int(groups['Y']))
			except AttributeError:
				result = None
			return result

		result = None
		timeout = {}
		timeout['limit'] = 500
		timeout['start'] = time_ns() // 1e6
		timeout['running'] = 0
		while not result:
			result = s.term._ansi_(s.ansi.getxy, Parser)
		s._xy =result
		return result

	def show(s, state=True):
		if s.hidden and state:
			s.ansi.show()
			s.hidden=False
			s.visible=True
		if s.visible and not state:
			s.ansi.hide()
			s.hidden=True
			s.visible=False

	def hide(s, state=True):
		if s.visible and state:
			s.show(False)
		if s.hidden and not state:
			s.show(True)

	@property
	def x(s):
		x=s.xy.x
		return x

	@property
	def y(s):
		y=s.xy.y
		return y

	def save(s):
		return s.store.save(s.xy)
	def load(s,n):
		coord=s.store.load(n)
		s.xy=coord
		return coord
	def undo(s):
		current=s.store.selected
		coord=s.store._store[current]
		if coord is not None:
			s.xy=coord
			s.store.prev()
		return coord

#TODO: class vCursor(Cursor):
# 	def __init__(s, term,cursor):
# 		s.term = term
# 		s.realcursor=cursor
# 		s.position = Coord(s.realcursor.x,s.realcursor.y)
# 		s.history = [*(None,) * 64]
# 		s.controled = False
# 		s.bound = True
# 		s.frozen = False
# 		s.init = s.__update__()#
# 	def freeze(s, state=True):
# 		if state:
# 			s.frozen = True
# 			s.bind(False)
# 			s.control(False)
# 		else:
# 			s.frozen = False#
# 	def __update__(s, get='XY'):
# 		pass#
# 	def show(s, state=True):
# 		if state:
# 			print('\x1b[?25h', end='', flush=True)
# 		else:
# 			s.hide()#
# 	def hide(s, state=True):
# 		if state:
# 			import atexit
# 			print('\x1b[?25l', end='', flush=True)
# 			atexit.register(s.show)
# 		else:
# 			s.show()
#
