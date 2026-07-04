class Metadata:
    def __init__(self, source: str):
        self.source = source


class Document:
    def __init__(self, metadata: Metadata, content: str):
        self.metadata = metadata
        self.content = content


class Chunk:
    def __init__(self,
                 content: str,
                 chunk_id: str,
                 metadata: Metadata):
        self.chunk_id = chunk_id
        self.content = content
        self.metadata = metadata


class SearchResult:
    def __init__(self, chunk: Chunk, score: float, retrieval_source: str):
        self.chunk = chunk
        self.score = score
        self.retrieval_source = retrieval_source

class MergedSearchResult:
    def __init__(self, chunk: Chunk):
        self.chunk = chunk
        self.source_scores: dict[str, float] = {}
        self.final_score: float = 0.0