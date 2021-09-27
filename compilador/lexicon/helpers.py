from .keywords import Keywords
from ..errors import CompilerSyntaxError
from ..token import Token, TokenType


def validate_ident(token: Token):
    if not token.tipo == TokenType.IDENTIFICADOR:
        raise CompilerSyntaxError.simples('identificador', token)

    if any(token == kw.value for kw in Keywords):
        raise CompilerSyntaxError(
            f'Palavra reservada não pode ser usada como identificador: {token}')


def validate_symbol(token: Token, symbol: str):
    if not token == Token.simbolo(symbol):
        raise CompilerSyntaxError.simples(repr(symbol), token)
