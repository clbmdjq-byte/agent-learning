from pathlib import Path

from config.config import get_store_dir


PathLike = str | Path


class LocalFileStore:
    def __init__(self):
        """创建以指定目录为根目录的本地文件存储。"""
        self.root_dir = Path(get_store_dir()).expanduser().resolve()
        if not self.root_dir.exists():
            self.root_dir.mkdir(parents=True)

    def write_text(self, path: PathLike, content: str) -> None:
        """覆盖写入 UTF-8 文本，目标文件不存在时先创建。"""
        target = self._resolve(path)
        self._ensure_parent_dir(target)
        if not target.exists():
            target.touch()
        target.write_text(content, encoding="utf-8")

    def append_text(self, path: PathLike, content: str) -> None:
        """追加写入 UTF-8 文本，目标文件不存在时先创建。"""
        target = self._resolve(path)
        self._ensure_parent_dir(target)
        if not target.exists():
            target.touch()
        with target.open("a", encoding="utf-8") as file:
            file.write(content)

    def append_line(self, path: PathLike, line: str) -> None:
        """追加写入一行 UTF-8 文本，目标文件不存在时先创建。"""
        line_content = line if line.endswith("\n") else f"{line}\n"
        self.append_text(path, line_content)

    def read_text(self, path: PathLike) -> str | None:
        """读取 UTF-8 文本文件，目标文件不存在时返回 None。"""
        target = self._resolve(path)
        if not target.exists():
            return None
        return target.read_text(encoding="utf-8")

    def read_lines(self, path: PathLike) -> list[str]:
        """按行读取 UTF-8 文本文件，目标文件不存在时返回空列表。"""
        target = self._resolve(path)
        if not target.exists():
            return []
        return target.read_text(encoding="utf-8").splitlines()

    def exists(self, path: PathLike) -> bool:
        """判断目标路径是否存在。"""
        return self._resolve(path).exists()

    def list_files(self, path: PathLike, pattern: str = "*") -> list[Path]:
        """列出目录下匹配指定模式的文件，目录不存在时返回空列表。"""
        target = self._resolve(path)
        if not target.exists():
            return []
        if not target.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        return sorted(file for file in target.glob(pattern) if file.is_file())

    def _resolve(self, path: PathLike) -> Path:
        """解析本地路径，并拒绝访问存储根目录之外的路径。"""
        raw_path = Path(path).expanduser()
        target = raw_path if raw_path.is_absolute() else self.root_dir / raw_path
        resolved = target.resolve()

        if resolved != self.root_dir and self.root_dir not in resolved.parents:
            raise ValueError(f"Path is outside store root: {path}")

        return resolved

    def _ensure_parent_dir(self, path: Path) -> None:
        """目标文件的父目录不存在时自动创建。"""
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
