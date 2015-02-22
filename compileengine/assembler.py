
from expression import Expression, UnknownExpression, NoopExpression, \
    ReturnExpression


class Disassembler(object):
    def __init__(self, handle, level=0):
        self.level = level
        self.handle = handle
        self.start = handle.tell()

    def reset(self):
        self.handle.seek(self.start)

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
        expr = self.parse_one()
        if not expr:
            raise StopIteration()
        return expr

    def __str__(self):
        self.reset()
        return '\n'.join(str(line) for line in self)

    def unknown(self, value):
        return UnknownExpression(self.level, value)

    def build(self, func, *args):
        return Expression(self.level, func, *args)

    def noop(self):
        return NoopExpression()

    def end(self):
        return ReturnExpression

    def parse_one(self):
        data = self.read_value(4)
        if not data:
            return
        return self.unknown(data)
