import select
from dataclasses import dataclass,field
from collections import namedtuple
from os import get_terminal_size
from  time import sleep, time_ns
import sys
from enum import IntEnum



class Mode(IntEnum):
	NONE    = 0
	none    = 1
	NRML    = 1
	nrml    = 1
	NORMAL  = 1
	normal  = 1
	DEFAULT = 1
	default = 1
	CTL     = 2
	ctl     = 2
	CTRL    = 2
	ctrl    = 2
	CONTROL = 2
	control = 2


@dataclass(frozen=True)
class Coord(namedtuple('Coord', ['x', 'y'])):
	__module__ = None
	__qualname__='Coord'
	_x: int = field(default=0)
	_y: int = field(default=0)

	def str__(s):
		return f'\x1b[{s.y + 1};{s.x + 1}H'

	def __repr__(s):
		return f'{s.__class__.__name__}({s.x}, {s.y})'

	def __len__(s):
		return 2
	def __iter__(s):
		yield s.x
		yield s.y
	def __getitem__(s, index):
		value=None
		if isinstance(index, int):
			value=(((index == 0)*s.x)+((index == 1)*s.y))
		elif isinstance(index, str):
			value = (((index == 'x') * s.x) + ((index == 'y') * s.y))
		if value is None:
			raise KeyError('index must be int 0 or 1 or str "x" or "y" ')
		return value
	def __add__(s, other):
		if isinstance(other,Coord):
			x=s.x+other.x
			y=s.y+other.y
			return Coord(x,y)
		elif isinstance(other,complex):
			x=s.x+other.real
			y=s.y+other.imag
			return Coord(x,y)
		elif isinstance(other,str):
			return f'{s.str__()}{other}'
		else:
			raise TypeError(f'cannot add {type(s)} to {type(other)}')


	def keys(s):
		return ('x', 'y')


	@property
	def xy(s) -> tuple[int, int]:
		return (s.x, s.y)

	@property
	def y(s):
		return s._y

	@property
	def x(s):
		return s._x

@dataclass(frozen=True)
class Color:
	R: int = field(default=0, metadata={'range': (0, 65535)})
	G: int = field(default=0, metadata={'range': (0, 65535)})
	B: int = field(default=0, metadata={'range': (0, 65535)})
	BIT: int = field(default=8, metadata={'set': (4, 8, 16, 32)})

	def __post_init__(s):
		rgb_error='{rgb} must be an integer between 0 and 65535. Got {value}.'
		bit_error='{rgb} must be one of 4,8,16,32. Got {value}.'
		for rgb in ('R', 'G', 'B'):
			value = getattr(s, rgb)
			if not isinstance(value, int):
				raise ValueError(rgb_error.format(rgb=rgb.upper(),value=value))
		if not isinstance(getattr(s, 'BIT'), int):
			raise ValueError(bit_error.format(rgb=rgb.upper(),value=value))

	@property
	def RGB(s) -> tuple[int, int, int]:
		return (s.R, s.G, s.B)

class Size():
	def __init__(s, **k):
		s.term = k.get('term')
		s.getsize = get_terminal_size
		s.time = None
		s.last = None
		s.xy = Coord(1, 1)
		s._tmp = Coord(1, 1)
		s.rows = 1
		s.cols = 1

		s.history = []
		s.changed = False
		s.changing = False
		s.__kwargs__(**k)
		s.__update__()

	@property
	def width(s):
		s.__update__()
		return s.cols
	@property
	def height(s):
		s.__update__()
		return s.rows
	@property
	def rc(s):
		s.__update__()
		return (s.cols, s.rows)

	def __kwargs__(s, **k):
		s.term = k.get('term')

	def __update__(s):
		if s.time is None:
			s.last = time_ns()
		size = Coord(*s.getsize())
		if size != s.xy:
			if size != s._tmp:
				s.changing = True
				s._tmp = size
				s._tmptime = time_ns()
			if size == s._tmp:
				if (time_ns() - s._tmptime) * 1e6 > 500:
					s.changing = False
					s.changed = True
					s.history += [s.xy]
					s.xy = size
					s.rows = s.xy.y
					s.cols = s.xy.x
				else:
					s._tmp = size
		if size == s.xy:
			s.changed = False

class Selector():

	def __init__(s,n, **k):
		s.selection = k.get('start', 0)
		s.n=n
		s.prev = lambda: s.selector(-1)
		s.next = lambda: s.selector(1)
		s.read = lambda: s.selector(0)
		s.write = s.setval

	def wrap(s,ss):
		return  ~(~ss * -~-s.n) % s.n

	def selector(s,i):
		s.selection = s.wrap(s.selection + i)
		return s.selection

	def setval(s,i):
		s.selection = s.wrap(i)
		return s.selection

class Store():
	def __init__(s, **k):
		"""Simple contiguous store backed by a list of values.

		Keys are 1-based integers (1..n). Internally values are stored in
		`s._values` where index 0 corresponds to key 1.

		Pointer semantics:
		- s._pointer ranges from -1 .. len(s._values)
		- -1 means before-first
		- 0..len-1 means index into values (current)
		- len means after-last

		By default the store has unlimited size; use `setmax` to bound it.
		"""
		s._store = {0:None,}
		s.tail=1
		s.size=lambda:len(s._store)
		s._current= 0
		s._pointer = lambda:s._values.get(s._current)
		s._max = None

		s.select=Selector(s.size())
		s.selected = s.select.read()
		s._value=s._store[s.selected]

	def setmax(s, maximum):
		"""Set maximum number of stored items (None = unlimited)."""
		result = None
		if maximum is not None:
			if not isinstance(maximum, int) or maximum < 1:
				raise ValueError('maximum must be a positive int or None')
		s._max = maximum
		return result
	def read(s):
		s.selected = s.select.read()
		return s.selected
	def write(s,index):
		s.select.write(index)
		s.selected = s.select.read()
		return s.selected
	@property
	def value(s):
		s.read()
		s._value=s._store[s.selected]
		return s._value

	def save(s, value):
		s._store[s.size()]=value
		s.tail+=1
		current=s.read()
		s.select=Selector(s.tail)
		s.write(current+1)
		s.read()
		return s.selected

	def load(s):
		s.read()
		return s._store[s.selected]

	def remove(s):
		s.read()
		value=s._store.pop(s.selected)
		return value

	def clear(s):
		result = None
		s._store.clear()
		s._tail = 1
		s._current=0
		s.select=Selector(s.size())
		s.read()
		return

	def prev(s):
		s.selected=s.select.prev()
		return s._store[s.selected]


	def next(s):
		s.selected=s.select.next()
		return s._store[s.selected]

	def replace(s, index: int, value):
		s.read()
		s._store[s.selected]=value


	def __len__(s):
		result = len(s._values)
		return result

	def keys(s):
		"""Return the list of integer keys (1-based)."""
		result = list(range(1, len(s._values) + 1))
		return result
