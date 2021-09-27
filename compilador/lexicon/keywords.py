from enum import Enum

from ..errors import CompilerSyntaxError
from ..token import Token


class Keywords(Enum):
    PROGRAM = Token.identificador('program')
    BEGIN = Token.identificador('begin')
    END = Token.identificador('end')
    REAL = Token.identificador('real')
    INTEGER = Token.identificador('integer')
    READ = Token.identificador('read')
    WRITE = Token.identificador('write')
    IF = Token.identificador('if')
    THEN = Token.identificador('then')
    ELSE = Token.identificador('else')

    def wrong_token_err(self, token: Token):
        return CompilerSyntaxError.simples(self.value, token)
