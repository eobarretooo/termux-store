from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.package import Package
from core.pkg_manager import PkgManager
from ui.install_dialog import show_command_result
from ui.rating_dialog import show_rating_placeholder


class PackageDetailDialog(QDialog):
    def __init__(self, package: Package, pkg_manager: PkgManager, parent=None) -> None:
        super().__init__(parent)
        self.package = package
        self.pkg_manager = pkg_manager

        self.setWindowTitle(package.name)
        self.setMinimumSize(520, 420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<h2>{package.name}</h2>"))
        layout.addWidget(QLabel(self._summary()))

        description = QTextEdit()
        description.setReadOnly(True)
        description.setPlainText(package.display_description)
        layout.addWidget(description)

        install_button = QPushButton("Install")
        install_button.clicked.connect(self._install)
        layout.addWidget(install_button)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self._remove)
        layout.addWidget(remove_button)

        rating_button = QPushButton("Rate compatibility")
        rating_button.clicked.connect(lambda: show_rating_placeholder(self))
        layout.addWidget(rating_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _summary(self) -> str:
        flags = [
            f"Category: {self.package.category}",
            f"Version: {self.package.version or 'unknown'}",
            f"Installed: {'yes' if self.package.installed else 'no'}",
            f"GUI: {'yes' if self.package.gui else 'no'}",
            f"X11 required: {'yes' if self.package.x11_required else 'no'}",
        ]
        return "<br>".join(flags)

    def _install(self) -> None:
        success, output = self.pkg_manager.install(self.package.name)
        show_command_result(self, success, "Install", output)

    def _remove(self) -> None:
        success, output = self.pkg_manager.remove(self.package.name)
        show_command_result(self, success, "Remove", output)
