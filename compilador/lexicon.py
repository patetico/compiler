from enum import Enum

from .errors import CompilerSyntaxError
from .tape import Tape
from .token import Token, TokenType
from .tokenizer import Tokenizer


class Keywords(Enum):
    PROGRAM = Token(TokenType.IDENTIFICADOR, 'program')
    BEGIN = Token(TokenType.IDENTIFICADOR, 'begin')
    END = Token(TokenType.IDENTIFICADOR, 'end')
    REAL = Token(TokenType.IDENTIFICADOR, 'real')
    INTEGER = Token(TokenType.IDENTIFICADOR, 'integer')
    READ = Token(TokenType.IDENTIFICADOR, 'read')
    WRITE = Token(TokenType.IDENTIFICADOR, 'write')
    IF = Token(TokenType.IDENTIFICADOR, 'if')
    THEN = Token(TokenType.IDENTIFICADOR, 'then')
    ELSE = Token(TokenType.IDENTIFICADOR, 'else')

    @property
    def valor(self):
        return self.value.valor

    @property
    def tipo(self):
        return self.value.tipo


class Lexicon:
    def __init__(self, filepath: str):
        self.tape = Tape(filepath)
        self.tokenizer = Tokenizer(self.tape)

    def parse(self):
        self._programa()

    def _next_token(self, skip_whitespace=True):
        while True:
            token = self.tokenizer.next_token()
            if not skip_whitespace or token.tipo != TokenType.WHITESPACE:
                return token

    def _programa(self):
        token = self._next_token()
        if not token == Keywords.PROGRAM.value:
            raise CompilerSyntaxError.simples(
                repr(Keywords.PROGRAM.valor),
                repr(token.valor))

        token = self._next_token()
        if not token.tipo == TokenType.IDENTIFICADOR:
            raise CompilerSyntaxError.simples('identificador', repr(token.valor))
        if any(token == kw for kw in Keywords):
            raise CompilerSyntaxError(
                f'Palavra reservada não pode ser usada como identificador: {token.valor!r}')

        self._corpo()

        token = self._next_token()
        if not token == Token(TokenType.SIMBOLO, '.'):
            raise CompilerSyntaxError.simples(repr('.'), repr(token.valor))

    def _corpo(self):
        # TODO
        pass

    def _dc(self):
        # TODO
        pass

    def _mais_dc(self):
        # TODO
        pass

    def _dc_v(self):
        # TODO
        pass

    def _tipo_var(self):
        # TODO
        pass

    def _variaveis(self):
        # TODO
        pass

    def _mais_var(self):
        # TODO
        pass

    def _comandos(self):
        # TODO
        pass

    def _mais_comandos(self):
        # TODO
        pass

    def _comando(self):
        # TODO
        pass

    def _condicao(self):
        # TODO
        pass

    def _relacao(self):
        # TODO
        pass

    def _expressao(self):
        # TODO
        pass

    def _termo(self):
        # TODO
        pass

    def _op_un(self):
        # TODO
        pass

    def _fator(self):
        # TODO
        pass

    def _outros_termos(self):
        # TODO
        pass

    def _op_ad(self):
        # TODO
        pass

    def _mais_fatores(self):
        # TODO
        pass

    def _op_mul(self):
        # TODO
        pass

    def _pfalsa(self):
        # TODO
        pass
