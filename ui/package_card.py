from __future__ import annotations

import hashlib
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from core.categories import category_label
from core.package import Package


ICON_COLORS = [
    "#5aa469",
    "#6aa6d9",
    "#c08f4f",
    "#9b8fd3",
    "#d07468",
    "#6cb6a9",
    "#b98f55",
    "#7aa65a",
]

CARD_WIDTH = 292
CARD_HEIGHT = 112


def icon_color(name: str) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return ICON_COLORS[digest[0] % len(ICON_COLORS)]


class PackageCard(QFrame):
    """Mint-style package tile: compact, clickable, no inline actions."""

    activated = pyqtSignal(object)

    def __init__(self, package: Package) -> None:
        super().__init__()
        self.package = package
        self.setObjectName("packageCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 8, 10, 8)
        outer.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(9)
        top.addWidget(self._build_icon(package), 0, Qt.AlignTop)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(4)

        title = QLabel(package.name)
        title.setObjectName("packageTitle")
        title.setWordWrap(False)
        copy.addWidget(title)

        summary = QLabel(package.description or package.short_fallback)
        summary.setObjectName("packageSummary")
        summary.setWordWrap(False)
        summary.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        copy.addWidget(summary)

        top.addLayout(copy, 1)

        installed = QLabel("OK")
        installed.setObjectName("installedMark")
        installed.setAlignment(Qt.AlignCenter)
        installed.setFixedSize(24, 24)
        installed.setVisible(package.installed)
        top.addWidget(installed, 0, Qt.AlignTop)

        outer.addLayout(top, 1)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(5)

        bottom.addWidget(self._meta("Termux"))
        bottom.addWidget(self._dot())
        bottom.addWidget(self._meta(category_label(package.category)))

        if package.gui:
            bottom.addWidget(self._dot())
            bottom.addWidget(self._meta("GUI"))
        if package.x11_required:
            bottom.addWidget(self._dot())
            bottom.addWidget(self._meta("X11"))

        bottom.addStretch(1)
        outer.addLayout(bottom)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.activated.emit(self.package)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    @staticmethod
    def _meta(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("packageMeta")
        return label

    @staticmethod
    def _dot() -> QLabel:
        label = QLabel("/")
        label.setObjectName("packageMetaDot")
        return label

    @staticmethod
    def _build_icon(package: Package) -> QLabel:
        label = QLabel()
        label.setObjectName("pkgIconLabel")
        label.setFixedSize(48, 48)
        label.setAlignment(Qt.AlignCenter)

        if package.icon_path and Path(package.icon_path).exists():
            pixmap = QIcon(package.icon_path).pixmap(48, 48)
            if not pixmap.isNull():
                label.setPixmap(pixmap)
                return label

        label.setText((package.name[0] if package.name else "?").upper())
        label.setStyleSheet(
            f"background: {icon_color(package.name)};"
            "border-radius: 8px;"
            "font-size: 21px;"
            "font-weight: 700;"
            "color: white;"
        )
        return label
