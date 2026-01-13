# /usr/bin/env pyhon
import sys
import unittest
from libTerm import Term
from libTerm.term.types import Coord
import ast


class TestCursor(unittest.TestCase):
	term=Term()
	cursor=term.cursor
		
	def test_cursor(s):
		s.assertIsInstance(s.cursor.xy,Coord)
		s.cursor.xy=Coord(2,2)
		s.assertEqual(s.cursor.xy,Coord(2,2))



	# def test_position_calls_underlying_term_and_returns_coord(self):
	# 	# position is set to __update__ in __init__, calling it should return the fake coord
	# 	self.fake.set_coord(Coord(7, 8))
	# 	result = self.cursor.position()
	# 	self.assertIsInstance(result, Coord)
	# 	self.assertEqual(result, Coord(7, 8))
	#
	# def test_XY_updated_by_position(self):
	# 	# calling position should update cursor.XY attribute
	# 	self.fake.set_coord(Coord(11, 12))
	# 	_ = self.cursor.position()
	# 	self.assertEqual(self.cursor.XY, Coord(11, 12))
	#
	# def test_ansi_enum_repr(self):
	# 	# repr on enum members should return repr of their value (stable and safe)
	# 	self.assertEqual(repr(ANSI_Cursor.show), repr(ANSI_Cursor.show.value))

if __name__ == '__main__':
	unittest.main()
