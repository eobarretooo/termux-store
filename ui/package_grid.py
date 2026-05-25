from __future__ import annotations

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QListView, QListWidget, QListWidgetItem

from core.package import Package
from ui.package_card import CARD_HEIGHT, PackageCard


_CARD_SPACING = 6
_CELL_HEIGHT = CARD_HEIGHT + _CARD_SPACING


class PackageGrid(QListWidget):
    """Vertical list of PackageCard rows, Mint Software Manager style."""

    package_selected = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._packages: list[Package] = []
        self.setAlternatingRowColors(False)
        self.setViewMode(QListView.ListMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setWrapping(False)
        self.setSpacing(3)
        self.setUniformItemSizes(True)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.itemDoubleClicked.connect(self._emit_package)

    def set_packages(self, packages: list[Package]) -> None:
        self.clear()
        self._packages = packages

        for package in packages:
            card = PackageCard(package)
            card.activated.connect(self.package_selected.emit)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, _CELL_HEIGHT))
            item.setData(Qt.UserRole, package)
            self.addItem(item)
            self.setItemWidget(item, card)

    def _emit_package(self, item: QListWidgetItem) -> None:
        package = item.data(Qt.UserRole)
        if package is not None:
            self.package_selected.emit(package)
