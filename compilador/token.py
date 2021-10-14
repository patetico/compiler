from enum import auto, Enum


class TokenType(Enum):
    IDENTIFICADOR = auto()
    INTEIRO = auto()
    REAL = auto()
    SIMBOLO = auto()
    WHITESPACE = auto()
    COMMENT = auto()


class Token:
    def __init__(self, tipo: TokenType, valor: str):
        self.tipo = tipo
        self.valor = valor

    def __str__(self):
        return repr(self.valor)

    def __repr__(self):
        return f"Token<{self.tipo.name}, {self.valor!r}>"

    def __eq__(self, other):
        if isinstance(other, Enum):
            other = other.value

        if isinstance(other, Token):
            return self.tipo == other.tipo and self.valor == other.valor
        elif (isinstance(other, tuple) or isinstance(other, list)) and len(other) == 2:
            tipo, valor = other
            return self.tipo == tipo and self.valor == valor

        return False

    @property
    def is_number(self):
        return self.tipo in {TokenType.INTEIRO, TokenType.REAL}

    @classmethod
    def identificador(cls, valor):
        return cls(TokenType.IDENTIFICADOR, valor)

    @classmethod
    def inteiro(cls, valor):
        return cls(TokenType.INTEIRO, valor)

    @classmethod
    def real(cls, valor):
        return cls(TokenType.REAL, valor)

    @classmethod
    def simbolo(cls, valor):
        return cls(TokenType.SIMBOLO, valor)

    @classmethod
    def whitespace(cls, valor):
        return cls(TokenType.WHITESPACE, valor)

    @classmethod
    def comentario(cls, valor):
        return cls(TokenType.COMMENT, valor)
