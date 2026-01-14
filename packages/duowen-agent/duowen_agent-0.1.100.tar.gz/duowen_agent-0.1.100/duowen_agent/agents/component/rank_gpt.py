import logging
import time
from typing import List

from duowen_agent.llm.chat_model import BaseAIChat
from duowen_agent.llm.tokenizer import tokenizer
from duowen_agent.utils.concurrency import concurrent_execute
from pydantic import BaseModel, Field

from .base import BaseComponent
from ...prompt.prompt_build import GeneralPromptBuilder
from ...utils.core_utils import json_observation, stream_to_string


class Ranker(BaseComponent):
    """通过语言模型实现 rerank能力 不支持分值，只能排序"""

    # query: str, documents
    def __init__(self, llm: BaseAIChat):
        super().__init__()
        self.llm = llm
        self.content_tokens_limit = None
        self.documents = None
        self.question_tokens = None
        self.prompt_tokens = 1000
        self.rank_limit = 5
        self.query = None

    def init_data(self, query: str, documents: List[str], rank_limit=5):
        self.query = query
        self.rank_limit = rank_limit
        self.question_tokens = tokenizer.chat_len(query)
        self.documents = documents
        self.content_tokens_limit = (
            self.llm.token_limit - self.prompt_tokens - self.question_tokens
        )

    def cut_passages(self):
        _content_tokens = self.content_tokens_limit
        _passages = []
        for _chunk in self.documents:
            _curr_token = tokenizer.chat_len(_chunk)
            _content_tokens = _content_tokens - _curr_token
            if _content_tokens > 0:
                _passages.append(_chunk)
            else:
                break
        self.documents = _passages

    def chk_passages_tokens_limit(self):
        if tokenizer.chat_len("".join(self.documents)) > self.content_tokens_limit:
            return False
        else:
            return True

    def get_prefix_prompt(self, num):
        return [
            {
                "role": "system",
                "content": "You are RankGPT, an intelligent assistant that can rank passages based on their relevancy to the query.",
            },
            {
                "role": "user",
                "content": f"I will provide you with {num} passages, each indicated by number identifier []. \nRank the passages based on their relevance to query: {self.query}.",
            },
            {"role": "assistant", "content": "Okay, please provide the passages."},
        ]

    def get_post_prompt(self, num):
        return f"Search Query: {self.query}. \nRank the {num} passages above based on their relevance to the search query. The passages should be listed in descending order using identifiers. The most relevant passages should be listed first. The output format should be [] > [], e.g., [1] > [2]. Only response the ranking results, do not say any word or explain."

    def create_permutation_instruction(self):
        if not self.chk_passages_tokens_limit():
            raise ValueError(
                f"Agent Ranker token passages overly long, model tokens limit number {self.llm.token_limit}."
            )
        num = len(self.documents)
        messages = self.get_prefix_prompt(num)
        rank = 0
        for hit in self.documents:
            rank += 1
            content = hit
            content = content.replace("Title: Content: ", "")
            content = content.strip()
            messages.append({"role": "user", "content": f"[{rank}] {content}"})
            messages.append(
                {"role": "assistant", "content": f"Received passage [{rank}]."}
            )
        messages.append({"role": "user", "content": self.get_post_prompt(num)})
        return messages

    def run_llm(self, messages):
        response = stream_to_string(
            self.llm.chat_for_stream(messages=messages, temperature=0)
        )
        return response

    async def arun_llm(self, messages):
        response = await self.llm.achat(messages=messages, temperature=0)
        return response

    @staticmethod
    def clean_response(response: str):
        new_response = ""
        for c in response:
            if not c.isdigit():
                new_response += " "
            else:
                new_response += c
        new_response = new_response.strip()
        return new_response

    @staticmethod
    def remove_duplicate(response):
        new_response = []
        for c in response:
            if c not in new_response:
                new_response.append(c)
        return new_response

    def receive_permutation(self, permutation):
        _passages = []
        response = self.clean_response(permutation)
        response = [int(x) - 1 for x in response.split()]
        response = self.remove_duplicate(response)
        original_rank = [tt for tt in range(len(self.documents))]
        response = [ss for ss in response if ss in original_rank]
        response = response + [tt for tt in original_rank if tt not in response]
        for x in response[: self.rank_limit]:
            _passages.append(self.documents[x])
        return _passages

    def receive_index(self, permutation):
        _passages = []
        response = self.clean_response(permutation)
        response = [int(x) - 1 for x in response.split()]
        response = self.remove_duplicate(response)
        return response[: self.rank_limit]

    def run(self, query: str, documents: List[str], rank_limit=5) -> List[str]:
        self.init_data(query, documents, rank_limit)
        if self.rank_limit < len(self.documents):
            messages = self.create_permutation_instruction()
            permutation = self.run_llm(messages)
            item = self.receive_permutation(permutation)
            return item
        else:
            return self.documents

    def run_with_index(
        self, query: str, documents: List[str], rank_limit=5
    ) -> List[int]:
        self.init_data(query, documents, rank_limit)
        if self.rank_limit <= len(self.documents):
            messages = self.create_permutation_instruction()
            permutation = self.run_llm(messages)
            item = self.receive_index(permutation)
            return item
        else:
            item = [tt for tt in range(len(self.documents))]
            return item

    async def arun(self, query: str, documents: List[str], rank_limit=5) -> List[str]:
        self.init_data(query, documents, rank_limit)
        if self.rank_limit < len(self.documents):
            messages = self.create_permutation_instruction()
            permutation = await self.arun_llm(messages)
            item = self.receive_permutation(permutation)
            return item
        else:
            return self.documents


