

class ExpressionBlockIterator(object):
    """Iterator over an Expression Block. Each iteration returns the next
    expression at the appropriate level.

    This is automatically returned when iterating an ExpressionBlock.

    Example
    -------
    >>> block = ExpressionBlock()
    >>> block2 = ExpressionBlock(1)
    >>> block.lines = [block.func('my_func', 1, 2),
    ... block.func('my_func', 3, 4),
    ... block.noop(),
    ... block2,
    ... block.end()]
    >>> block2.lines = [
    ... block2.noop()
    ... block2.func('my_func, 2, 3)
    ... block2.end()]
    >>> for expr in block:
    ... print(expr)
    engine.my_func(1, 2)
    engine.my_func(3, 4)
        engine.my_func(2, 3)
    return
    """
    def __init__(self, block):
        self.stack = [[block, 0]]

    def next(self):
        """Return the next expression from the current block. If there are
        no more lines in the current block, visit the parent item on the
        stack. If there are no more items in the stack, end the loop.
        """
        while self.stack:
            block, lineno = self.stack[-1]
            lines = block.header_lines+block.lines+block.footer_lines
            while True:
                try:
                    expr = lines[lineno]
                except IndexError:
                    break
                lineno += 1
                self.stack[-1][1] = lineno
                try:
                    if expr.is_block():
                        self.stack.append([expr, 0])
                        return self.next()
                except:
                    pass
                if expr:
                    return expr
            self.stack.pop()
        raise StopIteration()


class Expression(object):
    """Base Expression representing a function. This can be subclassed
    for different functionality.

    To get the textual representation, use `str(expr)`.

    Attributes
    ----------
    indent : int
        How deep this expression is. This determines how many spaces go before
        it on a line.
    name : str
        Name of the function being called. This should be a method belonging to
        the active Engine.
    *args : list of args
        Arguments passed to the function

    Example
    -------
    >>> print(str(Expression(2, 'my_func', 1, 2)))
            engine.my_func(1, 2)
    >>> print(str(Expression(0, 'my_func2')))
    engine.my_func2()
    """
    indent = 0

    def __init__(self, name, *args, **kwargs):
        self.indent = kwargs.get('indent', 0)
        self.name = name
        self.args = args
        self.namespace = kwargs.get('namespace', 'engine.')

    def __str__(self):
        return '{space}{namespace}{func}({args})'.format(
            space='    '*self.indent,
            namespace=self.namespace,
            func=self.name,
            args=', '.join(str(arg) for arg in self.args))

    def is_return(self):
        return False

    def is_block(self):
        return False


class UnknownExpression(Expression):
    """An unknown expression. The value passed in here will be written back
    raw.

    Attributes
    ----------
    value : int
        Raw value
    width : int
        Number of bytes this should be padded to.

    """
    def __init__(self, value, width=2):
        self.value = value
        self.width = width

    def __str__(self):
        return '{space}eval(engine.unknown({value:#x}, {width}))'.format(
            space='    '*self.indent,
            value=self.value,
            width=self.width)


class NoopExpression(Expression):
    """An empty expression.
    """
    def __str__(self):
        return ''

    def __bool__(self):
        return False
    __nonzero__ = __bool__


class ReturnExpression(Expression):
    """A return expression.

    This is the last expression of a block.
    """
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return '{space}return {args}'.format(
            space='    '*self.indent,
            args=', '.join(str(arg) for arg in self.args))

    def is_return(self):
        return True


class AssignmentExpression(Expression):
    """An assigment expression

    This indicates that a left-value should be assigned the result of an
    expression or other right-value.

    Attributes
    ----------
    dest : string
        Destination left-value
    expression : Expression or mixed
        Value or expression to be assigned to `dest`.

    Example
    -------
    >>> print(AssignmentExpression(0, 'engine.vars.b', 42))
    engine.vars.b = 42
    """
    def __init__(self, dest, expression):
        self.dest = dest
        self.expression = expression

    def __str__(self):
        try:
            dest = ', '.join(str(d.get_name()) for d in self.dest)
        except:
            dest = self.dest.get_name()
        return '{space}{dest} = {expression}'.format(
            space='    '*self.indent,
            dest=dest,
            expression=self.expression)


