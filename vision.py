import vtk

reader = vtk.vtkMetaImageReader()
reader.SetFileName('Data/brats.mha')
reader.Update()

polyMapper = vtk.vtkSmartVolumeMapper()
polyMapper.SetInputConnection(reader.GetOutputPort())

opacity_transfer_function = vtk.vtkPiecewiseFunction()
opacity_transfer_function.AddPoint(0.0, 0.0)
opacity_transfer_function.AddPoint(90, 0.0)
opacity_transfer_function.AddPoint(100, 0.2)
opacity_transfer_function.AddPoint(120, 0.0)

volume_property = vtk.vtkVolumeProperty()
volume_property.SetScalarOpacity(opacity_transfer_function)

actorVolume = vtk.vtkVolume()
actorVolume.SetMapper(polyMapper)
actorVolume.SetProperty(volume_property)

marchingCubes = vtk.vtkMarchingCubes()
marchingCubes.SetInputConnection(reader.GetOutputPort())
marchingCubes.SetValue(0, 135)
marchingCubes.ComputeNormalsOn()
marchingCubes.Update()


polyMapper = vtk.vtkPolyDataMapper()
polyMapper.SetInputConnection(marchingCubes.GetOutputPort())
polyMapper.SetScalarVisibility(0)
polyMapper.Update()

actor = vtk.vtkActor()
actor.SetMapper(polyMapper)
actor.GetProperty().SetRepresentationToWireframe()

renderer = vtk.vtkRenderer()
renderer.SetBackground(0.5, 0.5, 0.5)
renderer.ResetCamera()
renderer.AddActor(actor)
renderer.AddActor(actorVolume)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.SetRenderWindow(window)

window.Render()

interactor.Start()
