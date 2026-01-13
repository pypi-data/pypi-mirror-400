import os
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QCheckBox, QVBoxLayout, QGridLayout,
    QScrollArea, QMainWindow, QFileDialog, QPushButton, QHBoxLayout
)


@dataclass(frozen=True)
class SliceItem:
    path: str


class SliceTile(QWidget):
    toggled = Signal(str, bool)  # path, checked

    def __init__(self, item: SliceItem, display_size: QSize, parent=None):
        super().__init__(parent)
        self.item = item
        self.display_size = display_size

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(display_size)
        self.image_label.setStyleSheet("QLabel { background: #222; border: 1px solid #444; }")

        dcm_name = os.path.basename(item.path)[:-13] + '.dcm'
        self.checkbox = QCheckBox(dcm_name)
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(self._on_toggled)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(self.image_label)
        layout.addWidget(self.checkbox)

        self._load_and_scale()

    def _load_and_scale(self):
        pix = QPixmap(self.item.path)
        if pix.isNull():
            self.image_label.setText("Failed to load")
            return

        scaled = pix.scaled(
            self.display_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

    def _on_toggled(self, checked: bool):
        self.toggled.emit(self.item.path, checked)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        self.checkbox.setChecked(checked)