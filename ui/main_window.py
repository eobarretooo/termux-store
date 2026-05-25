from __future__ import annotations

from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from core.package import Package
from core.store import TermuxStore
from ui.install_dialog import run_pkg_command
from ui.package_detail import PackageDetailDialog
from ui.package_grid import PackageGrid
from ui.search_bar import SearchBar
from ui.sidebar import Sidebar


_THEME_DIR = Path(__file__).resolve().parents[1] / "assets" / "themes"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.store = TermuxStore()
        self.active_category = "all"
        self.active_query = ""
        self._dark = False

        self.setWindowTitle("Termux Store")
        self.setMinimumSize(980, 680)

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
        self.status.setContentsMargins(22, 6, 22, 10)
        root_layout.addWidget(self.status)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("headerBar")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(22, 0, 18, 0)
        layout.setSpacing(12)

        mark = QLabel("TS")
        mark.setObjectName("appMark")
        layout.addWidget(mark)

        title = QLabel("Termux Store")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.theme_btn = QPushButton("Dark")
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
        layout.setContentsMargins(22, 18, 22, 14)
        layout.setSpacing(16)

        layout.addWidget(self._build_hero())

        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self._set_query)
        layout.addWidget(self.search_bar)

        self.grid = PackageGrid()
        self.grid.package_selected.connect(self._open_detail)
        self.grid.package_action_requested.connect(self._run_package_action)
        layout.addWidget(self.grid, 1)

        return container

    def _build_hero(self) -> QWidget:
        hero = QFrame()
        hero.setObjectName("heroPanel")

        layout = QVBoxLayout(hero)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        kicker = QLabel("TERMUX NATIVE")
        kicker.setObjectName("heroKicker")
        layout.addWidget(kicker)

        title = QLabel("The app store for Termux")
        title.setObjectName("heroTitle")
        layout.addWidget(title)

        subtitle = QLabel(
            "Browse packages, discover X11 apps, and install directly through pkg."
        )
        subtitle.setObjectName("heroSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.hero_metric = QLabel("Loading package catalog...")
        self.hero_metric.setObjectName("heroMetric")
        layout.addWidget(self.hero_metric)

        return hero

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
        self.store.refresh()
        self._apply_filters()
        self.status.setText(self._status_text())

    def _set_category(self, category: str) -> None:
        self.active_category = category
        self._apply_filters()

    def _set_query(self, query: str) -> None:
        self.active_query = query.strip().lower()
        self._apply_filters()

    def _apply_filters(self) -> None:
        filtered = self.store.category_packages(self.active_category)
        if self.active_query:
            filtered = self.store.search(self.active_query, filtered)

        self.grid.set_packages(filtered)
        self.status.setText(self.store.stats(len(filtered)))
        if hasattr(self, "hero_metric"):
            self.hero_metric.setText(self.store.stats(len(filtered)))

    def _open_detail(self, package: Package) -> None:
        details = self.store.db_sync.fetch_package(package.name)
        if details:
            package.apply_metadata(details)

        dialog = PackageDetailDialog(package, self.store.pkg_manager, self)
        dialog.exec_()
        self.store.set_installed(package.name, package.installed)
        self._apply_filters()

    def _run_package_action(self, package: Package) -> None:
        if package.installed:
            command = [self.store.pkg_manager.pkg_executable, "uninstall", "-y", package.name]
            action = "Remove"
        else:
            command = [self.store.pkg_manager.pkg_executable, "install", "-y", package.name]
            action = "Install"

        success = run_pkg_command(self, action, command)
        if success:
            self.store.set_installed(package.name, not package.installed)
        self._apply_filters()

    def _status_text(self) -> str:
        if not self.store.pkg_manager.available():
            return "pkg not found - run inside Termux for package operations"
        return self.store.stats()
