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
        self.setMinimumHeight(80)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setObjectName("categoryTileIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(42, 42)
        layout.addWidget(icon_label)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(4)

        title = QLabel(label)
        title.setObjectName("categoryTileTitle")
        copy.addWidget(title)

        noun = "package" if count == 1 else "packages"
        subtitle = QLabel(f"{count} {noun}")
        subtitle.setObjectName("categoryTileCount")
        copy.addWidget(subtitle)

        layout.addLayout(copy, 1)

        arrow = QLabel(">")
        arrow.setObjectName("packageMeta")
        arrow.setStyleSheet("font-size: 18px;")
        layout.addWidget(arrow, 0, Qt.AlignVCenter)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.category_id)
            event.accept()
            return
        super().mouseReleaseEvent(event)
