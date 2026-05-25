from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.categories import category_label
from core.package import Package
from ui.package_card import icon_color
from ui.rating_dialog import show_rating_placeholder


class PackageDetailPage(QWidget):
    back_requested = pyqtSignal()
    action_requested = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.package: Package | None = None
        self.setObjectName("detailPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        nav = QHBoxLayout()
        nav.setContentsMargins(0, 0, 0, 0)
        nav.setSpacing(8)

        self.back_button = QPushButton("Back")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.back_requested.emit)
        nav.addWidget(self.back_button, 0, Qt.AlignLeft)
        nav.addStretch(1)
        layout.addLayout(nav)

        card = QFrame()
        card.setObjectName("detailCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 22)
        card_layout.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(18)

        self.icon = QLabel()
        self.icon.setObjectName("detailIcon")
        self.icon.setFixedSize(96, 96)
        self.icon.setAlignment(Qt.AlignCenter)
        header.addWidget(self.icon, 0, Qt.AlignTop)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(7)

        self.title = QLabel()
        self.title.setObjectName("detailTitle")
        copy.addWidget(self.title)

        self.summary = QLabel()
        self.summary.setObjectName("detailSummary")
        self.summary.setWordWrap(True)
        copy.addWidget(self.summary)

        self.meta = QLabel()
        self.meta.setObjectName("detailMeta")
        self.meta.setWordWrap(True)
        copy.addWidget(self.meta)

        copy.addStretch(1)
        header.addLayout(copy, 1)

        self.action_button = QPushButton()
        self.action_button.clicked.connect(self._emit_action)
        header.addWidget(self.action_button, 0, Qt.AlignTop)
        card_layout.addLayout(header)

        self.description = QTextEdit()
        self.description.setObjectName("detailDescription")
        self.description.setReadOnly(True)
        card_layout.addWidget(self.description, 1)

        self.rating_button = QPushButton("Rate compatibility")
        self.rating_button.setObjectName("secondaryButton")
        self.rating_button.clicked.connect(lambda: show_rating_placeholder(self))
        card_layout.addWidget(self.rating_button, 0, Qt.AlignLeft)

        layout.addWidget(card, 1)

    def set_package(self, package: Package) -> None:
        self.package = package
        self.title.setText(package.name)
        self.summary.setText(package.description or package.short_fallback)
        self.meta.setText(self._meta_text(package))
        self.description.setPlainText(package.display_description)
        self._set_icon(package)
        self._refresh_action_button(package)

    def _emit_action(self) -> None:
        if self.package is not None:
            self.action_requested.emit(self.package)

    def _set_icon(self, package: Package) -> None:
        self.icon.clear()
        self.icon.setStyleSheet("")

        if package.icon_path and Path(package.icon_path).exists():
            pixmap = QIcon(package.icon_path).pixmap(96, 96)
            if not pixmap.isNull():
                self.icon.setPixmap(pixmap)
                return

        self.icon.setText((package.name[0] if package.name else "?").upper())
        self.icon.setStyleSheet(
            f"background: {icon_color(package.name)};"
            "border-radius: 16px;"
            "font-size: 42px;"
            "font-weight: 700;"
            "color: white;"
        )

    def _refresh_action_button(self, package: Package) -> None:
        if package.installed:
            self.action_button.setText("Remove")
            self.action_button.setObjectName("removeButton")
        else:
            self.action_button.setText("Install")
            self.action_button.setObjectName("installButton")
        self.action_button.style().unpolish(self.action_button)
        self.action_button.style().polish(self.action_button)

    @staticmethod
    def _meta_text(package: Package) -> str:
        flags = [
            f"Category: {category_label(package.category)}",
            f"Version: {package.version or 'unknown'}",
            f"Installed: {'yes' if package.installed else 'no'}",
        ]
        if package.gui:
            flags.append("GUI")
        if package.x11_required:
            flags.append("X11 required")
        return " / ".join(flags)
