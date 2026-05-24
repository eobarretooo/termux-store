from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from core.package import Package


class PackageGrid(QListWidget):
    package_selected = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._packages: list[Package] = []
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
            item = QListWidgetItem(f"{package.name}{suffix}\n{package.description}")
            item.setData(Qt.UserRole, package)
            self.addItem(item)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
