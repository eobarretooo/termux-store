from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.categories import CATEGORIES


_ICONS: dict[str, str] = {
    "all": "*  ",
    "development": "/  ",
    "terminal": ">  ",
    "multimedia": "~  ",
    "network": "@  ",
    "utilities": "=  ",
    "security": "!  ",
    "graphics": "&  ",
    "productivity": ".  ",
    "games": "+  ",
    "desktop": "WM ",
    "fonts": "Aa ",
}


class Sidebar(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(200)

        self._buttons: dict[str, QPushButton] = {}
        self._active_id = "all"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 18, 10, 14)
        layout.setSpacing(2)

        section = QLabel("CATEGORIES")
        section.setObjectName("sidebarSection")
        layout.addWidget(section)
        layout.addSpacing(4)

        for category_id, label in CATEGORIES:
            icon = _ICONS.get(category_id, "")
            button = QPushButton(f"{icon}{label}")
            button.setProperty("active", False)
            button.clicked.connect(
                lambda _checked=False, cid=category_id: self._select(cid)
            )
            layout.addWidget(button)
            self._buttons[category_id] = button

        layout.addStretch(1)

        first_id = CATEGORIES[0][0] if CATEGORIES else "all"
        self._active_id = first_id
        self._refresh_button_states()

    def _select(self, category_id: str) -> None:
        if category_id == self._active_id:
            return
        self._active_id = category_id
        self._refresh_button_states()
        self.category_selected.emit(category_id)

    def _refresh_button_states(self) -> None:
        for category_id, button in self._buttons.items():
            is_active = category_id == self._active_id
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)
