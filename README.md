Python Extensible Compilation Framework
=====

Instead of inventing a new scripting language, this project allows Python to be
used as the scripting interface. When processed, the scripts will be
automatically turned into the desired compiled code.

This also contains code for an abstract script engine that can be extended
(or replaced with a matching interface) for use within the scripting.

```
from ext import engine

# Begin user script

a = engine.var(0)
b = engine.var(10)

a = b + 1
engine.while(a > 4):
   a -= 3
if engine.branch(a == 2):
    a = engine.var(50)

def absdouble(x):
    if x < 0:
        return x*-2
    else:
        return x*2
    
a = absdouble(a)

engine.message(a)  # Some custom command

```