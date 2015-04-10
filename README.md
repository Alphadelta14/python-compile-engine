Python Extensible Compilation Framework
=====

Instead of inventing a new scripting language, this project allows Python to be
used as the scripting interface. When processed, the scripts will be
automatically turned into the desired compiled code.

This also contains code for an abstract script engine that can be extended
(or replaced with a matching interface) for use within the scripting.

```

# A user script
def my_script(engine):
    engine.vars.b = 10
    engine.vars.a = engine.vars.b + 1

    while engine.loop(engine.vars.a > 4):
        engine.vars.a -= 3
    if engine.branch(engine.vars.a == 2):
        engine.vars.a = 50

    def absdouble(x):
        if engine.branch(x < 0):
            return x*-2
        else:
            return x*2

    engine.vars.a = absdouble(engine.vars.a)

    engine.funcs.message(engine.vars.a)  # Some custom command

```
