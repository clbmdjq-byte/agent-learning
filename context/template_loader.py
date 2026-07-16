from functools import lru_cache
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


@lru_cache
def load_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    return path.read_text(encoding="utf-8").strip()
