import math
from datetime import datetime
from typing import List, Tuple, Optional

import numpy as np


def mmr_reranking_optimized(
    query_embedding: List[float],
    search_results_embedding: List[List[float]],
    lambda_param: float = 0.5,
    top_k: int = 10,
) -> List[int]:
    """
    | 场景描述 | 推荐 `lambda_param` | 解释与示例 |
    | :--- | :--- | :--- |
    | **传统搜索引擎** | **0.6 ~ 0.8** | 用户希望最相关的结果排在前面。可以接受一定程度重复，但第一页结果必须高度相关。 |
    | **推荐系统 / 探索发现** | **0.3 ~ 0.5** | 目标是展示多样化的内容，避免给用户推荐相同的东西。例如：新闻推荐、商品推荐、内容发现平台。 |
    | **学术检索、法律案例检索** | **0.5 ~ 0.7** | 需要平衡：既要找到最相关的文献/案例，又要覆盖问题的不同方面或不同学派的观点。 |
    | **去除重复/近乎重复的文档** | **0.1 ~ 0.3** | 主要目的是过滤掉内容几乎相同的冗余文档。 |
    """
    if not search_results_embedding:
        return []

    n_docs = len(search_results_embedding)
    top_k = min(top_k, n_docs)

    doc_embeddings_np = np.array(search_results_embedding)
    query_embedding_np = np.array(query_embedding)

    query_norm = np.linalg.norm(query_embedding_np)
    doc_norms = np.linalg.norm(doc_embeddings_np, axis=1)
    relevance_scores = np.dot(doc_embeddings_np, query_embedding_np) / (
        doc_norms * query_norm + 1e-9
    )

    doc_doc_similarities = np.dot(doc_embeddings_np, doc_embeddings_np.T) / (
        np.outer(doc_norms, doc_norms) + 1e-9
    )

    selected_indices = []
    remaining_indices = list(range(n_docs))

    first_selected = np.argmax(relevance_scores)
    selected_indices.append(first_selected)
    remaining_indices.remove(first_selected)

    while len(selected_indices) < top_k and remaining_indices:
        rel_scores = relevance_scores[remaining_indices]
        max_sim_to_selected = np.max(
            doc_doc_similarities[np.ix_(remaining_indices, selected_indices)], axis=1
        )
        mmr_scores = (
            lambda_param * rel_scores - (1 - lambda_param) * max_sim_to_selected
        )

        best_idx_in_remaining = np.argmax(mmr_scores)
        best_idx = remaining_indices[best_idx_in_remaining]

        selected_indices.append(best_idx)
        del remaining_indices[best_idx_in_remaining]

    return selected_indices


class PageReranker:
    """
    一个页面重排器，结合了原始相关性分数和页面权重（如PageRank）来计算最终分数。
    """

    def __init__(self, page_rank_boost_factor: float = 0.15):
        """
        初始化重排器。
        参数:
        page_rank_boost_factor: 页面权重的影响因子。这个值越大，页面权重对最终分数的影响就越大。
        """
        if not page_rank_boost_factor > 0:
            raise ValueError("page_rank_boost_factor 必须是正数。")
        self.page_rank_boost_factor = page_rank_boost_factor

    def get_boost(self, docs_scores: List[tuple[float, float | None]]) -> List[float]:
        """
        根据原始相关性分数和页面权重，计算新的文档分数。
        采用加法模型计算新分数：
        new_score = original_relevance_score + (page_rank_boost_factor * page_rank_score)
        参数:
        docs_scores: 一个元组列表，每个元组包含 (relevance_score, page_rank_score)。
                     - relevance_score (float): 文档的原始相关性分数。
                     - page_rank_score (float | None): 文档的页面权重，值应在 0 到 1 之间。如果为 None，则视为 0。
        返回:
        一个浮点数列表，代表每个文档经过重排后的新分数。
        """
        boosts = []
        for relevance_score, page_rank_score in docs_scores:
            pr_score = page_rank_score if page_rank_score is not None else 0.0
            if not 0.0 <= pr_score <= 1.0:
                raise ValueError(f"页面权重必须在 0 到 1 之间，但收到了: {pr_score}")

            boost = relevance_score * self.page_rank_boost_factor * pr_score
            boosts.append(boost)

        return boosts


class TimeReranker:
    def __init__(
        self,
        time_boost_factor: float = 0.1,  # 建议设为 0.1 或 0.15
        half_life_days: float = 30.0,
        method: str = "multiplicative",
    ):
        """
        method:
          - 'multiplicative': (默认) 乘法模式。Boost = 原始分 * 因子 * 时间衰减。
                              优点：不破坏相关性，烂文章就算新也没用。
                              适合：综合搜索、技术文档。
          - 'additive':       加法模式。Boost = 因子 * 时间衰减。
                              优点：给新内容固定的“奖励分”。
                              适合：强时效性新闻，因子建议设小 (0.05)。
        """
        self.time_boost_factor = time_boost_factor
        self.half_life_days = half_life_days
        self.method = method
        self.decay_constant = math.log(2) / self.half_life_days

    def get_boost(
        self, docs_scores: List[Tuple[float, Optional[datetime]]]
    ) -> List[float]:
        now = datetime.now()
        boosts = []

        for relevance_score, doc_dt in docs_scores:
            if doc_dt is None:
                boosts.append(0.0)
                continue

            # 处理时区和未来时间
            if doc_dt.tzinfo is not None and now.tzinfo is None:
                doc_dt = doc_dt.replace(tzinfo=None)

            delta = now - doc_dt
            age_days = max(0.0, delta.total_seconds() / 86400.0)  # 防止未来时间

            try:
                decay_score = math.exp(-self.decay_constant * age_days)
            except OverflowError:
                decay_score = 0.0

            # --- 核心差异 ---
            if self.method == "multiplicative":
                # 乘法模式：基于原始分加权 (推荐，与 PageReranker 逻辑一致)
                # 如果 factor=0.1, relevance=0.8, decay=1.0 -> boost = 0.08
                boost = relevance_score * self.time_boost_factor * decay_score
            else:
                # 加法模式：独立加权
                # 如果 factor=0.1, decay=1.0 -> boost = 0.1
                boost = self.time_boost_factor * decay_score

            boosts.append(boost)

        return boosts
