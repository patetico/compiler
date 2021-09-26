from enum import auto, Enum


class TokenType(Enum):
    IDENTIFICADOR = auto()
    INTEIRO = auto()
    REAL = auto()
    SIMBOLO = auto()
    WHITESPACE = auto()


class Token:
    def __init__(self, tipo: TokenType, valor: str):
        self.tipo = tipo
        self.valor = valor

    def __str__(self):
        return f"Token<{self.tipo}, {self.valor!r}>"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.tipo == other.tipo and self.valor == other.valor
        elif (isinstance(other, tuple) or isinstance(other, list)) and len(other) == 2:
            tipo, valor = other
            return self.tipo == tipo and self.valor == valor

        return False
