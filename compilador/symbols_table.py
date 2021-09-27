from compilador.errors import CompilerSemanticError
from compilador.token import Token, TokenType


class SymbolsTable:
    def __init__(self):
        self.symbols = dict()

    def has(self, name: str):
        return name in self.symbols

    def add(self, name: Token, type_: TokenType):
        if name.tipo != TokenType.IDENTIFICADOR:
            raise CompilerSemanticError(
                f'Tentativa de criar variável com identicador inválido {name!r}')

        if self.has(name.valor):
            raise CompilerSemanticError(
                f'Redeclaração de variável {name!r}')

        if type_ not in (TokenType.REAL, TokenType.INTEIRO):
            raise CompilerSemanticError(
                f'Tentativa de criar variável {name.valor!r} com tipo inválido {type_}')

        self.symbols[name.valor] = type_
