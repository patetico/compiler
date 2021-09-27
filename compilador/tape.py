class Tape:
    def __init__(self, filepath: str):
        with open(filepath, 'rt') as f:
            self.code = f.read()
        self.pos = 0

    def next(self):
        self.pos += 1

    def back(self):
        self.pos -= 1

    def context(self, freeze=True):
        return TapeContext(self, freeze)

    def get_char(self, pos=0):
        pos += self.pos
        if self.is_eof():
            raise EOFError()
        return self.code[pos]

    def next_char(self):
        self.next()
        return self.get_char()

    def is_letra(self, pos=0):
        if self.is_eof(pos):
            return False
        c = self.get_char(pos)
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z')

    def is_num(self, pos=0):
        if self.is_eof(pos):
            return False
        c = self.get_char(pos)
        return '0' <= c <= '9'

    def is_whitespace(self, pos=0):
        if self.is_eof(pos):
            return False
        c = self.get_char(pos)
        return c in ' \r\n\t'

    def is_eof(self, pos=0):
        pos += self.pos
        return pos >= len(self.code) or pos < 0


class TapeContext:
    def __init__(self, tape: Tape, freeze=True):
        self.tape = tape
        self._saved_pos = None
        self._freeze = freeze

    def __enter__(self):
        self.save_pos()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._freeze:
            self.tape.pos = self._saved_pos

    def save_pos(self):
        self._saved_pos = self.tape.pos

    def freeze(self):
        self.save_pos()
        self._freeze = True

    def unfreeze(self):
        self._freeze = False
