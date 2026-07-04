import re

from rag.models import SearchResult, Chunk, MergedSearchResult


class Retriever:
    def __init__(self, chunks: list[Chunk], top_k: int) :
        self.chunks = chunks
        self.top_k = top_k or 10

    # 先实现一种后续进行扩展
    def retrieve(self, query: str) -> list[SearchResult]:
        search_results = []
        if self.chunks:
            for chunk in self.chunks:
                score = calculate_score(query, chunk)
                if score > 0:
                    search_results.append(SearchResult(chunk, score, "common"))
        # 过滤出top_k，可优化为维护top_k避免排序
        return sorted(search_results, key=lambda r: r.score, reverse=True)[:self.top_k]


def calculate_score(query: str, chunk: Chunk) -> float:
    score = 0.0
    query = query.lower()

    keywords = split_keywords(query)
    meta_info = chunk.metadata.source.lower()
    content = chunk.content.lower()
    if query in meta_info:
        score += 20
    if query in content:
        score += 10
    for word in keywords:
        score+= meta_info.count(word) * 2
        score+= content.count(word)
    return score

def split_keywords(query: str) -> list[str]:
    res = [
        word
        for word in re.split(r"[\s,，。.；;！？!?:：]+", query)
        if word
    ]
    for n in range(1, len(query)+1):
        for i in range(len(query)-n+1):
            res.append(
                query[i:i+n]
            )
    return res
def merge(results: list[SearchResult]) -> dict[str, MergedSearchResult]:
    merged_map: dict[str, MergedSearchResult] = {}
    for result in results:
        chunk_id = result.chunk.chunk_id

        if chunk_id not in merged_map:
            merged_map[chunk_id] = MergedSearchResult(result.chunk)

        merged_map[chunk_id].source_scores[result.retrieval_source] = result.score
    return merged_map
