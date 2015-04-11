
from expression import ExpressionBlock


class Decompiler(ExpressionBlock):
    """Base Decompiler class for building expression blocks from a stream

    Attributes
    ----------
    handle : readable
        File handle to read from. This should be seeked to the start of
        the expression.
    start : int
        Location parsing begins. Defaults to handle.tell()
    stop : int or None
        If specified, parsing will forcibly stop once this byte is reached

    Methods
    -------
    parse : ()
        Parse and store this expression

    See Also
    --------
    compileengine.expression.ExpressionBlock
    compileengine.expression.ExpressionIterator
    """
    def __init__(self, handle):
        ExpressionBlock.__init__(self)
        self.handle = handle
        self.start = handle.tell()
        self.stop = None

    def reset(self):
        self.handle.seek(self.start)
        self.lines = []

    def read(self, size=None):
        """Read from the handle
        """
        return self.handle.read(size)

    def read_value(self, size=None):
        """Read a value from the handle as an int based on `size`.

        This will return a UInt32 if 4 bytes are read, for example.

        Parameters
        ----------
        size : int
            Width in bytes of the returned datatype
        """
        value = 0
        shift = 0
        char = None
        for char in self.read(size):
            value += ord(char) << shift
            shift += 8
        if char is None:
            return None
        return value

    def tell(self):
        """Get position of handle
        """
        return self.handle.tell()

    def seek(self, ofs, whence=0):
        """Seek handle
        """
        return self.handle.seek(ofs, whence)

    def prepare(self):
        return []

    def parse(self):
        """Parse and store this expression as a whole
        """
        self.prepare()
        while True:
            if self.stop is not None and self.tell() >= self.stop:
                break
            self.lines += self.parse_next()
            if self.lines and self.lines[-1].is_return():
                break
        self.lines = self.simplify(self.lines)
        return self.lines

    def parse_next(self):
        """Parse the next set of values. This should be overridden in
        derived classes.

        Returns
        -------
        lines : list
            List of expressions to add to the block
        """
        data = self.read_value(4)
        if not data:
            return [self.end()]
        return [self.unknown(data, 4)]

    def simplify(self, parsed):
        """Simplify the parsed expression. This is called after processing.

        Parameters
        ----------
        parsed : list
            List of expressions

        Returns
        -------
        parsed : list
            Simplified list of expressions
        """
        return parsed
