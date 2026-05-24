from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from core.categories import CATEGORIES


class Sidebar(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        for category_id, label in CATEGORIES:
            button = QPushButton(label)
            button.setProperty("category", category_id)
            button.clicked.connect(
                lambda checked=False, value=category_id: self.category_selected.emit(value)
            )
            layout.addWidget(button)

        layout.addStretch(1)
