from __future__ import annotations

from PyQt5.QtWidgets import QMessageBox, QWidget


def show_command_result(parent: QWidget, success: bool, action: str, output: str) -> None:
    icon = QMessageBox.Information if success else QMessageBox.Warning
    title = f"{action} finished" if success else f"{action} failed"
    message = output or "No command output."

    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(title)
    box.setDetailedText(message)
    box.exec_()
