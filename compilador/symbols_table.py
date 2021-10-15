from .errors import CompilerSemanticError
from .token import Token, TokenType


def normalize_name(name):
    if isinstance(name, Token):
        name = name.valor
    elif isinstance(name, Symbol):
        name = name.name

    if not isinstance(name, str):
        raise CompilerSemanticError(f'Nome inválido de símbolo: {name!r}')

    return name


class Symbol:
    def __init__(self, name, type_: TokenType, data=None):
        self.name = normalize_name(name)
        self.type = type_
        self.data = data  # extra data

    def __str__(self):
        return repr(self.name)

    def __repr__(self):
        return f'Symbol<{self.type}, {self.name}>'

    def same_type(self, other):
        if not isinstance(other, Symbol):
            return self.type == other
        return self.type == other.type


class SymbolsTable:
    def __init__(self):
        self.symbols = dict()
        self._tmp_id = 1

    def get(self, name) -> Symbol:
        name = normalize_name(name)
        return self.symbols[name]

    def has(self, name):
        return normalize_name(name) in self.symbols

    def add(self, name: Token, type_: TokenType):
        if name.tipo != TokenType.IDENTIFICADOR:
            raise CompilerSemanticError(
                f'Tentativa de criar variável com identicador inválido {name!r}')

        if type_ not in (TokenType.REAL, TokenType.INTEIRO):
            raise CompilerSemanticError(
                f'Tentativa de criar variável {name.valor!r} com tipo inválido {type_}')

        name = normalize_name(name)
        if self.has(name):
            raise CompilerSemanticError(f'Redeclaração de variável {name!r}')

        symbol = Symbol(name, type_)
        self.symbols[name] = symbol
        return symbol

    def make_temp(self, type_: TokenType) -> Token:
        while self.has(f't{self._tmp_id}'):
            self._tmp_id += 1

        tmp = Token.identificador(f't{self._tmp_id}')
        self.add(tmp, type_)
        return tmp

    def typeof(self, name):
        return self.get(name).type

    def same_types(self, var1, var2):
        return self.typeof(var1) == self.typeof(var2)
