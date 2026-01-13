# /usr/bin/env pyhthon
from libTerm import Term,Color,Coord

term=Term()
print(term.size.xy)
print(term.color.bg)
print(term.cursor.xy)
term.mode(Term.MODE.CTRL)

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


