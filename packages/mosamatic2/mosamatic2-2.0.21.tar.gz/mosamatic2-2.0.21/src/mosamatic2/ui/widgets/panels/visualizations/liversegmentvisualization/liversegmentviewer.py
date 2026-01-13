import os
import vtk
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from mosamatic2.ui.widgets.panels.visualizations.liversegmentvisualization.liversegmentpicker import LiverSegmentPicker
from mosamatic2.core.managers.logmanager import LogManager

LOG = LogManager()
SEGMENT_COLORS = [
    (0.80, 0.25, 0.25),  # muted red
    (0.25, 0.55, 0.80),  # steel blue
    (0.30, 0.70, 0.45),  # green
    (0.85, 0.65, 0.25),  # amber
    (0.55, 0.40, 0.75),  # purple
    (0.90, 0.45, 0.15),  # orange
    (0.20, 0.75, 0.75),  # teal
    (0.75, 0.75, 0.30),  # olive
]

vtk.vtkObject.GlobalWarningDisplayOff()


class LiverSegmentViewer(QWidget):
    def __init__(self):
        super(LiverSegmentViewer, self).__init__()
        self._total_volume = 0.0
        self._selected_volume = 0.0
        self._liver_segment_actors = {}
        self._liver_volumes = {}
        self._vtk_widget = QVTKRenderWindowInteractor(self)
        self._render_window = self._vtk_widget.GetRenderWindow()
        self._interactor = self._render_window.GetInteractor()
        self._interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        layout = QVBoxLayout()
        layout.addWidget(self._vtk_widget)
        self.setLayout(layout)
        self._selected_volume_actor = vtk.vtkTextActor()
        self._selected_volume_actor.SetInput(f'Selected volume: {self._selected_volume} mL')
        self._selected_volume_actor.GetTextProperty().SetFontSize(18)
        self._selected_volume_actor.GetTextProperty().SetColor(1, 1, 1)  # RGB 0–1
        self._selected_volume_actor.SetDisplayPosition(20, 50)
        self._total_volume_actor = vtk.vtkTextActor()
        self._total_volume_actor.SetInput(f'Total volume: {self._total_volume} mL')
        self._total_volume_actor.GetTextProperty().SetFontSize(18)
        self._total_volume_actor.GetTextProperty().SetColor(1, 1, 1)  # RGB 0–1
        self._total_volume_actor.SetDisplayPosition(20, 20)
        self._renderer = vtk.vtkRenderer()
        self._renderer.AddViewProp(self._total_volume_actor)
        self._renderer.AddViewProp(self._selected_volume_actor)
        self._render_window.AddRenderer(self._renderer)
        self._render_window.Render()

    def image_to_surface(self, image: vtk.vtkImageData, label=1) -> vtk.vtkPolyData:
        dmc = vtk.vtkDiscreteMarchingCubes()
        dmc.SetInputData(image)
        dmc.SetValue(0, label)
        dmc.Update()
        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputConnection(dmc.GetOutputPort())
        cleaner.Update()
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputConnection(cleaner.GetOutputPort())
        smoother.SetNumberOfIterations(20)   # 10–30 typical
        smoother.SetPassBand(0.1)              # smaller = smoother (e.g. 0.05–0.2)
        smoother.SetFeatureAngle(120.0)      # preserve sharper edges
        smoother.BoundarySmoothingOff()              # usually best for closed organs
        smoother.FeatureEdgeSmoothingOff()           # keep features; turn On if you want more smoothing
        smoother.NonManifoldSmoothingOn()
        smoother.NormalizeCoordinatesOn()            # helps numerical stability
        smoother.Update()
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(smoother.GetOutputPort())
        normals.SetComputePointNormals(True)
        normals.SetComputeCellNormals(False)
        normals.SetAutoOrientNormals(True)
        normals.SetConsistency(True)
        normals.Update()
        return normals.GetOutput()

    def surface_to_actor(self, polydata: vtk.vtkPolyData) -> vtk.vtkActor:
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor
    
    def load_segments_and_volumes(self, liver_segments_dir, liver_volumes_file):
        # Load volumes
        df = pd.read_csv(liver_volumes_file, sep=';')
        for _, row in df.iterrows():
            self._liver_volumes[row['file']] = row['volume_mL']
        self._total_volume = sum(self._liver_volumes.values())
        self._total_volume_actor.SetInput(f'Total volume: {self._total_volume} mL')
        # Load liver segment actors
        i = 0
        for f in os.listdir(liver_segments_dir):
            segment_name = f
            f_path = os.path.join(liver_segments_dir, f)
            reader = vtk.vtkNIFTIImageReader()
            reader.SetFileName(f_path)
            reader.Update()
            image = reader.GetOutput()
            surface = self.image_to_surface(image)
            actor = self.surface_to_actor(surface)
            prop = actor.GetProperty()
            prop.SetSpecular(0.3)
            prop.SetSpecularPower(20)
            prop.SetDiffuse(0.7)
            prop.SetAmbient(0.1)
            prop.SetColor(*SEGMENT_COLORS[i])
            prop.SetOpacity(0.5)
            self._renderer.AddActor(actor)
            self._liver_segment_actors[segment_name] = actor
            i += 1
        picker = LiverSegmentPicker(
            self._renderer, 
            self._interactor, 
            self._liver_segment_actors, 
            self._liver_volumes, 
            self._selected_volume_actor,
        )
        self._renderer.SetBackground(0.1, 0.1, 0.12)
        self._renderer.ResetCamera()
        self._render_window.Render()
        self._interactor.Start()