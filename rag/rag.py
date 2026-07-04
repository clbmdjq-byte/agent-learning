import os
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.context_builder import ContextBuilder
from rag.loader import DocumentLoader
from rag.reranker import Reranker
from rag.retriever import Retriever, merge
from rag.spliter import DocumentSpliter


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
        self.context_builder = ContextBuilder()

    def search(self, query: str):
        retrieved = self.retriever.retrieve(query)
        return self.reranker.rerank(query, merge(retrieved))

    def build_context(self, query: str) -> str:
        results = self.search(query)
        return self.context_builder.build_context(results)

    def find(self, query: str) -> str:
        return self.build_context(query)


def build_rag() -> LocalRag:
    default_rag_path = Path(__file__).resolve().parent.parent.parent / "agent-learning-knowledge"
    rag_paths = os.getenv("RAG_PATHS", str(default_rag_path)).strip()
    paths = [path.strip() for path in rag_paths.split(os.pathsep) if path.strip()]
    return LocalRag(paths)

if __name__ == "__main__":
    mock_path = Path(__file__).resolve().parent.parent.parent / "agent-learning-knowledge"
    rag = LocalRag([str(mock_path)])
    print(rag.build_context("LocalRag 如何组合 RAG 流程"))
