
import string
import operator

OP_PRECEDENCE = [
    (operator.mul, ),
    (operator.add, operator.sub)
]


class Variable(object):
    def __init__(self, base=None, value=None):
        self.base = base
        self.value = value
        self.name = None
        self.refcount = 0
        self.persist = False
        self.refby = []

    def has_value(self):
        return self.value is not None

    def __str__(self):
        if not self.persist and self.refcount < 2:
            # TODO: complex stringification
            return str(self.value)
        return self.get_name()

    def get_name(self):
        if self.name is None:
            name = 'default_{0:x}'.format(id(self))
        else:
            name = self.name
        return 'engine.vars.{name}'.format(name=name)

    """def __add__(self, other):
        self.refcount += 1
        if isinstance(other, Variable):
            other.refcount += 1
        else:
            try:
                oper, operand1, operand2 = self.value
                if oper == operator.add:
                    try:
                        new_operand2 = operand2+other
                        if not isinstance(new_operand2, Variable):
                            return Variable(value=[operator.add, operand1, new_operand2])
                    except:
                        pass
                    try:
                        new_operand1 = operand1+other
                        if not isinstance(new_operand1, Variable):
                            return Variable(value=[operator.add, new_operand1, operand2])
                    except:
                        pass
            except:
                return Variable(value=[operator.add, self, other])"""

    def operate(self, oper, other):
        self.refcount += 1
        new_var = Variable()
        self.refby.append(new_var)
        if isinstance(other, Variable):
            other.refcount += 1
            other.refby.append(new_var)
        new_var.value = (oper, self.value, other)
        return new_var

    def __add__(self, other):
        if other is 0:
            return self
        return self.operate(operator.add, other)

    def __sub__(self, other):
        if other is 0:
            return self
        return self.operate(operator.sub, other)

    def __mul__(self, other):
        if other is 1:
            return self
        return self.operate(operator.mul, other)

    def __neg__(self):
        return self.operate(operator.mul, -1)

    def __lshift__(self, other):
        if other is 0:
            return self
        return self.operate(operator.lshift, other)

    def __rshift__(self, other):
        if other is 0:
            return self
        return self.operate(operator.rshift, other)

    @staticmethod
    def name_generator(prefix='local_'):
        idx = 0
        while True:
            # TODO: optimize (full recalculation not needed in loop)
            name = ''.join([string.ascii_lowercase[int(c, 10)]
                            for c in '{0:o}'.format(idx)])
            yield prefix+name
            idx += 1
