from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.request import urlopen


DB_BASE_URL = "https://raw.githubusercontent.com/eobarretooo/termux-store-db/main"
DB_INDEX_URL = f"{DB_BASE_URL}/packages/index.json"
DB_PACKAGE_URL = f"{DB_BASE_URL}/packages/{{name}}.json"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"


HttpGet = Callable[[str, int], str]


def fetch_text(url: str, timeout: int = 10) -> str:
    with urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8")


class DbSync:
    def __init__(
        self,
        cache_dir: Path | str = DEFAULT_CACHE_DIR,
        http_get: HttpGet = fetch_text,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.metadata_dir = self.cache_dir / "metadata"
        self.http_get = http_get
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def fetch_index(self) -> list[dict[str, Any]]:
        cache_path = self.cache_dir / "index.json"
        try:
            text = self.http_get(DB_INDEX_URL, 10)
            cache_path.write_text(text, encoding="utf-8")
            data = json.loads(text)
            return data if isinstance(data, list) else []
        except Exception:
            return self._read_json(cache_path, fallback=[])

    def fetch_package(self, name: str) -> dict[str, Any]:
        cache_path = self.metadata_dir / f"{name}.json"
        try:
            text = self.http_get(DB_PACKAGE_URL.format(name=name), 10)
            cache_path.write_text(text, encoding="utf-8")
            data = json.loads(text)
            return data if isinstance(data, dict) else {}
        except Exception:
            return self._read_json(cache_path, fallback={})

    def index_by_name(self) -> dict[str, dict[str, Any]]:
        return {
            item["name"]: item
            for item in self.fetch_index()
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        }

    @staticmethod
    def _read_json(path: Path, fallback: Any) -> Any:
        if not path.exists():
            return fallback

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return fallback
