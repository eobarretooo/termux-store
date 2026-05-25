from __future__ import annotations

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from core.package import Package


class PackageGrid(QListWidget):
    package_selected = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._packages: list[Package] = []
        self.setAlternatingRowColors(True)
        self.setSpacing(8)
        self.setUniformItemSizes(False)
        self.setStyleSheet(
            """
            QListWidget {
                padding: 8px;
            }
            QListWidget::item {
                border: 1px solid #2d3b43;
                border-radius: 8px;
                padding: 10px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background: #29485a;
            }
            """
        )
        self.itemDoubleClicked.connect(self._emit_package)

    def set_packages(self, packages: list[Package]) -> None:
        self.clear()
        self._packages = packages

        for package in packages:
            flags = []
            if package.installed:
                flags.append("installed")
            if package.gui:
                flags.append("GUI")
            if package.x11_required:
                flags.append("X11")

            suffix = f" ({', '.join(flags)})" if flags else ""
            details = package.description or f"Version: {package.version or 'unknown'}"
            item = QListWidgetItem(f"{package.name}{suffix}\n{details}")
            item.setSizeHint(QSize(0, 64))
            item.setData(Qt.UserRole, package)
            self.addItem(item)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
