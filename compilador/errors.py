from compilador.token import Token


def _invalid_token(token: Token):
    return f'Token inválido: {token!r}'


class CompilerError(Exception):
    def __init__(self, error_type, msg):
        # TODO: implement trace
        c = '#'
        size = 50
        header_msg = f'ERRO {error_type}'.upper().center(size - 4)
        header_border = c * (len(header_msg) + 4)
        msg = '\n'.join(
            [
                '',
                header_border,
                f'{c} {header_msg} {c}',
                header_border,
                f'  > {msg}'
            ])
        super().__init__(msg)


class CompilerSyntaxError(CompilerError):
    def __init__(self, msg):
        super().__init__('SINTÁTICO', msg)

    @classmethod
    def simples(cls, expected, found):
        return cls(f'Esperado {expected}, encontrado {found}')

    @classmethod
    def invalid_token(cls, token: Token):
        return cls(_invalid_token(token))


class CompilerSemanticError(CompilerError):
    def __init__(self, msg):
        super().__init__('SEMÂNTICO', msg)

    @classmethod
    def invalid_token(cls, token: Token):
        return cls(_invalid_token(token))
