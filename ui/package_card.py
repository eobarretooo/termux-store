from __future__ import annotations

import hashlib
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from core.categories import category_label
from core.package import Package


ICON_COLORS = [
    "#39d353",
    "#58a6ff",
    "#a371f7",
    "#ff7b72",
    "#f2cc60",
    "#2fcdcd",
    "#ff8f3c",
    "#7ee787",
]

CARD_WIDTH = 252
CARD_HEIGHT = 188


def icon_color(name: str) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return ICON_COLORS[digest[0] % len(ICON_COLORS)]


class PackageCard(QFrame):
    action_requested = pyqtSignal(object)

    def __init__(self, package: Package) -> None:
        super().__init__()
        self.package = package
        self.setObjectName("packageCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(9)

        top = QHBoxLayout()
        top.setSpacing(10)

        icon = self._build_icon(package)
        top.addWidget(icon, 0, Qt.AlignTop)

        top_text = QVBoxLayout()
        top_text.setContentsMargins(0, 0, 0, 0)
        top_text.setSpacing(4)

        title = QLabel(package.name)
        title.setObjectName("packageTitle")
        title.setWordWrap(False)
        top_text.addWidget(title)

        category = category_label(package.category)
        version = package.version or "available"
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

        action = QPushButton("Remove" if package.installed else "Install")
        action.setObjectName("removeButton" if package.installed else "installButton")
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

    @staticmethod
    def _build_icon(package: Package) -> QLabel:
        label = QLabel()
        label.setObjectName("pkgIconLabel")
        label.setFixedSize(58, 58)
        label.setAlignment(Qt.AlignCenter)

        if package.icon_path and Path(package.icon_path).exists():
            pixmap = QIcon(package.icon_path).pixmap(58, 58)
            if not pixmap.isNull():
                label.setPixmap(pixmap)
                return label

        label.setText((package.name[0] if package.name else "?").upper())
        label.setStyleSheet(
            f"background: {icon_color(package.name)};"
            "border-radius: 16px;"
            "font-size: 24px;"
            "font-weight: 900;"
            "color: white;"
        )
        return label
