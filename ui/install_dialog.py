from __future__ import annotations

from PyQt5.QtCore import QProcess, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class InstallDialog(QDialog):
    def __init__(self, parent: QWidget, action: str, command: list[str]) -> None:
        super().__init__(parent)
        self.action = action
        self.command = command
        self.success = False
        self.process = QProcess(self)

        self.setWindowTitle(action)
        self.setMinimumSize(680, 420)

        layout = QVBoxLayout(self)

        title = QLabel(f"{action}: {' '.join(command)}")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output, 1)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.button(QDialogButtonBox.Close).setEnabled(False)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._finished)

        QTimer.singleShot(0, self._start)

    def _start(self) -> None:
        self._append(f"$ {' '.join(self.command)}\n")
        self.process.start(self.command[0], self.command[1:])

    def _read_stdout(self) -> None:
        self._append(bytes(self.process.readAllStandardOutput()).decode(errors="replace"))

    def _read_stderr(self) -> None:
        self._append(bytes(self.process.readAllStandardError()).decode(errors="replace"))

    def _finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self.success = exit_code == 0 and exit_status == QProcess.NormalExit
        status = "finished" if self.success else f"failed with exit code {exit_code}"
        self._append(f"\n{self.action} {status}.\n")
        self.buttons.button(QDialogButtonBox.Close).setEnabled(True)

    def _append(self, text: str) -> None:
        self.output.moveCursor(QTextCursor.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QTextCursor.End)


def run_pkg_command(parent: QWidget, action: str, command: list[str]) -> bool:
    dialog = InstallDialog(parent, action, command)
    dialog.exec_()
    return dialog.success
