from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
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

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("homeScroll")

        page = QWidget()
        page.setObjectName("detailPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 16)
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
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(20)

        self.icon = QLabel()
        self.icon.setObjectName("detailIcon")
        self.icon.setFixedSize(96, 96)
        self.icon.setAlignment(Qt.AlignCenter)
        header.addWidget(self.icon, 0, Qt.AlignTop)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(6)

        self.title = QLabel()
        self.title.setObjectName("detailTitle")
        copy.addWidget(self.title)

        self.summary = QLabel()
        self.summary.setObjectName("detailSummary")
        self.summary.setWordWrap(True)
        copy.addWidget(self.summary)

        self._badge_row = QHBoxLayout()
        self._badge_row.setContentsMargins(0, 4, 0, 0)
        self._badge_row.setSpacing(6)
        copy.addLayout(self._badge_row)

        copy.addStretch(1)
        header.addLayout(copy, 1)

        button_column = QVBoxLayout()
        button_column.setSpacing(8)

        self.action_button = QPushButton()
        self.action_button.clicked.connect(self._emit_action)
        button_column.addWidget(self.action_button)

        self.rating_button = QPushButton("Rate compatibility")
        self.rating_button.setObjectName("secondaryButton")
        self.rating_button.clicked.connect(lambda: show_rating_placeholder(self))
        button_column.addWidget(self.rating_button)
        button_column.addStretch(1)

        header.addLayout(button_column, 0)
        card_layout.addLayout(header)

        sep = QFrame()
        sep.setObjectName("detailSeparator")
        sep.setFrameShape(QFrame.HLine)
        card_layout.addWidget(sep)

        desc_label = QLabel("Description")
        desc_label.setObjectName("sectionTitle")
        desc_label.setStyleSheet("font-size: 14px; font-weight: 700;")
        card_layout.addWidget(desc_label)

        self.description = QTextEdit()
        self.description.setObjectName("detailDescription")
        self.description.setReadOnly(True)
        self.description.setMinimumHeight(140)
        card_layout.addWidget(self.description, 1)

        layout.addWidget(card, 1)
        scroll.setWidget(page)
        outer.addWidget(scroll, 1)

    def set_package(self, package: Package) -> None:
        self.package = package
        self.title.setText(package.name)
        self.summary.setText(package.description or package.short_fallback)
        self.description.setPlainText(package.display_description)
        self._set_icon(package)
        self._refresh_badges(package)
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

        letter = (package.name[0] if package.name else "?").upper()
        self.icon.setText(letter)
        self.icon.setStyleSheet(
            f"background: {icon_color(package.name)};"
            "border-radius: 18px;"
            "font-size: 40px;"
            "font-weight: 700;"
            "color: white;"
        )

    def _refresh_badges(self, package: Package) -> None:
        while self._badge_row.count():
            item = self._badge_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        badges: list[str] = [category_label(package.category)]
        if package.version:
            badges.append(package.version)
        if package.installed:
            badges.append("Installed")
        if package.gui:
            badges.append("GUI")
        if package.x11_required:
            badges.append("X11")

        for text in badges:
            pill = QLabel(text)
            pill.setObjectName("metaBadge")
            self._badge_row.addWidget(pill)

        self._badge_row.addStretch(1)

    def _refresh_action_button(self, package: Package) -> None:
        if package.installed:
            self.action_button.setText("Remove")
            self.action_button.setObjectName("removeButton")
        else:
            self.action_button.setText("Install")
            self.action_button.setObjectName("installButton")
        self.action_button.style().unpolish(self.action_button)
        self.action_button.style().polish(self.action_button)
