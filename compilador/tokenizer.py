import logging

from .errors import CompilerSyntaxError
from .tape import Tape
from .token import Token, TokenType


_logger = logging.getLogger(__name__)


class Tokenizer:
    def __init__(self, tape: Tape):
        self.tape = tape
        self.state = 0
        self._token_val = None

    def next_token(self) -> Token:
        if self.state != 0:
            raise CompilerSyntaxError(f"Estado inesperado do automato: {self.state}")
        return self._state0()

    def _state0(self):
        _logger.debug('state 0')

        if self.tape.is_eof():
            raise CompilerSyntaxError.simples('novo token', 'EOF')

        self._token_val = c = self.tape.get_char()
        if self.tape.is_num():
            return self._state1()
        if c == '.':
            return self._state2()
        elif self.tape.is_letra():
            return self._state4()
        elif c in set('=$()+-*/.;,'):
            return self._state5()
        elif c in set('>:'):
            return self._state6()
        elif c == '<':
            return self._state7()
        elif c in set(' \t\r\n'):
            return self._state8()

        raise CompilerSyntaxError(f"Caractere ilegal: {c!r}")

    def _state1(self):
        _logger.debug('state 1')

        while self.tape.is_num(1):
            self._token_val += self.tape.next_char()

        if not self.tape.is_eof(1) and self.tape.get_char(1) == '.':
            self._token_val += self.tape.next_char()
            return self._state2()

        token = Token(TokenType.INTEIRO, self._token_val)
        return self._end_state(token)

    def _state2(self):
        _logger.debug('state 2')

        c = self.tape.next_char()
        if not self.tape.is_num():
            raise CompilerSyntaxError.simples('dígito', c)
        return self._state3()

    def _state3(self):
        _logger.debug('state 3')

        while self.tape.is_num(1):
            self._token_val += self.tape.next_char()

        token = Token(TokenType.REAL, self._token_val)
        return self._end_state(token)

    def _state4(self):
        _logger.debug('state 4')

        while self.tape.is_num(1) or self.tape.is_letra(1):
            self._token_val += self.tape.next_char()

        token = Token(TokenType.IDENTIFICADOR, self._token_val)
        return self._end_state(token)

    def _state5(self):
        _logger.debug('state 5')

        token = Token(TokenType.SIMBOLO, self._token_val)
        return token

    def _state6(self):
        _logger.debug('state 6')

        if self.tape.get_char(1) == '=':
            self._token_val += self.tape.next_char()

        return self._state5()

    def _state7(self):
        _logger.debug('state 7')

        if self.tape.get_char(1) in '=>':
            self._token_val += self.tape.next_char()

        return self._state5()

    def _state8(self):
        _logger.debug('state 8')

        while not self.tape.is_eof(1):
            self._token_val += self.tape.next_char()

        token = Token(TokenType.WHITESPACE, self._token_val)
        return self._end_state(token)

    def _end_state(self, token: Token):
        _logger.debug(token)
        self.state = 0
        self._token_val = None
        self.tape.next()
        return token
