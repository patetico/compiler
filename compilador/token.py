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
        return f"Token<{self.tipo}, {self.valor}>"
