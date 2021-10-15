class Interpreter:
    def __init__(self, code, input_caret=''):
        self.code = code
        self.data_stack = []
        self.i = 0
        self.input_caret = input_caret

    def run(self):
        while self.i < len(self.code):
            op, arg = self.code[self.i].split(' ', maxsplit=2)
            fn = getattr(self, f'_op_{op.lower()}')
            if arg:
                fn(arg)
            else:
                fn()
            self.i += 1

    def __basic_op(self, op):
        d1 = self.data_stack.pop()
        d2 = self.data_stack[-1]
        self.data_stack[-1] = op(d1, d2)

    def _op_crvl(self, n):
        self.data_stack.append(self.data_stack[int(n)])

    def _op_crct(self, k):
        self.data_stack.append(float(k))

    def _op_soma(self):
        d = self.data_stack.pop()
        self.data_stack[-1] += d

    def _op_subt(self):
        d = self.data_stack.pop()
        self.data_stack[-1] -= d

    def _op_mult(self):
        d = self.data_stack.pop()
        self.data_stack[-1] *= d

    def _op_divi(self):
        d = self.data_stack.pop()
        self.data_stack[-1] /= d

    def _op_inve(self):
        self.data_stack[-1] *= -1

    def _op_conj(self):
        self.__basic_op(lambda d1, d2: 1 if d1 or d2 else 0)

    def _op_disj(self):
        self.__basic_op(lambda d1, d2: 1 if d1 and d2 else 0)

    def _op_nega(self):
        self.data_stack[-1] = 0 if self.data_stack[-1] else 1

    def _op_cpme(self):
        self.__basic_op(lambda d1, d2: 1 if d1 < d2 else 0)

    def _op_cpma(self):
        self.__basic_op(lambda d1, d2: 1 if d1 > d2 else 0)

    def _op_cpig(self):
        self.__basic_op(lambda d1, d2: 1 if d1 == d2 else 0)

    def _op_cdes(self):
        self.__basic_op(lambda d1, d2: 1 if d1 != d2 else 0)

    def _op_cpmi(self):
        self.__basic_op(lambda d1, d2: 1 if d1 <= d2 else 0)

    def _op_cmai(self):
        self.__basic_op(lambda d1, d2: 1 if d1 >= d2 else 0)

    def _op_armz(self, n):
        self.data_stack[int(n)] = self.data_stack.pop()

    def _op_dsvi(self, p):
        self.i = int(p) - 1

    def _op_dsvf(self, p):
        if self.data_stack.pop() == 0:
            self.i = int(p) - 1

    def _op_leit(self):
        self.data_stack.append(float(input(self.input_caret)))

    def _op_impr(self):
        print(self.data_stack.pop())

    def _op_alme(self, n):
        for _ in range(int(n)):
            self.data_stack.append(0)

    def _op_inpp(self):
        pass

    def _op_para(self):
        pass
