from __future__ import annotations

import hashlib

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
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

_CARD_HEIGHT = 96


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

        outer = QHBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(14)

        icon_letter = (package.name[0] if package.name else "?").upper()
        icon = QLabel(icon_letter)
        icon.setObjectName("pkgIconLabel")
        icon.setFixedSize(54, 54)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            f"background: {_icon_color(package.name)};"
            "border-radius: 12px;"
            "font-size: 22px;"
            "font-weight: 800;"
            "color: rgba(255,255,255,0.95);"
        )
        outer.addWidget(icon, 0, Qt.AlignVCenter)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(3)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title = QLabel(package.name)
        title.setObjectName("packageTitle")
        title_row.addWidget(title, 0)

        if package.installed:
            title_row.addWidget(self._pill("Installed", "installedPill"))
        if package.gui:
            title_row.addWidget(self._pill("GUI", "featurePill"))
        if package.x11_required:
            title_row.addWidget(self._pill("X11", "featurePill"))

        title_row.addStretch(1)
        info.addLayout(title_row)

        category = category_label(package.category)
        version = package.version or "unknown version"
        meta = QLabel(f"{category} / {version}")
        meta.setObjectName("packageMeta")
        info.addWidget(meta)

        description = QLabel(package.description or "No description available.")
        description.setObjectName("packageDescription")
        description.setMaximumHeight(20)
        description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        info.addWidget(description)

        outer.addLayout(info, 1)

        if package.installed:
            action = QPushButton("Remove")
            action.setObjectName("removeButton")
        else:
            action = QPushButton("Install")
            action.setObjectName("installButton")

        action.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        action.clicked.connect(lambda _checked=False: self.action_requested.emit(self.package))
        outer.addWidget(action, 0, Qt.AlignVCenter)

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
        self.setSpacing(6)
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
            item.setSizeHint(QSize(0, _CARD_HEIGHT))
            item.setData(Qt.UserRole, package)
            self.addItem(item)
            self.setItemWidget(item, card)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
