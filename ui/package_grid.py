from __future__ import annotations

import hashlib

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from core.categories import category_label
from core.package import Package


_ICON_COLORS = [
    "#3584e4",
    "#33d17a",
    "#ff7800",
    "#9141ac",
    "#e5a50a",
    "#2190a4",
    "#c64600",
    "#ed333b",
    "#26a269",
    "#613583",
]

_CARD_WIDTH = 252
_CARD_HEIGHT = 188
_GRID_CELL = QSize(274, 210)


def _icon_color(name: str) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return _ICON_COLORS[digest[0] % len(_ICON_COLORS)]


class PackageCard(QFrame):
    action_requested = pyqtSignal(object)

    def __init__(self, package: Package) -> None:
        super().__init__()
        self.package = package
        self.setObjectName("packageCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedSize(_CARD_WIDTH, _CARD_HEIGHT)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(9)

        top = QHBoxLayout()
        top.setSpacing(10)

        icon_letter = (package.name[0] if package.name else "?").upper()
        icon = QLabel(icon_letter)
        icon.setObjectName("pkgIconLabel")
        icon.setFixedSize(58, 58)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            f"background: {_icon_color(package.name)};"
            "border-radius: 16px;"
            "font-size: 24px;"
            "font-weight: 900;"
            "color: white;"
        )
        top.addWidget(icon, 0, Qt.AlignTop)

        top_text = QVBoxLayout()
        top_text.setContentsMargins(0, 0, 0, 0)
        top_text.setSpacing(4)

        title = QLabel(package.name)
        title.setObjectName("packageTitle")
        title.setWordWrap(False)
        top_text.addWidget(title)

        category = category_label(package.category)
        version = package.version or "unknown version"
        meta = QLabel(f"{category} / {version}")
        meta.setObjectName("packageMeta")
        top_text.addWidget(meta)
        top_text.addStretch(1)

        top.addLayout(top_text, 1)
        outer.addLayout(top)

        description = QLabel(package.description or "No description available.")
        description.setObjectName("packageDescription")
        description.setWordWrap(True)
        description.setMaximumHeight(40)
        description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        outer.addWidget(description)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(8)

        if package.installed:
            bottom.addWidget(self._pill("Installed", "installedPill"))
        if package.gui:
            bottom.addWidget(self._pill("GUI", "featurePill"))
        if package.x11_required:
            bottom.addWidget(self._pill("X11", "featurePill"))

        bottom.addStretch(1)

        if package.installed:
            action = QPushButton("Remove")
            action.setObjectName("removeButton")
        else:
            action = QPushButton("Install")
            action.setObjectName("installButton")

        action.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        action.clicked.connect(lambda _checked=False: self.action_requested.emit(self.package))
        bottom.addWidget(action)
        outer.addLayout(bottom)

    @staticmethod
    def _pill(text: str, object_name: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName(object_name)
        label.setAlignment(Qt.AlignCenter)
        return label


class PackageGrid(QListWidget):
    package_selected = pyqtSignal(object)
    package_action_requested = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._packages: list[Package] = []
        self.setAlternatingRowColors(False)
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setWrapping(True)
        self.setSpacing(12)
        self.setGridSize(_GRID_CELL)
        self.setUniformItemSizes(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.itemDoubleClicked.connect(self._emit_package)

    def set_packages(self, packages: list[Package]) -> None:
        self.clear()
        self._packages = packages

        for package in packages:
            card = PackageCard(package)
            card.action_requested.connect(self.package_action_requested.emit)
            item = QListWidgetItem()
            item.setSizeHint(_GRID_CELL)
            item.setData(Qt.UserRole, package)
            self.addItem(item)
            self.setItemWidget(item, card)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
