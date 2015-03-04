
from expression import ExpressionBlock


class Decompiler(ExpressionBlock):
    def __init__(self, handle, level=0):
        ExpressionBlock.__init__(level)
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

    def parse(self):
        while True:
            self.lines += self.parse_next()
            if self.lines and self.lines[-1].is_return():
                break
        self.lines = self.simplify(self.lines)
        return self.lines

    def parse_next(self):
        data = self.read_value(4)
        if not data:
            return [self.end()]
        return [self.unknown(data, 4)]

    def simplify(self, parsed):
        return parsed
