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


def has_token(tests: iter, token: Token, raise_err=False):
    """
    Iterate through tests looking for a token match and optionally raises an exception.

    :param tests:       iterable with strings or objects that can be compared to token
    :param token:       token to be compared. if tests are strings, token.valor is compared instead
    :param raise_err:   raises a CompilerSyntaxError if token is not found in tests
    :return:            True if token is found, False otherwise
    """
    for t in tests:
        if (isinstance(t, str) and token.valor == t) or token == t:
            return True

    if raise_err:
        raise CompilerSyntaxError.simples(' ou '.join(map(repr, tests)), token)

    return False
