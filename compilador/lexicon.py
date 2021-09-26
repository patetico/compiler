from enum import Enum

from .errors import CompilerSyntaxError
from .tape import Tape
from .token import Token, TokenType
from .tokenizer import Tokenizer


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

    @property
    def valor(self):
        return self.value.valor

    @property
    def tipo(self):
        return self.value.tipo

    def wrong_token_err(self, token: Token):
        return CompilerSyntaxError.simples(repr(self.valor), repr(token.valor))


def validate_ident(token: Token):
    if not token.tipo == TokenType.IDENTIFICADOR:
        raise CompilerSyntaxError.simples('identificador', repr(token.valor))

    if any(token == kw.valor for kw in Keywords):
        raise CompilerSyntaxError(
            f'Palavra reservada não pode ser usada como identificador: {token.valor!r}')


def validate_symbol(token: Token, symbol: str):
    if not token == Token.simbolo(symbol):
        raise CompilerSyntaxError.simples(repr(symbol), repr(token.valor))


class Lexicon:
    def __init__(self, filepath: str):
        self.tape = Tape(filepath)
        self.tokenizer = Tokenizer(self.tape)

    def parse(self):
        self._programa()

    def _next_token(self, skip_whitespace=True, dont_move=False):
        pos = self.tape.pos
        while True:
            token = self.tokenizer.next_token()
            if not skip_whitespace or token.tipo != TokenType.WHITESPACE:
                if dont_move:
                    self.tape.pos = pos
                return token

    def _get_ident(self) -> Token:
        token = self._next_token()
        validate_ident(token)
        return token

    def _programa(self):
        token = self._next_token()
        if not token == Keywords.PROGRAM.value:
            raise Keywords.PROGRAM.wrong_token_err(token)

        self._get_ident()

        self._corpo()

        token = self._next_token()
        validate_symbol(token, '.')

    def _corpo(self):
        self._dc()

        token = self._next_token()
        if not token == Keywords.BEGIN.value:
            raise Keywords.BEGIN.wrong_token_err(token)

        self._comandos()

        token = self._next_token()
        if not token == Keywords.END.value:
            raise Keywords.END.wrong_token_err(token)

    def _dc(self):
        token = self._next_token(dont_move=True)
        if token == Keywords.REAL.value or token == Keywords.INTEGER.value:
            self._dc_v()
            self._mais_dc()

    def _mais_dc(self):
        pos = self.tape.pos
        token = self._next_token()
        if token == Token.identificador(';'):
            self._mais_dc()
        else:
            self.tape.pos = pos

    def _dc_v(self):
        self._tipo_var()

        token = self._next_token()
        if token != Token.simbolo(':'):
            raise CompilerSyntaxError.simples(repr(':'), repr(token.valor))

        self._variaveis()

    def _tipo_var(self):
        token = self._next_token()
        if not (token == Keywords.REAL or token == Keywords.INTEGER):
            raise CompilerSyntaxError.simples(
                f'{Keywords.REAL.valor!r} ou {Keywords.INTEGER.valor!r}',
                repr(token.valor))

    def _variaveis(self):
        self._get_ident()
        self._mais_var()

    def _mais_var(self):
        pos = self.tape.pos
        token = self._next_token()

        if token == Token.simbolo(','):
            self._variaveis()
        else:
            self.tape.pos = pos

    def _comandos(self):
        self._comandos()
        self._mais_comandos()

    def _mais_comandos(self):
        pos = self.tape.pos
        token = self._next_token()

        if token == Token.simbolo(';'):
            self._comandos()
        else:
            self.tape.pos = pos

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
