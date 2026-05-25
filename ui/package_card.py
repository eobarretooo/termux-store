from __future__ import annotations

import hashlib
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from core.categories import category_label
from core.package import Package


ICON_COLORS = [
    "#5c9e44",
    "#5b8fc4",
    "#c07830",
    "#8e6dc4",
    "#c45050",
    "#3a9e8a",
    "#b87c30",
    "#6aaa3a",
]

CARD_WIDTH = 0
CARD_HEIGHT = 74


def icon_color(name: str) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return ICON_COLORS[digest[0] % len(ICON_COLORS)]


class PackageCard(QFrame):
    """Mint-style list-row package tile."""

    activated = pyqtSignal(object)

    def __init__(self, package: Package) -> None:
        super().__init__()
        self.package = package
        self.setObjectName("packageCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedHeight(CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 14, 10)
        root.setSpacing(12)
        root.addWidget(self._build_icon(package), 0, Qt.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(3)

        title = QLabel(package.name)
        title.setObjectName("packageTitle")
        title.setWordWrap(False)
        text_col.addWidget(title)

        summary = QLabel(package.description or package.short_fallback)
        summary.setObjectName("packageSummary")
        summary.setWordWrap(False)
        summary.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        text_col.addWidget(summary)

        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(5)
        meta_row.addWidget(self._meta(category_label(package.category)))
        meta_row.addWidget(self._dot())

        source = QLabel("Termux")
        source.setObjectName("sourceBadge")
        meta_row.addWidget(source)

        if package.gui:
            meta_row.addWidget(self._dot())
            meta_row.addWidget(self._meta("GUI"))
        if package.x11_required:
            meta_row.addWidget(self._dot())
            meta_row.addWidget(self._meta("X11"))

        meta_row.addStretch(1)
        text_col.addLayout(meta_row)
        root.addLayout(text_col, 1)

        if package.installed:
            check = QLabel("OK")
            check.setObjectName("installedMark")
            check.setAlignment(Qt.AlignCenter)
            check.setFixedSize(28, 24)
            root.addWidget(check, 0, Qt.AlignVCenter)

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

        letter = (package.name[0] if package.name else "?").upper()
        label.setText(letter)
        label.setStyleSheet(
            f"background: {icon_color(package.name)};"
            "border-radius: 10px;"
            "font-size: 20px;"
            "font-weight: 700;"
            "color: white;"
        )
        return label
