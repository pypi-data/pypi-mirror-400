# /usr/bin/env pyhthon
from enum import IntEnum


class Fml(IntEnum):
	ONE = 1
	TWO = 2
	FIRST = 1
	SECOND = 2


a=Fml.ONE
b=Fml.FIRST

def fnc(totest=Fml.TWO):
	if totest == 1:
		print('yeey')
	if totest != 2:
		print('notwo')

fnc(a)