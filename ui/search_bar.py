from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget


class SearchBar(QWidget):
    """Search bar styled as a Mint-like toolbar field."""

    search_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("searchContainer")
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(0)

        icon = QLabel("Search")
        icon.setObjectName("searchIcon")
        layout.addWidget(icon)

        self._input = QLineEdit()
        self._input.setObjectName("searchBar")
        self._input.setPlaceholderText("Search apps and packages...")
        self._input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self._input, 1)

    def text(self) -> str:
        return self._input.text()

    def clear(self) -> None:
        self._input.clear()
