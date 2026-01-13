import os
from PySide6.QtWidgets import (
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QFileDialog,
)
from mosamatic2.ui.widgets.panels.visualizations.visualization import Visualization
from mosamatic2.ui.widgets.panels.visualizations.liversegmentvisualization.liversegmentviewer import LiverSegmentViewer
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.ui.settings import Settings
from mosamatic2.ui.utils import is_macos

LOG = LogManager()
PANEL_TITLE = 'LiverSegmentVisualization'
PANEL_NAME = 'liversegmentvisualization'


class LiverSegmentVisualization(Visualization):
    def __init__(self):
        super(LiverSegmentVisualization, self).__init__()
        self.set_title(PANEL_TITLE)
        self._liver_segment_actors = {}
        self._liver_volumes = {}
        self._liver_segments_dir_line_edit = None
        self._liver_segments_dir_select_button = None
        self._liver_volumes_file_line_edit = None
        self._liver_volumes_file_select_button = None
        self._load_liver_data_button = None
        self._liver_segment_viewer = None
        self._form_layout = None
        self._settings = None
        self.init_layout()

    def liver_segments_dir_line_edit(self):
        if not self._liver_segments_dir_line_edit:
            self._liver_segments_dir_line_edit = QLineEdit(self.settings().get(f'{PANEL_NAME}/liver_segments_dir'))
        return self._liver_segments_dir_line_edit
    
    def liver_segments_dir_select_button(self):
        if not self._liver_segments_dir_select_button:
            self._liver_segments_dir_select_button = QPushButton('Select directory')
            self._liver_segments_dir_select_button.clicked.connect(self.handle_liver_segments_dir_select_button)
        return self._liver_segments_dir_select_button
    
    def liver_volumes_file_line_edit(self):
        if not self._liver_volumes_file_line_edit:
            self._liver_volumes_file_line_edit = QLineEdit(self.settings().get(f'{PANEL_NAME}/liver_volumes_file'))
        return self._liver_volumes_file_line_edit
    
    def liver_volumes_file_select_button(self):
        if not self._liver_volumes_file_select_button:
            self._liver_volumes_file_select_button = QPushButton('Select file')
            self._liver_volumes_file_select_button.clicked.connect(self.handle_liver_volumes_file_select_button)
        return self._liver_volumes_file_select_button
    
    def load_liver_data_button(self):
        if not self._load_liver_data_button:
            self._load_liver_data_button = QPushButton('Load')
            self._load_liver_data_button.clicked.connect(self.handle_load_liver_data_button)
        return self._load_liver_data_button    
    
    def liver_segment_viewer(self):
        if not self._liver_segment_viewer:
            self._liver_segment_viewer = LiverSegmentViewer()
        return self._liver_segment_viewer
    
    def form_layout(self):
        if not self._form_layout:
            self._form_layout = QFormLayout()
            if is_macos():
                self._form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        return self._form_layout

    def settings(self):
        if not self._settings:
            self._settings = Settings()
        return self._settings

    def init_layout(self):
        liver_segments_layout = QHBoxLayout()
        liver_segments_layout.addWidget(self.liver_segments_dir_line_edit())
        liver_segments_layout.addWidget(self.liver_segments_dir_select_button())
        self.form_layout().addRow('Liver segments directory', liver_segments_layout)
        liver_volumes_layout = QHBoxLayout()
        liver_volumes_layout.addWidget(self.liver_volumes_file_line_edit())
        liver_volumes_layout.addWidget(self.liver_volumes_file_select_button())
        self.form_layout().addRow('Liver volumes file', liver_volumes_layout)
        layout = QVBoxLayout()
        layout.addLayout(self.form_layout())
        layout.addWidget(self.load_liver_data_button())
        layout.addWidget(self.liver_segment_viewer())
        self.setLayout(layout)
        self.setObjectName(PANEL_NAME)

    def handle_liver_segments_dir_select_button(self):
        last_directory = self.settings().get('last_directory')
        dir_path = QFileDialog.getExistingDirectory(dir=last_directory)
        if dir_path:
            self.liver_segments_dir_line_edit().setText(dir_path)
            self.settings().set('last_directory', dir_path)

    def handle_liver_volumes_file_select_button(self):
        last_directory = self.settings().get('last_directory')
        file_path, _ = QFileDialog.getOpenFileName(dir=last_directory)
        if file_path:
            self.liver_volumes_file_line_edit().setText(file_path)
            self.settings().set('last_directory', os.path.dirname(file_path))

    def handle_load_liver_data_button(self):
        self.liver_segment_viewer().load_segments_and_volumes(
            liver_segments_dir=self.liver_segments_dir_line_edit().text(),
            liver_volumes_file=self.liver_volumes_file_line_edit().text(),
        )

    def save_inputs_and_parameters(self):
        self.settings().set(f'{PANEL_NAME}/liver_segments_dir', self.liver_segments_dir_line_edit().text())
        self.settings().set(f'{PANEL_NAME}/liver_volumes_file', self.liver_volumes_file_line_edit().text())