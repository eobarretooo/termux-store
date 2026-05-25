from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.categories import CATEGORIES, category_label
from core.package import Package
from core.store import TermuxStore
from ui.category_tile import CategoryTile
from ui.install_dialog import run_pkg_command
from ui.package_detail_page import PackageDetailPage
from ui.package_grid import PackageGrid
from ui.search_bar import SearchBar
from ui.sidebar import Sidebar


_THEME_DIR = Path(__file__).resolve().parents[1] / "assets" / "themes"

_CATEGORY_ICONS: dict[str, str] = {
    "development": "</>",
    "terminal": ">_",
    "multimedia": "AV",
    "network": "NET",
    "utilities": "UTL",
    "security": "SEC",
    "graphics": "IMG",
    "productivity": "DOC",
    "games": "PAD",
    "desktop": "WM",
    "fonts": "Aa",
}


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
        self.status.setContentsMargins(18, 5, 18, 8)
        root_layout.addWidget(self.status)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("headerBar")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 0, 16, 0)
        layout.setSpacing(10)

        mark = QLabel("TS")
        mark.setObjectName("appMark")
        layout.addWidget(mark)

        title = QLabel("Software Manager")
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
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self._set_query)
        layout.addWidget(self.search_bar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("pageStack")
        self.home_page = self._build_home_page()
        self.list_page = self._build_list_page()
        self.detail_page = PackageDetailPage()
        self.detail_page.back_requested.connect(self._return_from_detail)
        self.detail_page.action_requested.connect(self._run_package_action)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.detail_page)
        layout.addWidget(self.stack, 1)

        return container

    def _build_home_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setObjectName("homeScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setObjectName("homePage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 2, 10, 2)
        layout.setSpacing(16)

        welcome = QFrame()
        welcome.setObjectName("welcomePanel")
        welcome_layout = QVBoxLayout(welcome)
        welcome_layout.setContentsMargins(20, 16, 20, 16)
        welcome_layout.setSpacing(6)

        kicker = QLabel("TERMUX SOFTWARE MANAGER")
        kicker.setObjectName("welcomeKicker")
        welcome_layout.addWidget(kicker)

        title = QLabel("Install desktop apps and command-line tools")
        title.setObjectName("welcomeTitle")
        title.setWordWrap(True)
        welcome_layout.addWidget(title)

        self.welcome_stats = QLabel("Loading package catalog...")
        self.welcome_stats.setObjectName("welcomeStats")
        welcome_layout.addWidget(self.welcome_stats)
        layout.addWidget(welcome)

        layout.addWidget(self._section_title("Featured"))
        self.featured_grid = PackageGrid()
        self.featured_grid.setFixedHeight(142)
        self.featured_grid.package_selected.connect(self._show_detail)
        layout.addWidget(self.featured_grid)

        layout.addWidget(self._section_title("Categories"))
        self.category_panel = QFrame()
        self.category_panel.setObjectName("categoryPanel")
        self.category_grid = QGridLayout(self.category_panel)
        self.category_grid.setContentsMargins(0, 0, 0, 0)
        self.category_grid.setHorizontalSpacing(10)
        self.category_grid.setVerticalSpacing(10)
        layout.addWidget(self.category_panel)

        layout.addStretch(1)
        scroll.setWidget(page)
        return scroll

    def _build_list_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("listPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        self.home_button = QPushButton("Home")
        self.home_button.setObjectName("backButton")
        self.home_button.clicked.connect(self._show_home)
        header.addWidget(self.home_button, 0, Qt.AlignTop)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(3)

        self.list_title = QLabel()
        self.list_title.setObjectName("listTitle")
        copy.addWidget(self.list_title)

        self.list_subtitle = QLabel()
        self.list_subtitle.setObjectName("listSubtitle")
        copy.addWidget(self.list_subtitle)

        header.addLayout(copy, 1)
        layout.addLayout(header)

        self.empty_state = QLabel("No packages found.")
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setVisible(False)
        layout.addWidget(self.empty_state)

        self.grid = PackageGrid()
        self.grid.package_selected.connect(self._show_detail)
        layout.addWidget(self.grid, 1)

        return page

    @staticmethod
    def _section_title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

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
        self._refresh_home()

        if self.active_category == "all" and not self.active_query:
            self._show_home()
        else:
            self._apply_filters()

        self.status.setText(self._status_text())

    def _refresh_home(self) -> None:
        self.featured_grid.set_packages(self.store.featured_packages())
        self.welcome_stats.setText(self.store.stats())
        self._refresh_category_tiles()

    def _refresh_category_tiles(self) -> None:
        while self.category_grid.count():
            item = self.category_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        categories = [
            (category_id, label)
            for category_id, label in CATEGORIES
            if category_id not in {"all", "installed"}
        ]

        for index, (category_id, label) in enumerate(categories):
            count = len(self.store.category_packages(category_id))
            tile = CategoryTile(
                category_id,
                label,
                count,
                _CATEGORY_ICONS.get(category_id, label[:2].upper()),
            )
            tile.selected.connect(self._set_category)
            self.category_grid.addWidget(tile, index // 3, index % 3)

    def _set_category(self, category: str) -> None:
        self.active_category = category
        self.sidebar.set_active(category)

        if category == "all":
            self._show_home()
            return

        self._apply_filters()

    def _set_query(self, query: str) -> None:
        self.active_query = query.strip().lower()
        if self.active_query or self.active_category != "all":
            self._apply_filters()
        else:
            self._show_home()

    def _apply_filters(self) -> None:
        filtered = self.store.category_packages(self.active_category)
        if self.active_query:
            filtered = self.store.search(self.active_query, filtered)

        title = self._list_title(len(filtered))
        self.list_title.setText(title)
        self.list_subtitle.setText(self._list_subtitle(len(filtered)))
        self.grid.set_packages(filtered)
        self.grid.setVisible(bool(filtered))
        self.empty_state.setVisible(not filtered)
        self.stack.setCurrentWidget(self.list_page)
        self.status.setText(self.store.stats(len(filtered)))

    def _list_title(self, count: int) -> str:
        if self.active_query:
            return f"Search results for '{self.active_query}'"
        return category_label(self.active_category)

    def _list_subtitle(self, count: int) -> str:
        noun = "package" if count == 1 else "packages"
        if self.active_query and self.active_category != "all":
            return f"{count} {noun} in {category_label(self.active_category)}"
        return f"{count} {noun}"

    def _show_home(self) -> None:
        self.active_category = "all"
        self.sidebar.set_active("all")
        if self.search_bar.text():
            self.active_query = ""
            self.search_bar.clear()
        self.stack.setCurrentWidget(self.home_page)
        self.status.setText(self.store.stats())

    def _show_detail(self, package: Package) -> None:
        details = self.store.db_sync.fetch_package(package.name)
        if details:
            package.apply_metadata(details)

        self.detail_page.set_package(package)
        self.stack.setCurrentWidget(self.detail_page)
        self.status.setText(f"{package.name} details")

    def _return_from_detail(self) -> None:
        if self.active_category == "all" and not self.active_query:
            self._show_home()
        else:
            self._apply_filters()

    def _run_package_action(self, package: Package) -> None:
        if package.installed:
            command = [self.store.pkg_manager.pkg_executable, "uninstall", "-y", package.name]
            action = "Remove"
            target_installed = False
        else:
            command = [self.store.pkg_manager.pkg_executable, "install", "-y", package.name]
            action = "Install"
            target_installed = True

        success = run_pkg_command(self, action, command)
        if success:
            self.store.set_installed(package.name, target_installed)
            package.installed = target_installed
            self.detail_page.set_package(package)
            self._refresh_home()

        self.status.setText(self.store.stats())

    def _status_text(self) -> str:
        if not self.store.pkg_manager.available():
            return "pkg not found - run inside Termux for package operations"
        return self.store.stats()
