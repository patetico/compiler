from abc import ABC, abstractmethod

from ..token import Token


class CodeGenerator(ABC):
    def __init__(self):
        self.code = []

    @abstractmethod
    def alme(self, arg1, res):
        pass

    @abstractmethod
    def read(self, res):
        pass

    @abstractmethod
    def write(self, arg1):
        pass

    @abstractmethod
    def goto(self, arg1):
        pass

    @abstractmethod
    def jf(self, arg1, arg2):
        pass

    @abstractmethod
    def uminus(self, arg1, res):
        pass

    @abstractmethod
    def para(self):
        pass

    @abstractmethod
    def if_(self, cond: Token):
        pass

    @abstractmethod
    def else_(self):
        pass

    @abstractmethod
    def close_if(self):
        pass

    @abstractmethod
    def while_(self, cond: Token):
        pass

    @abstractmethod
    def close_while(self):
        pass
