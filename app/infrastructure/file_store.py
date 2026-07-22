import json
from pathlib import Path
from typing import Any, Callable, TypeVar

from filelock import FileLock

T = TypeVar("T")


class JsonFileStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = FileLock(f"{path}.lock")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self, default: T) -> T:
        if not self.path.exists():
            return default
        with self.lock:
            with self.path.open("r", encoding="utf-8") as file:
                return json.load(file)

    def write(self, data: Any) -> None:
        with self.lock:
            tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
            with tmp_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            tmp_path.replace(self.path)

    def update(self, default: T, handler: Callable[[T], T]) -> T:
        with self.lock:
            if self.path.exists():
                with self.path.open("r", encoding="utf-8") as file:
                    current: T = json.load(file)
            else:
                current = default
            updated = handler(current)
            tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
            with tmp_path.open("w", encoding="utf-8") as file:
                json.dump(updated, file, ensure_ascii=False, indent=2)
            tmp_path.replace(self.path)
            return updated

    def append_jsonl(self, record: Any) -> None:
        with self.lock:
            with self.path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
