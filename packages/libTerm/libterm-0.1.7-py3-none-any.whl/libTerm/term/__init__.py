#!/usr/bin/env python
import os,sys

if os.name == 'nt':
	from libTerm.term.winnt import Term
else:
	from libTerm.term.posix import Term

from libTerm.term.types import Coord,Color,Size,Mode