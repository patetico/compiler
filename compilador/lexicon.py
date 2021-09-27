import logging
from enum import Enum

from . import codegen
from .errors import CompilerSyntaxError
from .symbols_table import SymbolsTable
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
        self.symbols = SymbolsTable()
        self.code = []

    def parse(self):
        self._programa()
        try:
            token = self._next_token()
        except EOFError:
            pass
        else:
            raise CompilerSyntaxError.simples('EOF', repr(token.valor))

    def _next_token(self, skip_whitespace=True):
        while True:
            token = self.tokenizer.next_token()
            if not skip_whitespace or token.tipo != TokenType.WHITESPACE:
                _logger.debug(token)
                return token

    def _get_ident(self) -> Token:
        token = self._next_token()
        validate_ident(token)
        return token

    def _programa(self):
        """
        Implementa <programa>

        <programa>  ->  program ident <corpo> .
        """
        _logger.debug('<programa>')
        token = self._next_token()
        if not token == Keywords.PROGRAM.value:
            raise Keywords.PROGRAM.wrong_token_err(token)

        self._get_ident()

        self._corpo()

        token = self._next_token()
        validate_symbol(token, '.')

    def _corpo(self):
        """
        Implementa <corpo>

        <corpo>  ->  <dc> begin <comandos> end
        """
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
        """
        Implementa <dc>

        <dc>  ->  <dc_v> <mais_dc> | λ
        """
        _logger.debug('<dc>')
        with self.tape.context():
            token = self._next_token()
        if token == Keywords.REAL or token == Keywords.INTEGER:
            self._dc_v()
            self._mais_dc()

    def _mais_dc(self):
        """
        Implementa <mais_dc>

        <mais_dc>  ->  ; <dc> | λ
        """
        _logger.debug('<mais_dc>')

        with self.tape.context() as tape_state:
            token = self._next_token()
            if token == Token.simbolo(';'):
                tape_state.unfreeze()
                self._dc()

    def _dc_v(self):
        """
        Implementa <dc_v>

        <dc_v>  ->  <tipo_var> : <variaveis>
        """
        _logger.debug('<dc_v>')
        tipo = self._tipo_var()

        token = self._next_token()
        if token != Token.simbolo(':'):
            raise CompilerSyntaxError.simples(repr(':'), repr(token.valor))

        self._variaveis(tipo)

    def _tipo_var(self) -> TokenType:
        """
        Implementa <tipo_var>

        <tipo_var>  ->  real | integer
        """
        _logger.debug('<tipo_var>')
        token = self._next_token()
        if token == Keywords.REAL:
            return TokenType.REAL
        elif token == Keywords.INTEGER:
            return TokenType.INTEIRO
        else:
            raise CompilerSyntaxError.simples(
                f'{Keywords.REAL.valor!r} ou {Keywords.INTEGER.valor!r}',
                repr(token.valor))

    def _variaveis(self, tipo: TokenType):
        """
        Implementa <variaveis>

        <variaveis>  ->  ident <mais_var>
        """
        _logger.debug('<variaveis>')

        id_ = self._get_ident()
        self.symbols.add(id_, tipo)
        code = codegen.alme('0.0' if tipo == TokenType.REAL else '0', id_.valor)
        self.code.append(code)

        self._mais_var(tipo)

    def _mais_var(self, tipo: TokenType):
        """
        Implementa <mais_var>

        <mais_var>  ->  , <variaveis> | λ
        """
        _logger.debug('<mais_var>')

        with self.tape.context() as tape_state:
            token = self._next_token()
            if token == Token.simbolo(','):
                tape_state.unfreeze()
                self._variaveis(tipo)

    def _comandos(self):
        """
        Implementa <comandos>

        <comandos>  ->  <comando> <mais_comandos>
        """
        _logger.debug('<comandos>')
        self._comando()
        self._mais_comandos()

    def _mais_comandos(self):
        """
        Implementa <mais_comandos>

        <mais_comandos>  ->  ; <comandos> | λ
        """
        _logger.debug('<mais_comandos>')

        with self.tape.context() as tape_state:
            token = self._next_token()

            if token == Token.simbolo(';'):
                tape_state.unfreeze()
                self._comandos()

    def _comando(self):
        """
        Implementa <comando>

        <comando>  ->  read (ident)
                   |   write (ident)
                   |   ident := <expressao>
                   |   if <condicao> then <comandos> <pfalsa> $

        """
        _logger.debug('<comando>')
        token = self._next_token()
        if token == Keywords.READ or token == Keywords.WRITE:
            fn = codegen.read if token == Keywords.READ else codegen.write

            token = self._next_token()
            validate_symbol(token, '(')

            id_ = self._get_ident()

            token = self._next_token()
            validate_symbol(token, ')')

            code = fn(id_.valor)
            self.code.append(code)
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
        """
        Implementa <condicao>

        <condicao>  ->  <expressao> <relacao> <expressao>
        """
        _logger.debug('<condicao>')
        self._expressao()
        self._relacao()
        self._expressao()

    def _relacao(self):
        """
        Implementa <relacao>

        <relacao>  ->  = | <> | >= | <= | > | <
        """
        _logger.debug('<relacao>')
        token = self._next_token()
        comps = {'=', '<>', '>=', '<=', '>', '<'}
        if token.tipo != TokenType.SIMBOLO or token.valor not in comps:
            raise CompilerSyntaxError.simples(
                ' ou '.join(map(repr, comps)),
                repr(token.valor))

    def _expressao(self):
        """
        Implementa <expressao>

        <expressao>  ->  <termo> <outros_termos>
        """
        _logger.debug('<expressao>')

        self._termo()
        self._outros_termos()

    def _termo(self):
        """
        Implementa <termo>

        <termo>  ->  <op_un> <fator> <mais_fatores>
        """
        _logger.debug('<termo>')
        self._op_un()
        self._fator()
        self._mais_fatores()

    def _op_un(self):
        """
        Implementa <op_un>

        <op_un>  ->  - | λ
        """
        _logger.debug('<op_un>')

        with self.tape.context() as tape_state:
            token = self._next_token()
            if token == Token.simbolo('-'):
                tape_state.unfreeze()

    def _fator(self):
        """
        Implementa <fator>

        <fator>  ->  ident
                 |   numero_int
                 |   numero_real
                 |   (<expressao>)
        """
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
        """
        Implementa <outros_termos>

        <outros_termos>  ->  <op_ad> <termo> <outros_termos> | λ
        """
        _logger.debug('<outros_termos>')

        res = []

        while True:
            with self.tape.context():
                token = self._next_token()

            if token != Token.simbolo('+') and token != Token.simbolo('-'):
                return res

            op = self._op_ad()
            termo = self._termo()
            res.append((op, termo))

    def _op_ad(self):
        """
        Implementa <op_ad>

        <op_ad>  ->  + | -
        """
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
        """
        Implementa <mais_fatores>

        <mais_fatores>  ->  <op_mul> <fator> <mais_fatores>
        """
        _logger.debug('<mais_fatores>')

        res = []

        while True:
            with self.tape.context():
                token = self._next_token()

            if token != Token.simbolo('*') and token != Token.simbolo('/'):
                return res

            op = self._op_mul()
            fator = self._fator()
            res.append((op, fator))

    def _op_mul(self) -> str:
        """
        Implementa <op_mul>

        <op_mul>  ->  * | /
        """
        _logger.debug('<op_mul>')

        token = self._next_token()
        if token == Token.simbolo('*'):
            return '*'
        elif token == Token.simbolo('/'):
            return '/'
        else:
            raise CompilerSyntaxError.simples(
                f'{"*"!r} ou {"/"!r}',
                repr(token.valor))

    def _pfalsa(self):
        """
        Implementa <pfalsa>

        <pfalsa>  ->  else <comandos> | λ
        """
        _logger.debug('<pfalsa>')

        with self.tape.context() as tape_state:
            token = self._next_token()
            if token == Keywords.ELSE:
                tape_state.unfreeze()
                self._comandos()
