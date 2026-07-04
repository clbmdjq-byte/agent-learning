from rag.models import Chunk, Document


class DocumentSpliter:
    def __init__(self, chunk_size: int, overlap: int):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if overlap < 0:
            raise ValueError("overlap must be greater than or equal to 0")
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_documents(self, documents: list[Document]) -> list[Chunk]:
        chunks = []
        for document in documents:
            metadata = document.metadata
            content = document.content
            index = 1
            step = self.chunk_size - self.overlap
            for i in range(0, len(content), step):
                chunk_id = f"{metadata.source}_{index}"
                chunks.append(Chunk(content[i:i + self.chunk_size], chunk_id, metadata))
                index += 1
        return chunks
