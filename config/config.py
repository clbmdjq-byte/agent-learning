import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class LlmClientConfig:
    def __init__(self,
                 base_url: str,
                 model: str,
                 api_key: str,
                 max_tokens: int,
                 max_context_tokens: int = 8192,
                 context_safety_tokens: int = 128):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.max_context_tokens = max_context_tokens
        self.context_safety_tokens = context_safety_tokens

    @classmethod
    def from_env(cls) -> "LlmClientConfig":
        return cls(
            base_url=os.getenv("BASE_URL", ""),
            model=os.getenv("MODEL", ""),
            api_key=os.getenv("API_KEY", ""),
            max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
            max_context_tokens=int(os.getenv("MAX_CONTEXT_TOKENS", "8192")),
            context_safety_tokens=int(
                os.getenv("CONTEXT_SAFETY_TOKENS", "128")
            ),
        )


def get_store_dir() -> Path:
    store_dir = os.getenv("STORE_DIR", str(PROJECT_ROOT / "data" / "store")).strip()
    return Path(store_dir).expanduser()


def get_rag_paths(default_path: Path) -> list[str]:
    rag_paths = os.getenv("RAG_PATHS", str(default_path)).strip()
    return [
        str(Path(path.strip()).expanduser())
        for path in rag_paths.split(os.pathsep)
        if path.strip()
    ]
