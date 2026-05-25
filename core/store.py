from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.categories import CATEGORIES, infer_category
from core.db_sync import DbSync
from core.package import Package
from core.pkg_manager import PkgManager


FEATURED_PACKAGE_NAMES = [
    "firefox",
    "alacritty",
    "gimp",
    "code-oss",
    "vlc-qt",
    "blender",
    "kdenlive",
    "telegram-desktop",
]


@dataclass(slots=True)
class StoreCategory:
    id: str
    label: str
    packages: list[Package]


class TermuxStore:
    """Catalog and filtering layer inspired by mintinstall.

    Mintinstall keeps UI code separate from package grouping, installed-state
    synchronization, category views and search results. This class provides the
    same role for Termux, backed only by curated markdown metadata and `pkg`.
    """

    def __init__(
        self,
        pkg_manager: PkgManager | None = None,
        db_sync: DbSync | None = None,
    ) -> None:
        self.pkg_manager = pkg_manager or PkgManager()
        self.db_sync = db_sync or DbSync()
        self.packages: list[Package] = []
        self.categories: dict[str, StoreCategory] = {}

    def refresh(self) -> None:
        pkg_map = {package.name: package for package in self.pkg_manager.list_all()}
        packages = self.db_sync.curated_packages()

        for package in packages:
            pkg_info = pkg_map.get(package.name)
            if pkg_info is not None:
                package.version = pkg_info.version
                package.installed = pkg_info.installed
                if not package.description:
                    package.description = pkg_info.description
            elif not package.category:
                package.category = infer_category(package.name)

        self.packages = sorted(packages, key=lambda p: p.name.lower())
        self._rebuild_categories()

    def all_packages(self) -> list[Package]:
        return list(self.packages)

    def featured_packages(self) -> list[Package]:
        by_name = {package.name: package for package in self.packages}
        featured = [by_name[name] for name in FEATURED_PACKAGE_NAMES if name in by_name]
        return featured or self.packages[:8]

    def installed_packages(self) -> list[Package]:
        return [package for package in self.packages if package.installed]

    def category_packages(self, category_id: str) -> list[Package]:
        if category_id == "all":
            return self.all_packages()
        if category_id == "installed":
            return self.installed_packages()
        category = self.categories.get(category_id)
        return list(category.packages) if category else []

    def search(self, query: str, packages: Iterable[Package] | None = None) -> list[Package]:
        terms = [term for term in query.lower().split() if term]
        if not terms:
            return list(packages) if packages is not None else self.all_packages()

        source = list(packages) if packages is not None else self.all_packages()
        return [
            package
            for package in source
            if all(term in self._search_text(package) for term in terms)
        ]

    def set_installed(self, package_name: str, installed: bool) -> None:
        for package in self.packages:
            if package.name == package_name:
                package.installed = installed
                break
        self._rebuild_categories()

    def stats(self, shown_count: int | None = None) -> str:
        installed = len(self.installed_packages())
        shown = len(self.packages) if shown_count is None else shown_count
        return (
            f"{len(self.packages)} curated apps / "
            f"{installed} installed / "
            f"{shown} shown"
        )

    def _rebuild_categories(self) -> None:
        self.categories = {
            category_id: StoreCategory(category_id, label, [])
            for category_id, label in CATEGORIES
            if category_id not in {"all", "installed"}
        }

        for package in self.packages:
            category_id = package.category or "utilities"
            if category_id not in self.categories:
                self.categories[category_id] = StoreCategory(
                    category_id,
                    category_id.title(),
                    [],
                )
            self.categories[category_id].packages.append(package)

    @staticmethod
    def _search_text(package: Package) -> str:
        return " ".join(
            [
                package.name,
                package.description,
                package.long_description,
                package.category,
            ]
        ).lower()
