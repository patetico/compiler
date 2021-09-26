import logging
from enum import Enum

from .errors import CompilerSyntaxError
from .tape import Tape
from .token import Token, TokenType
from .tokenizer import Tokenizer


_logger = logging.getLogger(__name__)


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
                _logger.debug(token)
                return token

    def _get_ident(self) -> Token:
        token = self._next_token()
        validate_ident(token)
        return token

    def _programa(self):
        _logger.debug('<programa>')
        token = self._next_token()
        if not token == Keywords.PROGRAM.value:
            raise Keywords.PROGRAM.wrong_token_err(token)

        self._get_ident()

        self._corpo()

        token = self._next_token()
        validate_symbol(token, '.')

    def _corpo(self):
        _logger.debug('<corpo>')
        self._dc()

        token = self._next_token()
        if not token == Keywords.BEGIN:
            raise Keywords.BEGIN.wrong_token_err(token)

        self._comandos()

        token = self._next_token()
        if not token == Keywords.END:
            raise Keywords.END.wrong_token_err(token)

    def _dc(self):
        _logger.debug('<dc>')
        token = self._next_token(dont_move=True)
        if token == Keywords.REAL or token == Keywords.INTEGER:
            self._dc_v()
            self._mais_dc()

    def _mais_dc(self):
        _logger.debug('<mais_dc>')
        pos = self.tape.pos
        token = self._next_token()
        if token == Token.simbolo(';'):
            self._dc()
        else:
            self.tape.pos = pos

    def _dc_v(self):
        _logger.debug('<dc_v>')
        self._tipo_var()

        token = self._next_token()
        if token != Token.simbolo(':'):
            raise CompilerSyntaxError.simples(repr(':'), repr(token.valor))

        self._variaveis()

    def _tipo_var(self):
        _logger.debug('<tipo_var>')
        token = self._next_token()
        if not (token == Keywords.REAL or token == Keywords.INTEGER):
            raise CompilerSyntaxError.simples(
                f'{Keywords.REAL.valor!r} ou {Keywords.INTEGER.valor!r}',
                repr(token.valor))

    def _variaveis(self):
        _logger.debug('<variaveis>')
        self._get_ident()
        self._mais_var()

    def _mais_var(self):
        _logger.debug('<mais_var>')
        pos = self.tape.pos
        token = self._next_token()

        if token == Token.simbolo(','):
            self._variaveis()
        else:
            self.tape.pos = pos

    def _comandos(self):
        _logger.debug('<comandos>')
        self._comando()
        self._mais_comandos()

    def _mais_comandos(self):
        _logger.debug('<mais_comandos>')
        pos = self.tape.pos
        token = self._next_token()

        if token == Token.simbolo(';'):
            self._comandos()
        else:
            self.tape.pos = pos

    def _comando(self):
        _logger.debug('<comando>')
        token = self._next_token()
        if token == Keywords.READ or token == Keywords.WRITE:
            token = self._next_token()
            validate_symbol(token, '(')

            self._get_ident()

            token = self._next_token()
            validate_symbol(token, ')')
        elif token == Keywords.IF:
            self._condicao()

            token = self._next_token()
            if not token == Keywords.THEN:
                raise Keywords.THEN.wrong_token_err(token)

            self._comandos()
            self._pfalsa()

            token = self._next_token()
            validate_symbol(token, '$')
        else:
            validate_ident(token)

            token = self._next_token()
            validate_symbol(token, ':=')

            self._expressao()

    def _condicao(self):
        _logger.debug('<condicao>')
        self._expressao()
        self._relacao()
        self._expressao()

    def _relacao(self):
        _logger.debug('<relacao>')
        token = self._next_token()
        comps = {'=', '<>', '>=', '<=', '>', '<'}
        if token.tipo != TokenType.SIMBOLO or token.valor not in comps:
            raise CompilerSyntaxError.simples(
                ' ou '.join(map(repr, comps)),
                repr(token.valor))

    def _expressao(self):
        _logger.debug('<expressao>')
        self._termo()
        self._outros_termos()

    def _termo(self):
        _logger.debug('<termo>')
        self._op_un()
        self._fator()
        self._mais_fatores()

    def _op_un(self):
        _logger.debug('<op_un>')
        pos = self.tape.pos
        token = self._next_token()
        if token != Token.simbolo('-'):
            self.tape.pos = pos

    def _fator(self):
        _logger.debug('<fator>')
        token = self._next_token()

        if token.tipo == TokenType.IDENTIFICADOR:
            validate_ident(token)
        elif token.tipo == TokenType.INTEIRO:
            pass
        elif token.tipo == TokenType.REAL:
            pass
        elif token == Token.simbolo('('):
            self._expressao()

            token = self._next_token()
            validate_symbol(token, ')')
        else:
            raise CompilerSyntaxError(f'Valor inesperado: {token.valor!r}')

    def _outros_termos(self):
        _logger.debug('<outros_termos>')
        token = self._next_token(dont_move=True)
        if token == Token.simbolo('+') or token == Token.simbolo('-'):
            self._op_ad()
            self._termo()
            self._outros_termos()

    def _op_ad(self):
        _logger.debug('<op_ad>')
        token = self._next_token()
        if token == Token.simbolo('+'):
            pass
        elif token == Token.simbolo('-'):
            pass
        else:
            raise CompilerSyntaxError.simples(
                f'{"+"!r} ou {"-"!r}',
                repr(token.valor))

    def _mais_fatores(self):
        _logger.debug('<mais_fatores>')
        token = self._next_token(dont_move=True)
        if token == Token.simbolo('*') or token == Token.simbolo('/'):
            self._op_mul()
            self._fator()
            self._mais_fatores()

    def _op_mul(self):
        _logger.debug('<op_mul>')
        token = self._next_token()
        if token == Token.simbolo('*'):
            pass
        elif token == Token.simbolo('/'):
            pass
        else:
            raise CompilerSyntaxError.simples(
                f'{"*"!r} ou {"/"!r}',
                repr(token.valor))

    def _pfalsa(self):
        _logger.debug('<pfalsa>')
        pos = self.tape.pos
        token = self._next_token()
        if token == Keywords.ELSE:
            self._comandos()
        else:
            self.tape.pos = pos
