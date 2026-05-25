from __future__ import annotations

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QListView, QListWidget, QListWidgetItem

from core.package import Package
from ui.package_card import CARD_HEIGHT, CARD_WIDTH, PackageCard


GRID_CELL = QSize(CARD_WIDTH + 22, CARD_HEIGHT + 22)


class PackageGrid(QListWidget):
    package_selected = pyqtSignal(object)
    package_action_requested = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._packages: list[Package] = []
        self.setAlternatingRowColors(False)
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setWrapping(True)
        self.setSpacing(12)
        self.setGridSize(GRID_CELL)
        self.setUniformItemSizes(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.itemDoubleClicked.connect(self._emit_package)

    def set_packages(self, packages: list[Package]) -> None:
        self.clear()
        self._packages = packages

        for package in packages:
            card = PackageCard(package)
            card.action_requested.connect(self.package_action_requested.emit)
            item = QListWidgetItem()
            item.setSizeHint(GRID_CELL)
            item.setData(Qt.UserRole, package)
            self.addItem(item)
            self.setItemWidget(item, card)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
