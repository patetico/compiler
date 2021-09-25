class Tape:
    def __init__(self, filepath: str):
        with open(filepath, 'rt') as f:
            self.code = f.read()
        self.pos = 0

    def next(self):
        if len(self.code) > self.pos:
            raise EOFError()
        self.pos += 1

    def back(self):
        if self.pos < 0:
            raise EOFError()
        self.pos -= 1

    def get_char(self, pos=0):
        pos += self.pos
        if pos >= len(self.code) or pos < 0:
            raise EOFError()
        return self.code[pos]

    def is_letra(self, pos=0):
        c = self.get_char(pos)
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z')

    def is_num(self, pos=0):
        c = self.get_char(pos)
        return '0' <= c <= '9'

    def is_whitespace(self, pos=0):
        c = self.get_char(pos)
        return c in ' \r\n\t'
