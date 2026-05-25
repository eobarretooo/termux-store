from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from core.categories import CATEGORIES


_ICONS: dict[str, str] = {
    "all": "HOME",
    "installed": "OK",
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

_PRIMARY = {"all", "installed"}


class Sidebar(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        self._buttons: dict[str, QPushButton] = {}
        self._active_id = "all"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 14, 0, 14)
        layout.setSpacing(0)

        self._add_section_label(layout, "BROWSE")
        for category_id, label in CATEGORIES:
            if category_id in _PRIMARY:
                self._add_button(layout, category_id, label)

        divider = QFrame()
        divider.setObjectName("sidebarDivider")
        divider.setFrameShape(QFrame.HLine)
        layout.addSpacing(6)
        layout.addWidget(divider)
        layout.addSpacing(6)

        self._add_section_label(layout, "CATEGORIES")
        for category_id, label in CATEGORIES:
            if category_id not in _PRIMARY:
                self._add_button(layout, category_id, label)

        layout.addStretch(1)

        self._active_id = CATEGORIES[0][0] if CATEGORIES else "all"
        self._refresh_button_states()

    def _add_section_label(self, layout: QVBoxLayout, text: str) -> None:
        label = QLabel(text)
        label.setObjectName("sidebarSection")
        layout.addWidget(label)

    def _add_button(self, layout: QVBoxLayout, category_id: str, label: str) -> None:
        icon = _ICONS.get(category_id, "PKG")
        button = QPushButton(f"  {icon:<4} {label}")
        button.setProperty("active", False)
        button.clicked.connect(
            lambda _checked=False, cid=category_id: self._select(cid)
        )
        layout.addWidget(button)
        self._buttons[category_id] = button

    def _select(self, category_id: str) -> None:
        if category_id == self._active_id:
            return
        self.set_active(category_id)
        self.category_selected.emit(category_id)

    def set_active(self, category_id: str) -> None:
        if category_id not in self._buttons:
            return
        self._active_id = category_id
        self._refresh_button_states()

    def _refresh_button_states(self) -> None:
        for category_id, button in self._buttons.items():
            is_active = category_id == self._active_id
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)
