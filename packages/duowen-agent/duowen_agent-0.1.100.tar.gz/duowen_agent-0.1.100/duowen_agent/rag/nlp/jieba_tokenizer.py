import logging
import math
import os
import re
import warnings
from typing import List

import nltk
from nltk import PorterStemmer, WordNetLemmatizer, word_tokenize
from nltk.data import find

from .base_tokenizer import BaseTokenizer

# 忽略无效转义序列的警告
warnings.filterwarnings(
    "ignore", message=".*invalid escape sequence.*", category=DeprecationWarning
)

# 忽略pkg_resources弃用警告
warnings.filterwarnings(
    "ignore", message=".*pkg_resources is deprecated.*", category=DeprecationWarning
)


from jieba import Tokenizer, re_userdict


from .utils import (
    is_chinese,
)


def ensure_nltk_resource(resource_name):
    try:
        find(resource_name)
    except LookupError:
        logging.info(f"Resource '{resource_name}' not found. Downloading...")
        nltk.download(resource_name.split("/")[-1])


ensure_nltk_resource("tokenizers/punkt_tab")
ensure_nltk_resource("corpora/wordnet")
ensure_nltk_resource("corpora/omw-1.4")

_curr_dir = os.path.dirname(os.path.abspath(__file__))


class JiebaTokenizer(BaseTokenizer):
    def __init__(self, user_dict=None):

        self.SPLIT_CHAR = r"([ ,\.<>/?;:'\[\]\\`!@#$%^&*\(\)\{\}\|_+=《》，。？、；‘’：“”【】~！￥%……（）——-]+|[a-zA-Z0-9,\.-]+)"
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.DENOMINATOR = 1000000
        self.tokenizer = Tokenizer()
        self.tokenizer.initialize()
        with open(f"{_curr_dir}/dictionary/jieba_ext_dict.txt", encoding="utf-8") as f:
            self.tokenizer.load_userdict(f)

        if user_dict:
            self.tokenizer.load_userdict(user_dict)
        self.pos = {}
        self.initialize_pos()

    def initialize_pos(self):
        self.pos = {}
        with self.tokenizer.get_dict_file() as f:
            for line in f:
                word, freq, tag = re_userdict.match(
                    line.strip().decode("utf-8")
                ).groups()
                self.pos[word] = tag
                if tag is not None and word is not None:
                    self.pos[word.strip()] = tag.strip()

        with open(f"{_curr_dir}/dictionary/jieba_ext_dict.txt", encoding="utf-8") as f:
            for line in f:
                word, freq, tag = re_userdict.match(line.strip()).groups()
                self.pos[word] = tag
                if tag is not None and word is not None:
                    self.pos[word.strip()] = tag.strip()

    def add_tok(self, token, freq: int = None, tag: str = None):
        """添加词语到分词词典
        Example: tok_add_word("量子计算", freq=100, pos="n")
        """
        self.tokenizer.add_word(token, freq=freq, tag=tag)
        self.pos[token] = tag

    def freq(self, tk):
        _freq = self.tokenizer.FREQ.get(tk, 0)
        if _freq:
            _freq = int(math.log(float(_freq) / self.DENOMINATOR) + 0.5)  # 对数压缩
            return int(math.exp(_freq) * self.DENOMINATOR + 0.5)  # 整数近似
        else:
            return 0

    def tag(self, tk):
        if tk in self.pos:
            return self.pos[tk]
        else:
            return ""

    def _split_by_lang(self, line):
        txt_lang_pairs = []
        arr = re.split(self.SPLIT_CHAR, line)
        for a in arr:
            if not a:
                continue
            s = 0
            e = s + 1
            zh = is_chinese(a[s])
            while e < len(a):
                _zh = is_chinese(a[e])
                if _zh == zh:
                    e += 1
                    continue
                txt_lang_pairs.append((a[s:e], zh))
                s = e
                e = s + 1
                zh = _zh
            if s >= len(a):
                continue
            txt_lang_pairs.append((a[s:e], zh))
        return txt_lang_pairs

    def merge_(self, tks):
        res = []
        tks = re.sub(r"[ ]+", " ", tks).split()
        s = 0
        while True:
            if s >= len(tks):
                break
            E = s + 1
            for e in range(s + 2, min(len(tks) + 2, s + 6)):
                tk = "".join(tks[s:e])
                if re.search(self.SPLIT_CHAR, tk) and self.tag(tk):
                    E = e
            res.append("".join(tks[s:E]))
            s = E

        return " ".join(res)

    def english_normalize_(self, tks):
        return [
            (
                self.stemmer.stem(self.lemmatizer.lemmatize(t))
                if re.match(r"[a-zA-Z_-]+$", t)
                else t
            )
            for t in tks
        ]

    def tokenize(self, line):
        line = re.sub(r"\W+", " ", line)
        line = self._strQ2B(line).lower()
        line = self._tradi2simp(line)

        arr = self._split_by_lang(line)
        res = []
        for L, lang in arr:
            if not lang:
                res.extend(
                    [
                        self.stemmer.stem(self.lemmatizer.lemmatize(t))
                        for t in word_tokenize(L)
                    ]
                )
                continue
            if len(L) < 2 or re.match(r"[a-z\.-]+$", L) or re.match(r"[0-9\.-]+$", L):
                res.append(L)
                continue

            res.extend(self.tokenizer.lcut(L))
        res = " ".join(res)
        return self.merge_(res)

    def get_precise_cut(self, text) -> List[str]:
        """
        基于 jieba 搜索引擎模式的所有分词候选结果，筛选出一条最佳的、
        无重叠的路径，效果类似于 Jieba 的精确模式。

        Args:
            text (str): 需要分词的原始字符串。

        Returns:
            list: 一个类似于精确模式分词结果的列表。
        """
        # print(f"get_precise_cut: {text}")
        # 1. 使用搜索引擎模式的 tokenize 获取所有词和它们的位置

        tokens_with_pos = self.tokenizer.tokenize(text, mode="search")

        # 2. 【关键修正】从所有候选中，排除掉与原始字符串完全相同的那个词。
        #    这是为了防止算法一步到位，直接选择整个字符串作为结果。
        candidates = []
        text_len = len(text)
        for word, start, end in tokens_with_pos:
            # 只有当词的长度不等于原句长度时，才采纳为候选
            if len(word) != text_len:

                candidates.append((word, start, end))

        # 如果过滤后没有候选词了（例如输入本身就是一个很短的词），
        # 那么直接返回原句分词结果。
        if not candidates:
            # print(f"get_precise_cut not candidate: {text}")
            # print("=" * 20)
            return [text]

        # 3. 将候选词按起始位置存入字典，方便快速查找
        #    格式：{0: [('中华', 0, 2)], 2: [('人民', 2, 4)], ...}
        tokens_map = {}
        for word, start, end in candidates:
            if start not in tokens_map:
                tokens_map[start] = []
            tokens_map[start].append((word, start, end))

        # 4. 执行正向最大匹配算法
        result = []
        current_pos = 0
        while current_pos < text_len:
            # 检查当前位置是否有可选的词
            if current_pos not in tokens_map:
                # 如果没有找到任何词（例如，对于未登录词），
                # 就将当前单个字符作为一个词，然后前进一步，避免死循环。
                result.append(text[current_pos])
                current_pos += 1
                continue

            # 从当前位置开始的所有候选词中，找到结束位置最远（即最长）的那个词
            # best_candidate = (word, start, end)
            best_candidate = max(tokens_map[current_pos], key=lambda x: x[2])

            # 将选中的词语加入结果列表
            result.append(best_candidate[0])

            # 将指针移动到选中词语的末尾
            current_pos = best_candidate[2]

        # print(f"get_precise_cut result: {result}")

        result2 = []
        _buffer = ""
        for i in result:
            if len(i) == 1:
                _buffer += i
            else:
                if _buffer:
                    result2.append(_buffer)
                    _buffer = ""
                result2.append(i)
        if _buffer:
            result2.append(_buffer)
        # print(f"get_precise_cut result2: {result2}")
        # print("=" * 20)
        return result2

    def fine_grained_tokenize(self, tks):
        tks = tks.split()
        zh_num = len([1 for c in tks if c and is_chinese(c[0])])
        if zh_num < len(tks) * 0.2:
            res = []
            for tk in tks:
                res.extend(tk.split("/"))
            return " ".join(res)
        res = []
        for tk in tks:
            if len(tk) < 3 or re.match(r"[0-9,\.-]+$", tk):
                res.append(tk)
                continue
            # for i in self.tokenizer.lcut_for_search(tk):
            for i in self.get_precise_cut(tk):
                res.append(i)
        return " ".join(self.english_normalize_(res))
