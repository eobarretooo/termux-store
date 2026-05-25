from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.categories import CATEGORIES


class Sidebar(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(190)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(8)

        title = QLabel("Termux Store")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)

        for category_id, label in CATEGORIES:
            button = QPushButton(label)
            button.setProperty("category", category_id)
            button.clicked.connect(
                lambda checked=False, value=category_id: self.category_selected.emit(value)
            )
            layout.addWidget(button)

        layout.addStretch(1)
        self.setStyleSheet(
            """
            QWidget#sidebar {
                background: #0b0f12;
                border-right: 1px solid #263038;
            }
            QLabel#sidebarTitle {
                color: #f2c66d;
                font-size: 18px;
                font-weight: 800;
                padding: 0 0 12px 2px;
            }
            QPushButton {
                background: transparent;
                color: #cbd4d8;
                border: 0;
                border-radius: 9px;
                padding: 10px 12px;
                text-align: left;
            }
            QPushButton:hover {
                background: #1a252b;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: #26343c;
            }
            """
        )
