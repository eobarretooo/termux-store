from __future__ import annotations

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.db_sync import DbSync
from core.package import Package
from core.pkg_manager import PkgManager
from ui.package_detail import PackageDetailDialog
from ui.package_grid import PackageGrid
from ui.search_bar import SearchBar
from ui.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.pkg_manager = PkgManager()
        self.db_sync = DbSync()
        self.packages: list[Package] = []
        self.active_category = "all"
        self.active_query = ""

        self.setWindowTitle("Termux Store")
        self.setMinimumSize(900, 600)
        self._build_ui()
        self._load_packages()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)

        self.sidebar = Sidebar()
        self.sidebar.category_selected.connect(self._set_category)
        root.addWidget(self.sidebar, 0)

        main = QVBoxLayout()
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)

        self.status = QLabel("Loading packages")
        main.addWidget(self.status)

        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self._set_query)
        main.addWidget(self.search_bar)

        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._load_packages)
        main.addWidget(refresh)

        self.grid = PackageGrid()
        self.grid.package_selected.connect(self._open_detail)
        main.addWidget(self.grid, 1)

        container = QWidget()
        container.setLayout(main)
        root.addWidget(container, 1)

    def _load_packages(self) -> None:
        self.status.setText("Loading packages")
        packages = self.pkg_manager.list_all()
        metadata = self.db_sync.index_by_name()

        for package in packages:
            if package.name in metadata:
                package.apply_metadata(metadata[package.name])

        self.packages = packages
        self.status.setText(self._status_text())
        self._apply_filters()

    def _set_category(self, category: str) -> None:
        self.active_category = category
        self._apply_filters()

    def _set_query(self, query: str) -> None:
        self.active_query = query.strip().lower()
        self._apply_filters()

    def _apply_filters(self) -> None:
        filtered = self.packages

        if self.active_category != "all":
            filtered = [pkg for pkg in filtered if pkg.category == self.active_category]

        if self.active_query:
            filtered = [
                pkg
                for pkg in filtered
                if self.active_query in pkg.name.lower()
                or self.active_query in pkg.description.lower()
            ]

        self.grid.set_packages(filtered)
        self.status.setText(f"{len(filtered)} shown / {len(self.packages)} total")

    def _open_detail(self, package: Package) -> None:
        details = self.db_sync.fetch_package(package.name)
        if details:
            package.apply_metadata(details)

        dialog = PackageDetailDialog(package, self.pkg_manager, self)
        dialog.exec_()

    def _status_text(self) -> str:
        if not self.pkg_manager.available():
            return "pkg not found. Run inside Termux for package operations."
        return f"{len(self.packages)} packages loaded"
