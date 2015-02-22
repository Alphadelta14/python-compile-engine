
from expression import Expression, UnknownExpression


class Disassembler(object):
    def __init__(self, handle, level=0):
        self.level = level
        self.handle = handle

    def read(self, size=None):
        return self.handle.read(size)

    def read_value(self, size=None):
        value = 0
        shift = 0
        for char in self.read(size):
            value += ord(char) << shift
            shift += 8
        return value

    def __iter__(self):
        return self

    def next(self):
        expr = self.parse()
        if not expr:
            raise StopIteration()
        return expr

    def unknown(self, value):
        return UnknownExpression(self.level, value)

    def build(self, func, *args):
        return Expression(self.level, func, *args)

    def parse(self):
        data = self.read_value(4)
        if not data:
            return
        return self.unknown(data)
