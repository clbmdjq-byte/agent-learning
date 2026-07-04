from pathlib import Path

from rag.models import Document, Metadata


class DocumentLoader:
    def __init__(self, scan_paths: list[str]):
        self.scan_paths = scan_paths
        self.suffixes = [".md", ".txt"]

    def load(self) -> list[Document]:
        documents = []
        for scan_path in self.scan_paths:
            path = Path(scan_path)
            if not path.exists():
                continue
            for file in path.rglob("*"):
                if file.suffix in self.suffixes:
                    content = file.read_text(encoding="utf-8")
                    documents.append(Document(Metadata(file.name), content))
        return documents
