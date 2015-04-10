
try:
    from io import BytesIO
    binary_type = bytes
except:
    from StringIO import StringIO as BytesIO
    binary_type = str

from compileengine.variable import Variable


class VariableCollection(object):
    def __init__(self, engine):
        self.engine = engine
        self._cache = {}

    def __getattr__(self, name):
        try:
            return self._cache[name]
        except KeyError:
            var = Variable()
            var.name = name
            self._cache[name] = var
            return var

    def __setattr__(self, name, value):
        var = getattr(self, name)
        var.value = value


class FunctionCollection(VariableCollection):
    def __setattr__(self, name, value):
        raise TypeError('Cannot set a function')


class Engine(BytesIO):
    """Execute a decompiled function with this object to compile it
    """
    variable_collection_class = VariableCollection
    function_collection_class = FunctionCollection

    def __init__(self):
        BytesIO.__init__(self)
        self.vars = self._init_vars()
        self.funcs = self._init_funcs()

    def write_value(self, value, size=4):
        """Write a fixed length value to the buffer

        Parameters
        ----------
        value : int
            Unsigned value to write
        size : int
            Number of bytes that value should occupy
        """
        buff = binary_type()
        for i in range(size):
            buff += chr((value >> i) & 0xFF)
        self.write(buff)

    def reset(self):
        self.truncate(0)

    def _init_vars(self):
        return VariableCollection(self)

    def _init_funcs(self):
        return FunctionCollection(self)
