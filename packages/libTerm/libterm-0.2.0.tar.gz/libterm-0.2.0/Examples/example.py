# /usr/bin/env pyhthon
from libTerm import Term,Color,Coord

term=Term()
print(term.size.xy)
print(term.color.bg)
print(term.cursor.xy)
term.mode(Term.MODE.CTRL)
print('press q to resume:')
while True:
	if term.stdin.event:
		key=term.stdin.read()
		print('\x1b[3;1HKey:\x1b[32m {KEY}\x1b[m'.format(KEY=key),end='',flush=True)
		if key=='q':
			print('continuing')
			break



term.cursor.xy=Coord(10,5)
print('#',end='',flush=True)
term.cursor.move.down()
print('#',end='',flush=True)
term.cursor.move.right()
print('#',end='',flush=True)
term.cursor.move.up(2)
print('#',end='',flush=True)
term.cursor.move.abs(X=2,Y=12)
print('#',end='',flush=True)

print(term.mode(Term.MODE.normal))


