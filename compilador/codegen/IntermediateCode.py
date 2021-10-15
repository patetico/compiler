import logging

from ._base import CodeGenerator
from ..symbols_table import normalize_name
from ..token import Token


_logger = logging.getLogger(__name__)


def _reduce_to_arg(var) -> str:
    if isinstance(var, Token) and var.is_number:
        return var.valor

    if isinstance(var, int):
        return str(var)

    return normalize_name(var)


def base(op, arg1='', arg2='', res=''):
    arg1 = _reduce_to_arg(arg1)
    arg2 = _reduce_to_arg(arg2)
    res = _reduce_to_arg(res)
    code = f'{op};{arg1};{arg2};{res}'
    _logger.debug(code)
    return code


class IntermediateCode(CodeGenerator):
    def __init__(self):
        super().__init__()
        self._if_stack = []

    def __pop_stack(self):
        line, cond = self._if_stack.pop()
        next_line = len(self.code)
        if cond is None:
            self.code[line] = base('goto', next_line)
        else:
            self.code[line] = base('JF', cond, next_line)

    def op(self, op, arg1='', arg2='', res=''):
        self.code.append(base(op, arg1, arg2, res))

    def alme(self, arg1, res):
        return self.code.append(base('ALME', arg1, res=res))

    def read(self, res):
        return self.code.append(base('read', res=res))

    def write(self, arg1):
        return self.code.append(base('write', arg1))

    def goto(self, arg1):
        return self.code.append(base('goto', arg1))

    def jf(self, arg1, arg2):
        return self.code.append(base('JF', arg1, arg2))

    def uminus(self, arg1, res):
        return self.code.append(base('uminus', arg1, res=res))

    def para(self):
        return self.code.append(base('PARA'))

    def if_(self, cond: Token):
        line = len(self.code)
        self._if_stack.append((line, cond))
        self.code.append(None)

    def else_(self):
        line = len(self.code)
        self.code.append(None)
        self.__pop_stack()
        self._if_stack.append((line, None))

    def close_if(self):
        self.__pop_stack()

    def while_(self, cond: Token):
        pass

    def close_while(self):
        pass
