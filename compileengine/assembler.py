
from expression import Expression, UnknownExpression, NoopExpression, \
    ReturnExpression, AssignmentExpression, StatementExpression


class Disassembler(object):
    def __init__(self, handle, level=0):
        self.level = level
        self.handle = handle
        self.start = handle.tell()
        self.returned = False  # for next()
        self._parsed_queue = []

    def reset(self):
        self.handle.seek(self.start)
        self.returned = False

    def read(self, size=None):
        return self.handle.read(size)

    def read_value(self, size=None):
        value = 0
        shift = 0
        for char in self.read(size):
            value += ord(char) << shift
            shift += 8
        return value

    def tell(self):
        return self.handle.tell()

    def seek(self, ofs, whence=0):
        return self.handle.seek(ofs, whence)

    def __iter__(self):
        return self

    def next(self):
        try:
            expr = self._parsed_queue.pop(0)
        except:
            self._parsed_queue = self.parse_next()
            if not self._parsed_queue:
                expr = None
            else:
                expr = self._parsed_queue.pop(0)
        if not expr:
            raise StopIteration()
        if self.returned:
            self.returned = False
            raise StopIteration()
        if expr.is_return():
            self.returned = True
        return expr

    def __str__(self):
        self.reset()
        return '\n'.join(str(line) for line in self.parse_all())

    def parse_all(self):
        self.reset()
        parsed = [expr for expr in self]
        return self.simplify(parsed)

    def unknown(self, value, width=2):
        return UnknownExpression(self.level, value, width)

    def build(self, func, *args, **kwargs):
        level = kwargs.get('level', self.level)
        return Expression(level, func, *args)

    def noop(self):
        return NoopExpression(self.level)

    def end(self):
        return ReturnExpression(self.level)

    def add(self, *args):
        return self.statement('+', *args)

    def assign(self, dest, statement):
        return AssignmentExpression(self.level, dest, statement)

    def statement(self, operator, *args):
        return StatementExpression(operator, *args)

    def parse_next(self):
        data = self.read_value(4)
        if not data:
            return [self.end()]
        return [self.unknown(data)]

    def simplify(self, parsed):
        return parsed
