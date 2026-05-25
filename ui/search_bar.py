from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit


class SearchBar(QLineEdit):
    search_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("searchBar")
        self.setMinimumHeight(42)
        self.setPlaceholderText("Search packages")
        self.setStyleSheet(
            """
            QLineEdit#searchBar {
                background: #151c21;
                color: #f4f0e8;
                border: 1px solid #2a3841;
                border-radius: 12px;
                padding: 0 14px;
                font-size: 15px;
            }
            QLineEdit#searchBar:focus {
                border-color: #e8a93a;
            }
            """
        )
        self.textChanged.connect(self.search_changed.emit)
