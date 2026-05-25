from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.package import Package
from core.pkg_manager import PkgManager
from ui.install_dialog import run_pkg_command
from ui.rating_dialog import show_rating_placeholder


class PackageDetailDialog(QDialog):
    def __init__(self, package: Package, pkg_manager: PkgManager, parent=None) -> None:
        super().__init__(parent)
        self.package = package
        self.pkg_manager = pkg_manager

        self.setWindowTitle(package.name)
        self.setMinimumSize(640, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        header = QHBoxLayout()
        header.setSpacing(16)
        header.addWidget(self._icon_label())

        title_box = QVBoxLayout()
        title = QLabel(package.name)
        title.setObjectName("dialogTitle")
        title_box.addWidget(title)

        version = QLabel(self._summary())
        version.setObjectName("dialogVersion")
        title_box.addWidget(version)
        title_box.addStretch(1)
        header.addLayout(title_box, 1)
        layout.addLayout(header)

        description = QTextEdit()
        description.setReadOnly(True)
        description.setPlainText(package.display_description)
        layout.addWidget(description, 1)

        self.action_button = QPushButton()
        self._refresh_action_button()
        self.action_button.clicked.connect(self._run_action)
        layout.addWidget(self.action_button)

        rating_button = QPushButton("Rate compatibility")
        rating_button.clicked.connect(lambda: show_rating_placeholder(self))
        layout.addWidget(rating_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _icon_label(self) -> QLabel:
        label = QLabel()
        label.setFixedSize(96, 96)
        label.setAlignment(Qt.AlignCenter)

        if self.package.icon_path and Path(self.package.icon_path).exists():
            pixmap = QIcon(self.package.icon_path).pixmap(96, 96)
            if not pixmap.isNull():
                label.setPixmap(pixmap)
                return label

        label.setText((self.package.name[0] if self.package.name else "?").upper())
        label.setStyleSheet(
            "background: #1a1a2e;"
            "color: #39d353;"
            "border-radius: 24px;"
            "font-size: 42px;"
            "font-weight: 900;"
        )
        return label

    def _summary(self) -> str:
        flags = [
            f"Category: {self.package.category}",
            f"Version: {self.package.version or 'unknown'}",
            f"Installed: {'yes' if self.package.installed else 'no'}",
            f"GUI: {'yes' if self.package.gui else 'no'}",
            f"X11 required: {'yes' if self.package.x11_required else 'no'}",
        ]
        return " / ".join(flags)

    def _refresh_action_button(self) -> None:
        if self.package.installed:
            self.action_button.setText("Remove")
            self.action_button.setObjectName("removeButton")
        else:
            self.action_button.setText("Install")
            self.action_button.setObjectName("installButton")
        self.action_button.style().unpolish(self.action_button)
        self.action_button.style().polish(self.action_button)

    def _run_action(self) -> None:
        if self.package.installed:
            command = [self.pkg_manager.pkg_executable, "uninstall", "-y", self.package.name]
            if run_pkg_command(self, "Remove", command):
                self.package.installed = False
        else:
            command = [self.pkg_manager.pkg_executable, "install", "-y", self.package.name]
            if run_pkg_command(self, "Install", command):
                self.package.installed = True

        self._refresh_action_button()
