import logging

from compilador.symbols_table import Symbol


_logger = logging.getLogger(__name__)

opcodes = {
    '/': 'DIVI',
    '*': 'MULT',
    '-': 'SUBT',
    '+': 'SOMA',
    '=': 'CPIG',
    '<>': 'CDES',
    '>=': 'CMAI',
    '<=': 'CPMI',
    '>': 'CPMA',
    '<': 'CPME',
}


def mkcode(op, arg):
    return f'{op.upper()} {arg}'


class ObjectCode:
    def __init__(self):
        self.code = []
        self.symbol_pos = 0
        self.symbols = dict()
        self._if_stack = []
        self._while_stack = []

    def _push(self, op: str, arg=''):
        code = mkcode(op, arg)
        _logger.debug(code)
        self.code.append(code)

    def inpp(self):
        self._push('INPP')

    def alme(self, res):
        self._push('ALME', '1')
        pos = self.symbol_pos
        self.symbols[res] = pos
        self.symbol_pos += 1
        return pos

    def read(self, var: Symbol):
        self._push('LEIT')
        self.assign(var)

    def write(self, var):
        self.stack(var)
        self._push('IMPR')

    def para(self):
        self._push('PARA')

    def uminus(self):
        self._push('INVE')

    def stack(self, token):
        if isinstance(token, Symbol):
            self._push('CRVL', token.data)
        else:
            self._push('CRCT', token)

    def op(self, op):
        self._push(opcodes[op])

    def __pop_if_stack(self):
        line, op = self._if_stack.pop()
        next_line = len(self.code)
        self.code[line] = mkcode(op, next_line)

    def if_(self):
        line = len(self.code)
        self.code.append(None)
        self._if_stack.append((line, 'DSVF'))

    def else_(self):
        line = len(self.code)
        self.code.append(None)
        self.__pop_if_stack()
        self._if_stack.append((line, 'DSVI'))

    def close_if(self):
        self.__pop_if_stack()

    def while_(self):
        line = len(self.code)
        self._while_stack.append([line, None])

    def do_(self):
        self._while_stack[-1][1] = len(self.code)
        self.code.append(None)

    def close_while(self):
        l1, l2 = self._while_stack.pop()
        self._push('DSVI', l1)
        next_line = len(self.code)
        self.code[l2] = mkcode('DSVF', next_line)

    def assign(self, var: Symbol):
        self._push('ARMZ', var.data)
