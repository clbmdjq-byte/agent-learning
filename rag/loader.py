from pathlib import Path

from rag.models import Document, Metadata


class DocumentLoader:
    def __init__(self, scan_paths: list[str]):
        self.scan_paths = scan_paths
        self.suffixes = [".md", ".txt"]

    def load(self) -> list[Document]:
        documents = []
        for scan_path in self.scan_paths:
            root = Path(scan_path).expanduser()
            if not root.exists():
                continue
            for file in root.rglob("*"):
                if file.suffix.lower() in self.suffixes:
                    content = file.read_text(encoding="utf-8")
                    source = str(file.relative_to(root))
                    documents.append(Document(Metadata(source), content))
        return documents
