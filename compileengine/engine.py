
import itertools

try:
    from io import BytesIO
    binary_type = bytes
except:
    from StringIO import StringIO as BytesIO
    binary_type = str

from compileengine.variable import Variable


class VariableCollection(object):
    def __init__(self, engine):
        object.__setattr__(self, '_cache', {})
        object.__setattr__(self, 'engine', engine)

    def _create(self, name):
        var = Variable()
        var.name = name
        var.engine = self.engine
        return var

    def __getattr__(self, name):
        try:
            return self._cache[name]
        except KeyError:
            var = self._create(name)
            self._cache[name] = var
            return var

    def __setattr__(self, name, value):
        var = getattr(self, name)
        var.value = value


class Function(Variable):
    """Function

    This variable type is callable
    """
    def __call__(self, *args):
        # self.engine.func(self, *args)
        return


class FunctionCollection(VariableCollection):
    def __setattr__(self, name, value):
        raise TypeError('Cannot set a function')

    def _create(self, name):
        var = Function()
        var.name = name
        var.engine = self.engine
        return var


class NewBranch(Exception):
    pass


class EngineBlock(object):
    """Stored compiled block

    Attributes
    ----------
    engine : Engine
        Reference to parent engine
    buff : str
        Value of block
    jumps : dict
        Map of offset (relative to block start) to another block
    offset : int, optional
        Determined offset of block
    """
    def __init__(self, engine):
        self.engine = engine
        self.buff = None
        self.jumps = {}
        self.offset = -1

    def __eq__(self, other):
        if self is other:
            return True
        if len(self.buff) != len(other.buff):
            return False
        idx = 0
        while idx < len(self.buff):
            if idx in self.jumps:
                if idx not in other.jumps:
                    return False
                if self.jumps[idx] != other.jumps[idx]:
                    return False
                idx += self.engine.pointer_size
                continue
            byte1 = self.buff[idx]
            byte2 = other.buff[idx]
            if byte1 != byte2:
                return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Engine(BytesIO):
    """Execute a decompiled function with this object to compile it
    """
    variable_collection_class = VariableCollection
    function_collection_class = FunctionCollection
    pointer_size = 4

    STATE_IDLE = 0
    STATE_BUILDING_BRANCHES = 1

    def __init__(self):
        BytesIO.__init__(self)
        self.vars = self._init_vars()
        self.funcs = self._init_funcs()
        self.state = self.STATE_IDLE
        self.stack = []
        self.current_block = EngineBlock(self)

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

    def push(self):
        block = self.current_block
        block.buff = self.getvalue()
        self.truncate(0)
        self.stack.append(block)

    def pop(self):
        self.current_block.buff = self.getvalue()
        block = self.stack.pop()
        self.truncate(0)
        self.write(block.buff)

    def _init_vars(self):
        return VariableCollection(self)

    def _init_funcs(self):
        return FunctionCollection(self)

    def compile(self, func):
        self.find_branches(func)

    def find_branches(self, func):
        self.paths = [()]
        self.loops = []
        self.state = self.STATE_BUILDING_BRANCHES
        self.path_id = 0
        while self.path_id < len(self.paths):
            self.current_path = self.paths[self.path_id]
            self.branch_id = 0
            try:
                func(self)
            except NewBranch:
                self.paths[self.path_id] = self.current_path+(NewBranch,)
            self.path_id += 1
        self.paths = [path for path in self.paths if path[-1] != NewBranch]
        self.state = self.STATE_IDLE

    def branch(self, condition):
        try:
            value = self.current_path[self.branch_id]
            self.branch_id += 1
            return value
        except IndexError:
            self.paths.append(self.current_path+(True, ))
            self.paths.append(self.current_path+(False, ))
            raise NewBranch

    def loop(self, condition):
        return False