class RelevanceScore(BaseModel):
    reasoning: str = Field(..., description="推理过程(50字以内)")
    relevance_score: int = Field(..., ge=0, le=5, description="相关性分数")


class RankerScore(BaseComponent):
    """通过语言模型实现 对文档进行相关性打分"""

    def __init__(self, llm: BaseAIChat, concurrency: int = 5):
        super().__init__()
        self.llm = llm
        self.concurrency = concurrency

    def build_prompt(self) -> GeneralPromptBuilder:
        return GeneralPromptBuilder(
            instruction="""你是一个专业的文档相关性评估专家。请根据[用户问题]和[文档片段]，评估文档对问题的回答价值。
请严格遵守以下评分标准（1-5分）：
- **1分 (无关/极弱)**: 文档与问题完全无关，或仅包含个别无关紧要的词汇。
- **2分 (弱相关)**: 涉及相关领域，但没有提供解决问题所需的具体信息。
- **3分 (部分相关)**: 能够回答问题的次要部分，或提供了一些背景信息，但核心问题未解决。
- **4分 (强相关)**: 直接回答了问题的核心部分，虽然可能缺少一些细节，但对用户很有帮助。
- **5分 (完美相关)**: 准确、全面地回答了用户问题，提供了详尽的细节或深度见解。
""",
            step="""1. **识别关键要素**
   - 提取问题核心需求：[主要查询点]
   - 标记文档核心信息：[关键知识点]
2. **对比分析**
   - 主题匹配度：[领域/场景重合度]
   - 信息完整度：[问题需求覆盖比例]
   - 细节精确度：[数据/术语准确率]
3. **缺失项检测**
   - 未覆盖的需求点：[列出具体遗漏]
   - 矛盾信息：[存在冲突的陈述]
4. **推理结论**
   - 说明评分依据与标准条款对应关系""",
            output_format=RelevanceScore,
            sample="""Input:
用户问题："网站显示500错误怎么办？"
文档片段："HTTP 500 Internal Server Error 是通用的服务器错误消息。通常是服务器端的脚本错误或配置问题导致的。建议检查服务器日志文件(error_log)以获取详细信息。"

Output:
```json
{
  "reasoning": "用户询问500错误的解决方案。文档准确定义了500错误，并给出了'检查服务器日志'这一核心解决思路，虽然没有给出具体代码修复方案，但指明了正确的排查方向，属于高度相关。",
  "relevance_score": 4
}
```
""",
            note="""1. **分析意图**：简要分析用户真正想知道什么。
2. **内容比对**：判断文档是否包含用户查询的关键信息。
3. **最终打分**：基于上述分析给出1-5的整数分值。""",
        )

    def run(self, query: str, documents: List[str]) -> List[int]:
        results = concurrent_execute(
            self._run, [(query, doc) for doc in documents], self.concurrency
        )
        return results

    def _run(self, query: str, document: str) -> int:
        for i in range(3):
            try:
                _prompt = self.build_prompt().get_instruction(
                    f"用户问题：{query}\n\n文档片段：\n{document}"
                )

                resp = stream_to_string(self.llm.chat_for_stream(_prompt))

                resp = json_observation(resp, RelevanceScore)

                return resp.relevance_score
            except Exception as e:
                logging.error(f"RankerScore run error: {e}")
                time.sleep((i + 1) * 0.1)
                continue

    async def arun(self, query: str, document: str) -> int:
        _prompt = self.build_prompt().get_instruction(
            f"用户问题：{query}\n\n文档片段：\n{document}"
        )
        resp = await self.llm.achat(_prompt)
        res: RelevanceScore = json_observation(resp, RelevanceScore)
        return res.relevance_score
