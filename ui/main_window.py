from __future__ import annotations

from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from core.categories import infer_category
from core.db_sync import DbSync
from core.package import Package
from core.pkg_manager import PkgManager
from ui.package_detail import PackageDetailDialog
from ui.package_grid import PackageGrid
from ui.install_dialog import show_command_result
from ui.search_bar import SearchBar
from ui.sidebar import Sidebar


_THEME_DIR = Path(__file__).resolve().parents[1] / "assets" / "themes"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.pkg_manager = PkgManager()
        self.db_sync = DbSync()
        self.packages: list[Package] = []
        self.active_category = "all"
        self.active_query = ""
        self._dark = True

        self.setWindowTitle("Termux Store")
        self.setMinimumSize(960, 640)

        self._build_ui()
        self._apply_theme()
        self._load_packages()

    def _build_ui(self) -> None:
        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.category_selected.connect(self._set_category)
        body.addWidget(self.sidebar, 0)
        body.addWidget(self._build_content(), 1)

        body_widget = QWidget()
        body_widget.setLayout(body)
        root_layout.addWidget(body_widget, 1)

        self.status = QLabel()
        self.status.setObjectName("statusLabel")
        self.status.setContentsMargins(16, 4, 16, 8)
        root_layout.addWidget(self.status)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("headerBar")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(10)

        title = QLabel("Termux Store")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.theme_btn = QPushButton("Light")
        self.theme_btn.setObjectName("themeToggleButton")
        self.theme_btn.setToolTip("Toggle light/dark theme")
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.clicked.connect(self._load_packages)
        layout.addWidget(refresh_btn)

        return header

    def _build_content(self) -> QWidget:
        container = QWidget()
        container.setObjectName("contentPanel")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 14, 16, 10)
        layout.setSpacing(12)

        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self._set_query)
        layout.addWidget(self.search_bar)

        self.grid = PackageGrid()
        self.grid.package_selected.connect(self._open_detail)
        self.grid.package_action_requested.connect(self._run_package_action)
        layout.addWidget(self.grid, 1)

        return container

    def _apply_theme(self) -> None:
        qss_file = _THEME_DIR / ("dark.qss" if self._dark else "light.qss")
        try:
            stylesheet = qss_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            stylesheet = ""

        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(stylesheet)

        self.theme_btn.setText("Light" if self._dark else "Dark")

    def _toggle_theme(self) -> None:
        self._dark = not self._dark
        self._apply_theme()

    def _load_packages(self) -> None:
        self.status.setText("Loading packages...")
        packages = self.pkg_manager.list_all()
        metadata = self.db_sync.index_by_name()

        for package in packages:
            if package.name in metadata:
                package.apply_metadata(metadata[package.name])
            else:
                package.category = infer_category(package.name)

        self.packages = packages
        self._apply_filters()
        self.status.setText(self._status_text())

    def _set_category(self, category: str) -> None:
        self.active_category = category
        self._apply_filters()

    def _set_query(self, query: str) -> None:
        self.active_query = query.strip().lower()
        self._apply_filters()

    def _apply_filters(self) -> None:
        filtered = self.packages

        if self.active_category != "all":
            filtered = [p for p in filtered if p.category == self.active_category]

        if self.active_query:
            filtered = [
                p
                for p in filtered
                if self.active_query in p.name.lower()
                or self.active_query in p.description.lower()
            ]

        self.grid.set_packages(filtered)
        self.status.setText(f"{len(filtered)} shown / {len(self.packages)} total")

    def _open_detail(self, package: Package) -> None:
        details = self.db_sync.fetch_package(package.name)
        if details:
            package.apply_metadata(details)

        dialog = PackageDetailDialog(package, self.pkg_manager, self)
        dialog.exec_()

    def _run_package_action(self, package: Package) -> None:
        if package.installed:
            success, output = self.pkg_manager.remove(package.name)
            action = "Remove"
            if success:
                package.installed = False
        else:
            success, output = self.pkg_manager.install(package.name)
            action = "Install"
            if success:
                package.installed = True

        show_command_result(self, success, action, output)
        self._apply_filters()

    def _status_text(self) -> str:
        if not self.pkg_manager.available():
            return "pkg not found - run inside Termux for package operations"
        return f"{len(self.packages)} packages loaded"
