import logging

from compilador.symbols_table import Symbol


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

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


class ObjectCode:
    def __init__(self):
        self.code = []
        self.symbol_pos = 0
        self.symbols = dict()

    def _push(self, op: str, arg=''):
        _logger.debug(f'{op.upper()} {arg}')
        self.code.append(f'{op.upper()} {arg}')

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

    def if_(self, cond):
        pass

    def else_(self):
        pass

    def close_if(self):
        pass

    def while_(self, cond):
        pass

    def close_while(self):
        pass

    def assign(self, var: Symbol):
        self._push('ARMZ', var.data)
