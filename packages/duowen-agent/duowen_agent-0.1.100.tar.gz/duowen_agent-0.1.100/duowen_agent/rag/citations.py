import logging
import re
from typing import Optional

import numpy as np
from duowen_agent.llm.embedding_model import BaseEmbedding

from .nlp import LexSynth


class Citations:
    """
    引用插入器 - 用于将相关引用插入到答案文本中
    
    该类通过语义相似度匹配，将答案文本片段与提供的文本块进行关联，
    并在答案中插入对应的引用标识符。
    
    主要功能：
    1. 将答案文本分割成合适的片段
    2. 计算答案片段与候选文本块的语义相似度
    3. 为相似度高的片段插入引用标识
    4. 支持混合相似度计算（文本+向量）
    """

    def __init__(
        self,
        embedding_model: BaseEmbedding,
        lex_synth: LexSynth,
        citations_format: str = " [ID:{}]",
    ):
        """
        初始化引用插入器
        
        Args:
            embedding_model: 嵌入模型，用于生成文本的向量表示
            lex_synth: 文本处理工具，提供分词和相似度计算功能
            citations_format: 引用格式模板，默认为" [ID:{}]"
        """
        self.embedding_model = embedding_model
        self.lex_synth = lex_synth
        self.citations_format = citations_format

    def insert(
        self,
        answer: str,
        chunks: list[str],
        chunk_v: Optional[list[list[float]]] = None,
        tkweight=0.1,
        vtweight=0.9,
    ) -> tuple[str, set[int]]:
        """
        将引用插入到答案文本中
        
        处理流程：
        1. 预处理：生成文本块的向量表示（如需要）
        2. 文本分割：将答案分割成语义完整的片段
        3. 相似度计算：计算答案片段与文本块的相似度
        4. 引用插入：为相似度高的片段插入引用标识
        
        Args:
            answer: 原始答案文本
            chunks: 候选文本块列表，用于引用匹配
            chunk_v: 预计算的文本块向量（可选），如果为None则重新计算
            tkweight: 文本相似度权重（0-1），默认0.1
            vtweight: 向量相似度权重（0-1），默认0.9
            
        Returns:
            tuple[str, set[int]]: (插入引用后的答案文本, 使用的引用ID集合)
            
        算法特点：
        - 支持代码块保护（```内的内容不会被分割）
        - 使用混合相似度（文本+向量）
        - 自适应阈值调整（从高到低逐步降低）
        - 每个片段最多引用4个相关文本块
        - 避免重复引用相同的文本块
        """
        """ """
        # 步骤1: 预处理 - 生成文本块的向量表示（如需要）
        if chunk_v is None:
            chunk_v = self.embedding_model.get_embedding(chunks)
        assert len(chunks) == len(chunk_v), "文本块数量与向量数量不匹配"
        
        # 如果没有提供文本块，直接返回原答案
        if not chunks:
            return answer, set([])
            
        # 步骤2: 文本分割 - 将答案分割成语义片段
        # 特殊处理：保护代码块（```内的内容）
        pieces = re.split(r"(```)", answer)
        if len(pieces) >= 3:
            # 存在代码块，需要特殊处理
            i = 0
            pieces_ = []
            while i < len(pieces):
                if pieces[i] == "```":
                    # 收集完整的代码块
                    st = i
                    i += 1
                    while i < len(pieces) and pieces[i] != "```":
                        i += 1
                    if i < len(pieces):
                        i += 1
                    pieces_.append("".join(pieces[st:i]) + "\n")
                else:
                    # 对普通文本按标点符号分割
                    pieces_.extend(
                        re.split(r"([^\|][；。？!！\n]|[a-z][.?;!][ \n])", pieces[i])
                    )
                    i += 1
            pieces = pieces_
        else:
            # 没有代码块，直接按标点符号分割
            pieces = re.split(r"([^\|][；。？!！\n]|[a-z][.?;!][ \n])", answer)
            
        # 修复分割后的片段：将分隔符合并到前面的片段
        for i in range(1, len(pieces)):
            if re.match(r"([^\|][；。？!！\n]|[a-z][.?;!][ \n])", pieces[i]):
                pieces[i - 1] += pieces[i][0]
                pieces[i] = pieces[i][1:]
                
        # 过滤掉过短的片段（长度小于5的片段不参与匹配）
        idx = []
        pieces_ = []
        for i, t in enumerate(pieces):
            if len(t) < 5:
                continue
            idx.append(i)  # 记录原始索引
            pieces_.append(t)  # 记录有效片段
            
        logging.debug("文本分割结果: {} => {}".format(answer, pieces_))
        
        # 如果没有有效片段，直接返回
        if not pieces_:
            return answer, set([])

        # 步骤3: 相似度计算
        # 生成答案片段的向量表示
        ans_v = self.embedding_model.get_embedding(pieces_)
        
        # 处理向量维度不匹配的情况
        for i in range(len(chunk_v)):
            if len(ans_v[0]) != len(chunk_v[i]):
                # 维度不匹配时，用零向量填充
                chunk_v[i] = [0.0] * len(ans_v[0])
                logging.warning(
                    "查询和文本块维度不匹配: {} vs. {}".format(
                        len(ans_v[0]), len(chunk_v[i])
                    )
                )
                
        # 确保维度一致
        assert len(ans_v[0]) == len(chunk_v[0]), \
            "查询和文本块维度不匹配: {} vs. {}".format(len(ans_v[0]), len(chunk_v[0]))
            
        # 预处理文本块：分词和清理
        chunks_tks = [
            self.lex_synth.content_cut(self.lex_synth.query.rmWWW(ck)).split()
            for ck in chunks
        ]
        
        # 步骤4: 引用匹配
        cites = {}  # 片段索引 -> 引用ID列表
        thr = 0.63  # 初始相似度阈值
        # 自适应阈值调整：从高到低逐步降低，直到找到匹配或阈值过低
        while thr > 0.3 and len(cites.keys()) == 0 and pieces_ and chunks_tks:
            for i, a in enumerate(pieces_):
                # 计算混合相似度（文本+向量）
                sim, tksim, vtsim = self.lex_synth.query.hybrid_similarity(
                    ans_v[i],  # 答案片段向量
                    chunk_v,   # 文本块向量列表
                    self.lex_synth.content_cut(
                        self.lex_synth.query.rmWWW(pieces_[i])
                    ).split(),  # 答案片段分词
                    chunks_tks,  # 文本块分词列表
                    tkweight,    # 文本相似度权重
                    vtweight,    # 向量相似度权重
                )
                mx = np.max(sim) * 0.99  # 获取最高相似度（稍微降低以避免边界情况）
                logging.debug("片段 '{}' 的最高相似度: {}".format(pieces_[i], mx))
                
                # 如果相似度低于阈值，跳过
                if mx < thr:
                    continue
                    
                # 记录匹配的文本块ID（最多4个）
                cites[idx[i]] = list(
                    set([str(ii) for ii in range(len(chunk_v)) if sim[ii] > mx])
                )[:4]
                
            thr *= 0.8  # 降低阈值，扩大匹配范围

        # 步骤5: 引用插入
        res = ""
        seted = set([])  # 已使用的引用ID（避免重复）
        for i, p in enumerate(pieces):
            res += p
            # 只处理有引用的片段
            if i not in idx:
                continue
            if i not in cites:
                continue
                
            # 验证引用ID的有效性
            for c in cites[i]:
                assert int(c) < len(chunk_v), "引用ID超出文本块范围"
                
            # 插入引用标识（避免重复）
            for c in cites[i]:
                if c in seted:
                    continue  # 避免重复引用
                res += self.citations_format.format(c)
                seted.add(c)
                
        return res, seted