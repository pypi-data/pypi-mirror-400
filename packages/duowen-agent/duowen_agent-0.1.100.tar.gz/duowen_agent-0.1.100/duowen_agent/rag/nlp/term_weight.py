import json
import logging
import math
import os
import re

import numpy as np
from duowen_agent.rag.nlp.base_tokenizer import BaseTokenizer
from duowen_agent.rag.nlp.surname import check_surname

_curr_dir = os.path.dirname(os.path.abspath(__file__))


class TermWeight:
    def __init__(self, tokenizer: BaseTokenizer):
        with open(f"{_curr_dir}/dictionary/stopwords.json", encoding="utf-8") as f:
            self.stop_words = set(json.loads(f.read())["STOPWORDS"])

        self.tokenizer = tokenizer

        self.ne, self.df = {}, {}

        with open(_curr_dir + "/dictionary/ner.json", "r") as f:
            try:
                self.ne = json.load(f)
            except Exception as e:
                print(str(e))
                logging.warning("Load ner.json FAIL!")

    def add_stop_word(self, word: str):
        """添加停用词

        Args:
            word: 要添加的停用词
        """
        if word and word not in self.stop_words:
            self.stop_words.add(word)

    def add_ner(self, word: str, type: str):
        """添加命名实体识别词

        Args:
            word: 要添加的词
            type: 实体类型 (如: toxic, func, corp, loca, sch, stock, firstnm)
        """
        if word and type:
            self.ne[word] = type

    def add_term_freq(self, word: str, freq: int):
        """添加词频

        Args:
            word: 要添加的词
            freq: 词频数值
        """
        if word and freq > 0:
            self.df[word] = freq

    def pretoken(self, txt, num=False, stpwd=True):
        patt = [
            r"[~—\t @#%!<>,\.\?\":;'\{\}\[\]_=\(\)\|，。？》•●○↓《；‘’：“”【¥ 】…￥！、·（）×`&\\/「」\\]"
        ]
        rewt = []
        for p, r in rewt:
            txt = re.sub(p, r, txt)

        res = []
        for t in self.tokenizer.tokenize(txt).split():
            tk = t
            if (stpwd and tk in self.stop_words) or (
                re.match(r"[0-9]$", tk) and not num
            ):
                continue
            for p in patt:
                if re.match(p, t):
                    tk = "#"
                    break
            # tk = re.sub(r"([\+\\-])", r"\\\1", tk)
            if tk != "#" and tk:
                res.append(tk)
        return res

    def token_merge(self, tks):
        def one_term(t):
            return len(t) == 1 or re.match(r"[0-9a-z]{1,2}$", t)

        res, i = [], 0
        while i < len(tks):
            j = i
            if (
                i == 0
                and one_term(tks[i])
                and len(tks) > 1
                and (len(tks[i + 1]) > 1 and not re.match(r"[0-9a-zA-Z]", tks[i + 1]))
            ):  # 多 工位
                res.append(" ".join(tks[0:2]))
                i = 2
                continue

            while (
                j < len(tks)
                and tks[j]
                and tks[j] not in self.stop_words
                and one_term(tks[j])
            ):
                j += 1
            if j - i > 1:
                if j - i < 5:
                    res.append(" ".join(tks[i:j]))
                    i = j
                else:
                    res.append(" ".join(tks[i : i + 2]))
                    i = i + 2
            else:
                if len(tks[i]) > 0:
                    res.append(tks[i])
                i += 1
        return [t for t in res if t]

    def ner(self, t):
        if not self.ne:
            return ""
        res = self.ne.get(t, "")
        if res:
            return res

    def split(self, txt):
        tks = []
        for t in re.sub(r"[ \t]+", " ", txt).split():
            if (
                tks
                and re.match(r".*[a-zA-Z]$", tks[-1])
                and re.match(r".*[a-zA-Z]$", t)
                and tks
                and self.ne.get(t, "") != "func"
                and self.ne.get(tks[-1], "") != "func"
            ):
                tks[-1] = tks[-1] + " " + t
            else:
                tks.append(t)
        return tks

    def weights(self, tks, preprocess=True):
        num_pattern = re.compile(r"[0-9,.]{2,}$")
        short_letter_pattern = re.compile(r"[a-z]{1,2}$")
        num_space_pattern = re.compile(r"[0-9. -]{2,}$")
        letter_pattern = re.compile(r"[a-z. -]+$")

        def ner(t):
            if num_pattern.match(t):
                return 2
            if short_letter_pattern.match(t):
                return 0.01
            if not self.ne or t not in self.ne:
                return 1
            m = {
                "toxic": 2,
                "func": 1,
                "corp": 3,
                "loca": 3,
                "sch": 3,
                "stock": 3,
                "firstnm": 1,
            }
            return m[self.ne[t]]

        def postag(t):
            _t = self.tokenizer.tag(t)
            if _t in {"r", "c", "d"}:
                return 0.3
            if _t in {"ns", "nt", "nr"}:
                return 3
            if _t in {"nz"}:
                return 2.5
            if _t in {"n"}:
                return 2
            if re.match(r"[0-9-]+", _t):
                return 2
            if check_surname(t):  # 姓名
                return 3
            return 1

        def freq(t):
            if num_space_pattern.match(t):
                return 3
            s = self.tokenizer.freq(t)
            if not s and letter_pattern.match(t):
                return 300
            if not s:
                s = 0

            if not s and len(t) >= 4:
                s = [
                    tt
                    for tt in self.tokenizer.fine_grained_tokenize(t).split()
                    if len(tt) > 1
                ]
                if len(s) > 1:
                    s = np.min([freq(tt) for tt in s]) / 6.0
                else:
                    s = 0

            return max(s, 10)

        def df(t):
            if num_space_pattern.match(t):
                return 5
            if t in self.df:
                return self.df[t] + 3
            elif letter_pattern.match(t):
                return 300
            elif len(t) >= 4:
                s = [
                    tt
                    for tt in self.tokenizer.fine_grained_tokenize(t).split()
                    if len(tt) > 1
                ]
                if len(s) > 1:
                    return max(3, np.min([df(tt) for tt in s]) / 6.0)

            return 3

        def idf(s, N):
            return math.log10(10 + ((N - s + 0.5) / (s + 0.5)))

        tw = []
        if not preprocess:
            idf1 = np.array([idf(freq(t), 10000000) for t in tks])
            idf2 = np.array([idf(df(t), 1000000000) for t in tks])
            wts = (0.3 * idf1 + 0.7 * idf2) * np.array(
                [ner(t) * postag(t) for t in tks]
            )
            wts = [s for s in wts]
            tw = list(zip(tks, wts))
        else:
            for tk in tks:
                tt = self.token_merge(self.pretoken(tk, True))
                idf1 = np.array([idf(freq(t), 10000000) for t in tt])
                idf2 = np.array([idf(df(t), 1000000000) for t in tt])
                wts = (0.3 * idf1 + 0.7 * idf2) * np.array(
                    [ner(t) * postag(t) for t in tt]
                )
                wts = [s for s in wts]
                tw.extend(zip(tt, wts))

        S = np.sum([s for _, s in tw])
        _res = [(t, s / S) for t, s in tw]

        # bug fix: 对合并后的token，权重平分
        _res_ = []
        for i in _res:
            if len(i[0].split(" ")) > 1:
                for j in i[0].split(" "):
                    _res_.append((j, i[1]))
            else:
                _res_.append(i)

        return _res_


if __name__ == "__main__":
    tokenizer = Tokenizer()
    term_weight = TermWeight(tokenizer)

    print(
        term_weight.weights(
            [
                "多校划片就是一个小区对应多个小学初中，让买了学区房的家庭也不确定到底能上哪个学校。"
            ]
        )
    )
