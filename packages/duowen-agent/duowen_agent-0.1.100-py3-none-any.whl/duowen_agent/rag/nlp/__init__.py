from typing import List, Literal

from .base_tokenizer import BaseTokenizer
from .query import FulltextQueryer
from .synonym import Synonym
from .term_weight import TermWeight


class LexSynth:

    def __init__(
        self,
        tokenizer: BaseTokenizer = None,
        tw: TermWeight = None,
        syn: Synonym = None,
        tok_mode: Literal["ragflow", "jieba"] = "jieba",
    ):

        if tokenizer:
            self.tokenizer = tokenizer
        else:
            if tok_mode == "jieba":
                from .jieba_tokenizer import JiebaTokenizer

                self.tokenizer = JiebaTokenizer()
            elif tok_mode == "ragflow":
                from .rag_tokenizer import RagTokenizer

                self.tokenizer = RagTokenizer()
            else:
                raise ValueError(f"Unknown tokenizer mode: {tok_mode}")

        self.tw = tw if tw else TermWeight(self.tokenizer)
        self.syn = syn if syn else Synonym()
        self.query = FulltextQueryer(
            tokenizer=self.tokenizer, term_weight=self.tw, synonym=self.syn
        )

    def tok_add_word(self, word, frequency: int, pos: str):
        self.tokenizer.add_tok(token=word, freq=frequency, tag=pos)

    def ner_set_word(self, word: str, term_type: str) -> None:
        self.tw.add_ner(word, term_type)

    def syn_set_word(self, word: str, alias: str) -> None:
        self.syn.add_syn(word, alias)

    def add_stop_word(self, word: str):
        self.tw.add_stop_word(word)

    def add_term_freq(self, word: str, freq: int):
        """获取真实语料的词频率"""
        self.tw.add_term_freq(word, freq)

    def trunc_ner_word(self) -> None:
        """清空NER词汇表"""
        self.tw.ne.clear()

    def trunc_syn_word(self) -> None:
        """清空同义词词汇表"""
        self.syn.dictionary.clear()

    def trunc_stop_word(self) -> None:
        """清空停用词词汇表"""
        self.tw.stop_words.clear()

    def trunc_term_freq(self) -> None:
        """清空词频统计表"""
        self.tw.df.clear()

    def tok_tag_word(self, word: str):
        return self.tokenizer.tag(word)

    def content_cut(self, text: str):
        return self.tokenizer.tokenize(text)

    def content_sm_cut(self, text: str):
        return self.tokenizer.fine_grained_tokenize(self.tokenizer.tokenize(text))

    def term_weight(self, text: str):
        match, keywords = self.query.question(text)
        if match:
            return match.matching_text
        else:
            return None

    def text_similarity(
        self, question: str, docs: List[str] = None, docs_sm: List[str] = None
    ):

        if docs_sm is None and docs is None:
            raise Exception("docs_sm or docs need to be set")

        _, _kwd = self.query.question(question)

        return [
            float(i)
            for i in self.query.token_similarity(
                " ".join(_kwd),
                docs_sm if docs_sm else [self.content_cut(i) for i in docs],
            )
        ]

    def hybrid_similarity(
        self,
        question: str,
        question_vector: List[float],
        docs_vector: List[List[float]],
        docs: List[str] = None,
        docs_sm: List[str] = None,
        tkweight: float = 0.3,
        vtweight: float = 0.7,
    ):

        if docs_sm is None and docs is None:
            raise Exception("docs_sm or docs need to be set")

        _, _kwd = self.query.question(question)
        _h, _t, _v = self.query.hybrid_similarity(
            question_vector,
            docs_vector,
            " ".join(_kwd),
            docs_sm if docs_sm else [self.content_cut(i) for i in docs],
            tkweight,
            vtweight,
        )
        return [float(i) for i in _h]

    def vector_similarity(
        self, question_vector: List[float], docs_vector: List[List[float]]
    ):
        return [
            float(i) for i in self.query.vector_similarity(question_vector, docs_vector)
        ]
