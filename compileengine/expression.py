
class Expression(object):
    def __init__(self, level, func, *args):
        self.level = level
        self.func = func
        self.args = args

    def __str__(self):
        return '{space}engine.{func}({args})'.format(
            space='    '*self.level,
            func=self.func,
            args=', '.join(str(arg) for arg in self.args))

    def is_return(self):
        return False


class UnknownExpression(Expression):
    def __init__(self, level, value, width=2):
        self.level = level
        self.value = value
        self.width = width

    def __str__(self):
        return '{space}eval(engine.unknown({value:#x}, {width}))'.format(
            space='    '*self.level,
            value=self.value,
            width=self.width)


class NoopExpression(Expression):
    def __init__(self, level=0):
        pass

    def __str__(self):
        return ''


class ReturnExpression(Expression):
    def __init__(self, level):
        self.level = level

    def __str__(self):
        return '{space}return'.format(
            space='    '*self.level)

    def is_return(self):
        return True


class AssignmentExpression(Expression):
    def __init__(self, level, dest, expression):
        self.level = level
        self.dest = dest
        self.expression = expression

    def __str__(self):
        return '{space}{dest} = {expression}'.format(
            space='    '*self.level,
            dest=self.dest,
            expression=self.expression)


class StatementExpression(Expression):
    def __init__(self, operator, *args):
        self.operator = operator
        self.args = args

    def __str__(self):
        return self.operator.join(map(str, self.args))
