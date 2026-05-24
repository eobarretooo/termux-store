from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit


class SearchBar(QLineEdit):
    search_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setPlaceholderText("Search packages")
        self.textChanged.connect(self.search_changed.emit)
