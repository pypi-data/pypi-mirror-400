import importlib
import sys
import unittest
from libTerm import Term
from libTerm.term.types import Coord
POSIX_MODULE = 'libTerm.term.posix'

TTY = sys.stdin.isatty()

@unittest.skipUnless(TTY, "Requires a real TTY to run terminal-integration tests")
class TestPosixTerm(unittest.TestCase):
	def setUp(self):
		# Create a Term instance that will use the real terminal APIs.
		# mod = importlib.import_module(POSIX_MODULE)
		self.Term = Term
		self.t = self.Term()

	def tearDown(self):
		# Attempt to restore a normal terminal mode when possible.
		try:
			self.t.mode('normal')
		except Exception:
			pass

	def test_init_basic_fields_set(self):
		self.assertTrue(hasattr(self.t, 'pid'))
		self.assertTrue(hasattr(self.t, 'ppid'))
		self.assertTrue(hasattr(self.t, 'fd'))
		self.assertTrue(hasattr(self.t, 'tty'))
		self.assertTrue(hasattr(self.t, 'cursor'))
		self.assertTrue(hasattr(self.t, 'size'))
		self.assertTrue(hasattr(self.t, 'color'))
		self.assertTrue(isinstance(self.t.attr.active, list))

	def test_mode_switch_changes_internal_mode(self):
		# Switch modes and check the internal indicator changes.
		self.t.mode('ctl')
		self.assertEqual(self.t._mode, 2)
		self.t.mode('normal')
		self.assertEqual(self.t._mode, 1)

	def test_echo_and_canonical_toggle_do_not_raise(self):
		# Ensure these calls execute against the real terminal without raising.
		self.t.echo(False)
		self.t.echo(True)
		self.t.canonical(False)
		self.t.canonical(True)

	def test_update_and_stage_restore_do_not_error(self):
		# Stage, update and restore attributes to ensure call paths succeed.
		self.t.attr.stage()
		# mutate staged safely if present
		try:
			if isinstance(self.t.attr.staged, list):
				self.t.attr.staged[3] = self.t.attr.staged[3]
		except Exception:
			pass
		# Attempt to apply staged attributes; this will perform real tcsetattr calls.
		self.t._update_()
		# Attempt a restore
		restored = self.t.attr.restore()
		# restore might be None or a list; ensure the call succeeded
		self.assertTrue(restored is None or isinstance(restored, list))

	def test_coord_iter_and_mapping(self):
		from libTerm.term.types import Coord
		loc = Coord(5, 6)
		self.assertEqual(list(loc), [5, 6])
		self.assertEqual(dict(**loc), {'x': 5, 'y': 6})

	def test_cursor(self):
		import time
		xy=self.t.cursor.xy
		self.assertIsInstance(xy,Coord)
		self.t.mode('normal')
		self.t.echo(True)
		self.t.cursor.show(False)
		self.t.cursor.hide(True)
		print('\x1b[B\x1b[D▌',flush=True)
		for i in range(8):
			for i in range(20):
				print('\x1b[B\x1b[D░' 	,end='',flush=True)
				val=self.t.cursor.save();time.sleep(0.01)
			val = self.t.cursor.save();	time.sleep(0.01)
			for i in range(6):
				val=self.t.cursor.save();time.sleep(0.01)
				print('░',end='',flush=True)

			val = self.t.cursor.save();	time.sleep(0.01)

			for i in range(20):
				print('\x1b[A\x1b[D░',end='',flush=True)
				val = self.t.cursor.save();	time.sleep(0.01)
			for i in range(6):
				val=self.t.cursor.save();time.sleep(0.01)
				print('░',end='',flush=True)
			val = self.t.cursor.save();	time.sleep(0.01)

		for i in range(380):
			self.t.cursor.undo()
			print('\x1b[D ',end='',flush=True)
			time.sleep(0.01)
	def test_cursor2(self):
		import time
		xy=self.t.cursor.xy
		self.assertIsInstance(xy,Coord)
		self.t.mode('normal')
		self.t.echo(True)
		self.t.cursor.show(False)
		self.t.cursor.hide(False)
		self.t.cursor.hide(True)
		print('\x1b[B\x1b[D▌',flush=True)
		for i in range(8):
			for i in range(20):
				print('\x1b[B\x1b[D\x1b[38;2;0;255;0m░\x1b[m' 	,end='',flush=True)
				val=self.t.cursor.save()
			val = self.t.cursor.save();
			for i in range(6):
				val=self.t.cursor.save()
				print('░',end='',flush=True)

			val = self.t.cursor.save();

			for i in range(20):
				print('\x1b[A\x1b[D░',end='',flush=True)
				val = self.t.cursor.save();
			for i in range(6):
				val=self.t.cursor.save();
				print('░',end='',flush=True)
			val = self.t.cursor.save();

		for i in range(380):
			self.t.cursor.undo()
			print('\x1b[D ',end='',flush=True)
			time.sleep(0)

if __name__ == '__main__':
	unittest.main()
