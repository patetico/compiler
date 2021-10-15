import logging

from .helpers import has_token, validate_ident, validate_symbol
from .keywords import Keywords
from ..codegen._base import CodeGenerator
from ..errors import CompilerSemanticError, CompilerSyntaxError
from ..symbols_table import SymbolsTable
from ..tape import Tape
from ..token import Token, TokenType
from ..tokenizer import Tokenizer


_logger = logging.getLogger(__name__)


class Lexicon:
    def __init__(self, filepath: str, compiler: CodeGenerator):
        self.tape = Tape(filepath)
        self.tokenizer = Tokenizer(self.tape)
        self.symbols = SymbolsTable()
        self.compiler = compiler

    def parse(self) -> [str]:
        self._programa()
        try:
            token = self._next_token()
        except EOFError:
            pass
        else:
            raise CompilerSyntaxError.simples('EOF', token)

        return self.compiler.code

    def validate_var(self, var):
        if not self.symbols.has(var):
            raise CompilerSemanticError(f'Variável {var!r} não foi declarada.')

    def validate_same_type_op(self, arg1, arg2, op):
        if not self.same_types(arg1, arg2):
            msg = (
                'Operação não é permitida entre tipos diferentes '
                f'(<{self.typeof(arg1).name}> e <{self.typeof(arg2).name}>):\n'
                f'\t{arg1!r} {op} {arg2!r}\n')
            raise CompilerSemanticError(msg)

    def _next_token(self, skip_whitespace=True):
        while True:
            token = self.tokenizer.next_token()
            if token.tipo == TokenType.COMMENT:
                continue
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
        self.compiler.para()

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
        validate_symbol(token, ':')

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
                f'{Keywords.REAL.value} ou {Keywords.INTEGER.value}',
                token)

    def _variaveis(self, tipo: TokenType):
        """
        Implementa <variaveis>

        <variaveis>  ->  ident <mais_var>
        """
        _logger.debug('<variaveis>')

        id_ = self._get_ident()
        self.symbols.add(id_, tipo)
        self.compiler.alme('0.0' if tipo == TokenType.REAL else '0', id_.valor)

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
                   |   while <condicao> do <comandos> $
        """
        _logger.debug('<comando>')

        token = self._next_token()
        if token == Keywords.READ or token == Keywords.WRITE:
            fn = token

            token = self._next_token()
            validate_symbol(token, '(')

            id_ = self._get_ident()

            token = self._next_token()
            validate_symbol(token, ')')

            if fn == Keywords.READ:
                self.compiler.read(id_.valor)
            else:
                self.compiler.write(id_.valor)
        elif token == Keywords.IF:
            cond = self._condicao()

            token = self._next_token()
            if not token == Keywords.THEN:
                raise Keywords.THEN.wrong_token_err(token)

            self.compiler.if_(cond)
            self._comandos()
            self._pfalsa()
            self.compiler.close_if()

            token = self._next_token()
            validate_symbol(token, '$')
        elif token == Keywords.WHILE:
            cond = self._condicao()

            token = self._next_token()
            if not token == Keywords.DO:
                raise Keywords.DO.wrong_token_err(token)

            self.compiler.while_(cond)
            self._comandos()
            self.compiler.close_while()

            token = self._next_token()
            validate_symbol(token, '$')
        else:
            validate_ident(token)
            ident = token

            token = self._next_token()
            op = ':='
            validate_symbol(token, op)

            termo = self._expressao()
            self.validate_same_type_op(ident, termo, op)
            self.compiler.op(op, termo, res=ident)

    def _condicao(self) -> Token:
        """
        Implementa <condicao>

        <condicao>  ->  <expressao> <relacao> <expressao>
        """
        _logger.debug('<condicao>')
        arg1 = self._expressao()
        op = self._relacao()
        arg2 = self._expressao()

        self.validate_same_type_op(arg1, arg2, op)
        tmp = self.symbols.make_temp(self.typeof(arg1))
        self.compiler.op(op, arg1, arg2, tmp)
        return tmp

    def _relacao(self) -> str:
        """
        Implementa <relacao>

        <relacao>  ->  = | <> | >= | <= | > | <
        """
        _logger.debug('<relacao>')

        token = self._next_token()
        comps = {'=', '<>', '>=', '<=', '>', '<'}
        has_token(comps, token, True)
        return token.valor

    def _expressao(self) -> Token:
        """
        Implementa <expressao>

        <expressao>  ->  <termo> <outros_termos>
        """
        _logger.debug('<expressao>')

        termo = self._termo()
        return self._outros_termos(termo)

    def _termo(self) -> Token:
        """
        Implementa <termo>

        <termo>  ->  <op_un> <fator> <mais_fatores>
        """
        _logger.debug('<termo>')

        signal = self._op_un()
        fator = self._fator()

        if signal == '-':
            type_ = self.symbols.typeof(fator)
            t = self.symbols.make_temp(type_)
            self.compiler.uminus(fator.valor, t.valor)
            fator = t

        return self._mais_fatores(fator)

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
                return '-'
        return None

    def _fator(self) -> Token:
        """
        Implementa <fator>

        <fator>  ->  ident
                 |   numero_int
                 |   numero_real
                 |   (<expressao>)
        """
        _logger.debug('<fator>')

        res = token = self._next_token()

        if token.tipo == TokenType.IDENTIFICADOR:
            validate_ident(token)
            self.validate_var(token)
        elif token == Token.simbolo('('):
            res = self._expressao()

            token = self._next_token()
            validate_symbol(token, ')')
        elif not token.is_number:
            raise CompilerSyntaxError.invalid_token(token)

        return res

    def _outros_termos(self, termo: Token) -> Token:
        """
        Implementa <outros_termos>

        <outros_termos>  ->  <op_ad> <termo> <outros_termos> | λ
        """
        _logger.debug('<outros_termos>')

        return self.__do_add_or_mult('+-', termo, self._op_ad, self._termo)

    def _op_ad(self) -> str:
        """
        Implementa <op_ad>

        <op_ad>  ->  + | -
        """
        _logger.debug('<op_ad>')

        token = self._next_token()
        has_token('+-', token, True)
        return token.valor

    def _mais_fatores(self, fator: Token) -> Token:
        """
        Implementa <mais_fatores>

        <mais_fatores>  ->  <op_mul> <fator> <mais_fatores>
        """
        _logger.debug('<mais_fatores>')

        return self.__do_add_or_mult('*/', fator, self._op_mul, self._fator)

    def _op_mul(self) -> str:
        """
        Implementa <op_mul>

        <op_mul>  ->  * | /
        """
        _logger.debug('<op_mul>')

        token = self._next_token()
        has_token('*/', token, True)
        return token.valor

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
                self.compiler.else_()
                self._comandos()

    def same_types(self, var1, var2):
        return self.typeof(var1) == self.typeof(var2)

    def typeof(self, var):
        if isinstance(var, Token) and var.is_number:
            return var.tipo

        self.validate_var(var)
        return self.symbols.typeof(var)

    def __do_add_or_mult(
            self,
            symbols: iter,
            token: Token,
            fn_op,
            fn_dir
    ) -> Token:
        if token.tipo == TokenType.IDENTIFICADOR:
            if not self.symbols.has(token):
                raise CompilerSemanticError(f'Identificador desconhecido: {token}')
            type_ = self.symbols.typeof(token)
        elif token.is_number:
            type_ = token.tipo
        else:
            raise CompilerSemanticError.invalid_token(token)

        esq = token

        while True:
            with self.tape.context():
                next_token = self._next_token()

            if not has_token(symbols, next_token):
                return esq

            op = fn_op()
            dir_ = fn_dir()

            self.validate_same_type_op(esq, dir_, op)

            t = self.symbols.make_temp(type_)
            self.compiler.op(op, esq, dir_, t)
            esq = t
