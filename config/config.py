import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class LlmClientConfig:
    def __init__(self, base_url: str, model: str, api_key: str, max_tokens: int):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens

    @classmethod
    def from_env(cls) -> "LlmClientConfig":
        return cls(
            base_url=os.getenv("BASE_URL", ""),
            model=os.getenv("MODEL", ""),
            api_key=os.getenv("API_KEY", ""),
            max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
        )


def get_memory_store_dir() -> Path:
    memory_store_dir = os.getenv("MEMORY_STORE_DIR", str(PROJECT_ROOT / "data" / "memory")).strip()
    return Path(memory_store_dir).expanduser()


def get_rag_paths(default_path: Path) -> list[str]:
    rag_paths = os.getenv("RAG_PATHS", str(default_path)).strip()
    return [
        str(Path(path.strip()).expanduser())
        for path in rag_paths.split(os.pathsep)
        if path.strip()
    ]