class StatementExpression(Expression):
    """Statement expression for applying an operator to arguments

    Attributes
    ----------
    operator : str
        Operator to apply to `args`
    *args : list
        Target list of arguments
    """
    def __init__(self, operator, *args):
        self.operator = operator
        self.args = args

    def __str__(self):
        return self.operator.join(map(str, self.args))


class ContextExpression(Expression):
    """Creates a context manager and potentially assigns it

    Attributes
    ----------
    expression : Expression or mixed
        Value or expression to be assigned to `dest`.
    dest : string
        Destination right value. Optional.
    """
    def __init__(self, expression, dest=None):
        self.expression = expression
        self.dest = dest

    def __str__(self):
        if self.dest is None:
            dest = ''
        else:
            dest = ' as {dest}'.format(dest=self.dest)
        return '{space}with {expression}{dest}:'.format(
            space='    '*self.indent,
            expression=self.expression,
            dest=dest)


class ConditionalExpression(Expression):
    """
    Attributes
    ----------
    conditional : Statement or Expression
    loop_type : (TYPE_IF, TYPE_WHILE)
        Specifies type of condition. Defaults to TYPE_IF (no loop)

    Notes
    -----
    Values such as None, False, and True are valid conditional expressions
    """
    TYPE_IF = 0
    TYPE_WHILE = 1

    def __init__(self, conditional=None, loop_type=0):
        self.conditional = conditional
        self.loop_type = loop_type

    def __str__(self):
        if self.loop_type == self.TYPE_IF:
            prefix = 'if'
        elif self.loop_type == self.TYPE_WHILE:
            prefix = 'while'
        return '{space}{prefix} engine.branch({conditional}):'.format(
            prefix=prefix,
            space='    '*self.indent,
            conditional=str(self.conditional))


class ExpressionBlock(Expression):
    """Block of expressions. This contains a list of expressions

    Attributes
    ----------
    lines : list
        List of expressions in block body
    indent : int
        Indentation of body
    """
    def __init__(self, indent=1):
        self.indent = indent
        self.lines = []
        self.header_indent = indent-1
        self.header_lines = []
        self.footer_indent = indent-1
        self.footer_lines = []

    def is_block(self):
        return True

    def __iter__(self):
        return ExpressionBlockIterator(self)

    def __str__(self):
        out = []
        for indent, lines in ((self.header_indent, self.header_lines),
                              (self.indent, self.lines),
                              (self.footer_indent, self.footer_lines)):
            for expr in lines:
                for line in str(expr).split('\n'):
                    out.append(
                        '{space}{line}'.format(
                            space='    '*indent,
                            line=line))
        return '\n'.join(out)
        # return '\n'.join(str(line) for line in self)

    def unknown(self, value, width=2):
        return UnknownExpression(self.indent, value, width)

    def func(self, name, *args, **kwargs):
        indent = kwargs.pop('indent', kwargs.pop('level', self.indent))
        kwargs['namespace'] = kwargs.pop('namespace', 'engine.funcs.')
        return Expression(name, *args, **kwargs)

    def noop(self):
        return NoopExpression()

    def end(self, *args):
        return ReturnExpression(*args)

    def add(self, *args):
        return self.statement('+', *args)

    def assign(self, dest, statement, assign_var=True):
        try:
            if assign_var:
                dest.value = statement
        except:
            pass
        return AssignmentExpression(dest, statement)

    def context(self, expression, dest=None):
        return ContextExpression(expression, dest)

    def condition(self, statement):
        return ConditionalExpression(statement)

    def while_loop(self, statement):
        return ConditionalExpression(statement,
                                     ConditionalExpression.TYPE_WHILE)

    def statement(self, operator, *args):
        return StatementExpression(operator, *args)
