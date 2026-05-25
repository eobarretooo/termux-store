from __future__ import annotations

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QListView, QListWidget, QListWidgetItem

from core.package import Package
from ui.package_card import CARD_HEIGHT, CARD_WIDTH, PackageCard


GRID_CELL = QSize(CARD_WIDTH + 14, CARD_HEIGHT + 14)


class PackageGrid(QListWidget):
    package_selected = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._packages: list[Package] = []
        self.setAlternatingRowColors(False)
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setWrapping(True)
        self.setSpacing(8)
        self.setGridSize(GRID_CELL)
        self.setUniformItemSizes(False)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.itemDoubleClicked.connect(self._emit_package)

    def set_packages(self, packages: list[Package]) -> None:
        self.clear()
        self._packages = packages

        for package in packages:
            card = PackageCard(package)
            card.activated.connect(self.package_selected.emit)

            item = QListWidgetItem()
            item.setSizeHint(GRID_CELL)
            item.setData(Qt.UserRole, package)
            self.addItem(item)
            self.setItemWidget(item, card)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
