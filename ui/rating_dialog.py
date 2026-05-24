from __future__ import annotations

from PyQt5.QtWidgets import QMessageBox, QWidget


def show_rating_placeholder(parent: QWidget) -> None:
    QMessageBox.information(
        parent,
        "Rating",
        "Rating submission will be added after the metadata contribution flow is defined.",
    )
