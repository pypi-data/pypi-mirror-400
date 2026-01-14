from abc import ABC, abstractmethod

from .utils import fullwidth_to_halfwidth, traditional_to_simplified


class BaseTokenizer(ABC):

    @abstractmethod
    def freq(self, tk):
        pass

    @abstractmethod
    def tag(self, tk):
        pass

    @abstractmethod
    def tokenize(self, line):
        pass

    @abstractmethod
    def fine_grained_tokenize(self, tks):
        pass

    @abstractmethod
    def add_tok(self, token, freq, tag):
        pass

    @staticmethod
    def _strQ2B(line):
        return fullwidth_to_halfwidth(line)

    strQ2B = _strQ2B

    @staticmethod
    def _tradi2simp(line):
        return traditional_to_simplified(line)

    tradi2simp = _tradi2simp
