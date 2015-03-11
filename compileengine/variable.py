
import string
import operator


def name_generator(prefix='local_'):
    idx = 0
    while True:
        # TODO: optimize (full recalculation not needed in loop)
        name = ''.join([string.ascii_lowercase[int(c, 10)]
                        for c in oct(idx)[1:]])
        yield prefix+name
        idx += 1


class Variable(object):
    def __init__(self, base=None):
        self.value = None
        self.name = 'default'

    def has_value(self):
        return self.value is not None

    def __str__(self):
        return 'engine.vars.{name}'.format(name=self.name)
