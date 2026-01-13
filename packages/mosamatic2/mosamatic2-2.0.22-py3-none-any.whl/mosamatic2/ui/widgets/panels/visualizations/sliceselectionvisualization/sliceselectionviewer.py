import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QScrollArea, QGridLayout
from PySide6.QtCore import Qt, Signal, QSize
from mosamatic2.ui.widgets.panels.visualizations.sliceselectionvisualization.slicetile import SliceTile
from mosamatic2.ui.widgets.panels.visualizations.sliceselectionvisualization.slicetile import SliceItem

# https://chatgpt.com/c/69494292-b8fc-8327-863f-438838247bd4


class SliceSelectionViewer(QWidget):
    selection_changed = Signal()

    def __init__(self, columns: int = 4, tile_size: QSize = QSize(220, 220), parent=None):
        super(SliceSelectionViewer, self).__init__()
        self._columns = columns
        self._tile_size = tile_size
        self._tiles: list[SliceTile] = []
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setContentsMargins(10, 10, 10, 10)
        self._grid.setSpacing(10)
        self._scroll_area.setWidget(self._container)
        self._root = QVBoxLayout(self)
        self._root.addWidget(self._scroll_area)

    def clear(self):
        # remove widgets from layout
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        self._tiles.clear()

    def load_images(self, images_dir):
        images = []
        for f in os.listdir(images_dir):
            if f.endswith('_sagittal.png'):
                f_path = os.path.join(images_dir, f)
                images.append(f_path)
        self.clear()
        for i, p in enumerate(images):
            tile = SliceTile(SliceItem(p), self._tile_size)
            tile.toggled.connect(self._on_tile_toggled)
            self._tiles.append(tile)
            r, c = divmod(i, self._columns)
            self._grid.addWidget(tile, r, c)
        # Optional: keep grid left-aligned by adding stretch
        self._grid.setColumnStretch(self._columns, 1)

    def selected_paths(self) -> list[str]:
        return [t.item.path for t in self._tiles if t.is_checked()]
    
    def set_all_checked(self, checked: bool):
        for t in self._tiles:
            t.set_checked(checked)

    def _on_tile_toggled(self, _path: str, _checked: bool):
        self.selection_changed.emit()