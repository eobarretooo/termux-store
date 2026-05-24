from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests


DB_BASE_URL = "https://raw.githubusercontent.com/eobarretooo/termux-store-db/main"
DB_INDEX_URL = f"{DB_BASE_URL}/packages/index.json"
DB_PACKAGE_URL = f"{DB_BASE_URL}/packages/{{name}}.json"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"


HttpGet = Callable[..., requests.Response]


class DbSync:
    def __init__(
        self,
        cache_dir: Path | str = DEFAULT_CACHE_DIR,
        http_get: HttpGet = requests.get,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.metadata_dir = self.cache_dir / "metadata"
        self.http_get = http_get
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def fetch_index(self) -> list[dict[str, Any]]:
        cache_path = self.cache_dir / "index.json"
        try:
            response = self.http_get(DB_INDEX_URL, timeout=10)
            response.raise_for_status()
            cache_path.write_text(response.text, encoding="utf-8")
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception:
            return self._read_json(cache_path, fallback=[])

    def fetch_package(self, name: str) -> dict[str, Any]:
        cache_path = self.metadata_dir / f"{name}.json"
        try:
            response = self.http_get(DB_PACKAGE_URL.format(name=name), timeout=10)
            response.raise_for_status()
            cache_path.write_text(response.text, encoding="utf-8")
            data = response.json()
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
