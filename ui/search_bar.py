from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget


class SearchBar(QWidget):
    """Search bar styled like GNOME Software — icon + input in a single pill."""

    search_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("searchContainer")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(0)

        icon = QLabel("⌕")
        icon.setObjectName("searchIcon")
        layout.addWidget(icon)

        self._input = QLineEdit()
        self._input.setObjectName("searchBar")
        self._input.setPlaceholderText("Search packages…")
        self._input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self._input, 1)

    # ── Public API ────────────────────────────────────────────────

    def text(self) -> str:
        return self._input.text()

    def clear(self) -> None:
        self._input.clear()
