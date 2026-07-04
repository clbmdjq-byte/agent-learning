from rag.models import SearchResult, MergedSearchResult


class Reranker:
    def __init__(self, top_k: int, source_map: dict[str, float]):
        self.top_k = top_k or 5
        self.source_map = source_map


    def rerank(self, query: str,
               merged_map: dict[str, MergedSearchResult]) -> list[SearchResult]:
        if not merged_map:
            return []
        # 1可以使用reranker模型进行重排给出分数，也可以结合之前的结果给分
        # 当前先实现一种来源加权的算法
        reranked_results = []
        for merged_search in merged_map.values():
            final_score = 0.0

            for source, source_score in merged_search.source_scores.items():
                weight = self.source_map.get(source, 0.0)
                final_score += source_score * weight

            if final_score > 0:
                reranked_results.append(SearchResult(merged_search.chunk,
                                                     final_score, "reranked"))
        return sorted(reranked_results, key=lambda x: x.score, reverse=True)[:self.top_k]
