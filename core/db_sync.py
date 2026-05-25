from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.icon_resolver import get_icon
from core.package import Package


DEFAULT_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "curated_packages.md"


class DbSync:
    """Local curated package catalog.

    The original project idea used a remote metadata database. The current app
    is intentionally offline-friendly: it parses data/curated_packages.md and
    merges that metadata with Termux pkg output in the UI layer.
    """

    def __init__(self, data_file: Path | str = DEFAULT_DATA_FILE, **_: object) -> None:
        self.data_file = Path(data_file)
        self._index: dict[str, dict[str, Any]] | None = None

    def fetch_index(self) -> list[dict[str, Any]]:
        return list(self.index_by_name().values())

    def fetch_package(self, name: str) -> dict[str, Any]:
        return self.index_by_name().get(name, {})

    def index_by_name(self) -> dict[str, dict[str, Any]]:
        if self._index is None:
            self._index = {
                item["name"]: item
                for item in self._parse_curated_file()
                if isinstance(item.get("name"), str)
            }
        return self._index

    def curated_packages(self) -> list[Package]:
        packages: list[Package] = []
        for metadata in self.fetch_index():
            package = Package(name=metadata["name"])
            package.apply_metadata(metadata)
            packages.append(package)
        return packages

    def _parse_curated_file(self) -> list[dict[str, Any]]:
        if not self.data_file.exists():
            return []

        category = "utilities"
        items: list[dict[str, Any]] = []

        for raw_line in self.data_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()

            if line.startswith("## "):
                category = self._category_from_heading(line)
                continue

            if not line.startswith("|") or "---" in line or "Pacote" in line:
                continue

            columns = [part.strip() for part in line.strip("|").split("|")]
            if len(columns) < 4:
                continue

            name, description, gui, x11 = columns[:4]
            if not name or name.lower() == "pacote":
                continue

            items.append(
                {
                    "name": name,
                    "category": category,
                    "short_description": description,
                    "long_description": description,
                    "gui": self._truthy(gui),
                    "x11_required": self._truthy(x11),
                    "install_command": f"pkg install {name}",
                    "launch_command": self._launch_command(name, self._truthy(x11)),
                    "icon_path": get_icon(name),
                    "tips": [],
                    "screenshots": [],
                    "community_rating": {
                        "works_great": 0,
                        "unstable": 0,
                        "broken": 0,
                    },
                }
            )

        return items

    @staticmethod
    def _category_from_heading(line: str) -> str:
        match = re.search(r"\(([^)]+)\)", line)
        return match.group(1).strip().lower() if match else "utilities"

    @staticmethod
    def _truthy(value: str) -> bool:
        normalized = value.strip().lower()
        return normalized in {"yes", "sim", "true", "1", "gui", "x11", "check"}

    @staticmethod
    def _launch_command(name: str, x11_required: bool) -> str:
        return f"DISPLAY=:0 {name}" if x11_required else name
