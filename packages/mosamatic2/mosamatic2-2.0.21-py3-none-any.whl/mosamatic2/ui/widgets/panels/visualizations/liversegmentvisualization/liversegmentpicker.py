import vtk


class LiverSegmentPicker:
    def __init__(self, renderer, interactor, actors, volumes, selected_volume_actor):
        self.ren = renderer
        self.iren = interactor
        self.actors = actors
        self.actor_keys = {v: k for k, v in actors.items()}
        self.volumes = volumes
        self.selected_volume_actor = selected_volume_actor
        self.selected = set()
        self._orig = {}
        self._opacity_selected = 1.0
        self._opacity_not_selected = 0.25

        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.001)

        # Use trackball so it rotates only when you move
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(self.style)

        # Hook events
        self.iren.AddObserver("LeftButtonPressEvent", self.on_left_down)
        self.iren.AddObserver("LeftButtonReleaseEvent", self.on_left_up)

        self._allow_camera_drag = True

    def _save(self, a):
        if a in self._orig:
            return

    def _highlight(self, a, on):
        self._save(a)
        p = a.GetProperty()
        if on:
            p.SetOpacity(self._opacity_selected)
        else:
            p.SetOpacity(self._opacity_not_selected)

    def clear(self):
        for a in list(self.selected):
            self._highlight(a, False)
        self.selected.clear()

    def toggle(self, a):
        if a in self.selected:
            self._highlight(a, False)
            self.selected.remove(a)
        else:
            self._highlight(a, True)
            self.selected.add(a)
        total_selected_volume = 0
        for a in self.selected:
            a_key = self.actor_keys[a]
            volume = int(self.volumes[a_key])
            total_selected_volume += volume
        self.selected_volume_actor.SetInput(f'Selected volume: {total_selected_volume} mL')
            

    def on_left_down(self, iren, evt):
        x, y = iren.GetEventPosition()

        # Only do picking when Shift or Ctrl is held.
        do_pick = (iren.GetShiftKey() or iren.GetControlKey())

        if do_pick:
            self.picker.Pick(x, y, 0, self.ren)
            a = self.picker.GetActor()
            a_key = self.actor_keys[a]

            if a in self.actors.values():
                # Additive (Shift/Ctrl): toggle selection
                self.toggle(a)
            else:
                # Shift/Ctrl + empty click: clear selection (optional)
                self.clear()

            iren.GetRenderWindow().Render()
            self._allow_camera_drag = False  # don't also start a camera drag
            return

        # No modifier => normal rotate/pan/zoom interaction
        self._allow_camera_drag = True
        self.style.OnLeftButtonDown()

    def on_left_up(self, iren, evt):
        if self._allow_camera_drag:
            self.style.OnLeftButtonUp()

    def set_opacity_selected(self, opacity_selected):
        self._opacity_selected = opacity_selected

    def set_opacity_not_selected(self, opacity_not_selected):
        self._opacity_not_selected = opacity_not_selected
