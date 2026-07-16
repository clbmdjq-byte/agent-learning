import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.config import get_rag_paths
from rag.loader import DocumentLoader
from rag.models import SearchResult
from rag.reranker import Reranker
from rag.retriever import Retriever, merge
from rag.spliter import DocumentSpliter


DEFAULT_RAG_PATH = Path(__file__).resolve().parent.parent.parent / "agent-learning-knowledge"


class LocalRag:
    def __init__(self,
                 paths: list[str],
                 chunk_size: int = 500,
                 overlap: int = 50,
                 retrieve_top_k: int = 20,
                 rerank_top_k: int = 5):
        docs = DocumentLoader(paths).load()
        chunks = DocumentSpliter(chunk_size, overlap).split_documents(docs)
        self.retriever = Retriever(chunks, retrieve_top_k)
        self.reranker = Reranker(rerank_top_k, {"common": 1.0})

    def search(self, query: str) -> list[SearchResult]:
        retrieved = self.retriever.retrieve(query)
        return self.reranker.rerank(query, merge(retrieved))


def build_rag() -> LocalRag:
    return LocalRag(get_rag_paths(DEFAULT_RAG_PATH))

if __name__ == "__main__":
    rag = build_rag()
    search_results = rag.search("LocalRag 如何组合 RAG 流程")
    for search_result in search_results:
        print(search_result.chunk.content)
