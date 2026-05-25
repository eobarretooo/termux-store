from __future__ import annotations

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.categories import category_label
from core.package import Package


class PackageCard(QFrame):
    def __init__(self, package: Package) -> None:
        super().__init__()
        self.setObjectName("packageCard")
        self.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(7)

        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel(package.name)
        title.setObjectName("packageTitle")
        header.addWidget(title, 1)

        if package.installed:
            header.addWidget(self._pill("Installed", "installedPill"))
        if package.gui:
            header.addWidget(self._pill("GUI", "featurePill"))
        if package.x11_required:
            header.addWidget(self._pill("X11", "featurePill"))

        layout.addLayout(header)

        meta = QLabel(f"{category_label(package.category)}  |  {package.version or 'unknown version'}")
        meta.setObjectName("packageMeta")
        layout.addWidget(meta)

        description = QLabel(package.description or "No community description yet.")
        description.setObjectName("packageDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

    @staticmethod
    def _pill(text: str, object_name: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName(object_name)
        label.setAlignment(Qt.AlignCenter)
        return label


class PackageGrid(QListWidget):
    package_selected = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._packages: list[Package] = []
        self.setAlternatingRowColors(False)
        self.setSpacing(10)
        self.setUniformItemSizes(False)
        self.setStyleSheet(
            """
            QListWidget {
                background: #101417;
                border: 0;
                padding: 8px;
            }
            QListWidget::item {
                background: transparent;
                border: 0;
                margin: 0;
                padding: 0;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QFrame#packageCard {
                background: #182126;
                border: 1px solid #2d3a40;
                border-left: 4px solid #e8a93a;
                border-radius: 12px;
            }
            QLabel#packageTitle {
                color: #f7efe2;
                font-size: 17px;
                font-weight: 700;
            }
            QLabel#packageMeta {
                color: #b8c2c8;
                font-size: 12px;
            }
            QLabel#packageDescription {
                color: #e0e4e6;
                font-size: 13px;
            }
            QLabel#installedPill {
                background: #1f6f50;
                color: #effff7;
                border-radius: 9px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#featurePill {
                background: #2a3d52;
                color: #dbeeff;
                border-radius: 9px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 700;
            }
            """
        )
        self.itemDoubleClicked.connect(self._emit_package)

    def set_packages(self, packages: list[Package]) -> None:
        self.clear()
        self._packages = packages

        for package in packages:
            card = PackageCard(package)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 96))
            item.setData(Qt.UserRole, package)
            self.addItem(item)
            self.setItemWidget(item, card)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
