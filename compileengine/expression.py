
class Expression(object):
    def __init__(self, level, func, *args):
        self.level = level
        self.func = func
        self.args = args

    def __str__(self):
        return '{space}engine.{func}({args})'.format(
            space='    '*self.level,
            func=self.func,
            args=','.join(str(arg) for arg in self.args))


class UnknownExpression(object):
    def __init__(self, level, value):
        self.level = level
        self.value = value

    def __str__(self):
        return '{space}eval(engine.unknown({value:#x}))'.format(
            space='    '*self.level,
            value=self.value)
