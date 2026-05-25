from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class CategoryTile(QFrame):
    selected = pyqtSignal(str)

    def __init__(self, category_id: str, label: str, count: int, icon: str) -> None:
        super().__init__()
        self.category_id = category_id
        self.setObjectName("categoryTile")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(74)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setObjectName("categoryTileIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(38, 38)
        layout.addWidget(icon_label)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(3)

        title = QLabel(label)
        title.setObjectName("categoryTileTitle")
        copy.addWidget(title)

        noun = "package" if count == 1 else "packages"
        subtitle = QLabel(f"{count} {noun}")
        subtitle.setObjectName("categoryTileCount")
        copy.addWidget(subtitle)

        layout.addLayout(copy, 1)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.category_id)
            event.accept()
            return
        super().mouseReleaseEvent(event)
