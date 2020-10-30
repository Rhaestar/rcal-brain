import vtk

reader = vtk.vtkMetaImageReader()
reader.SetFileName('Data/brats.mha')
reader.Update()

reader2 = vtk.vtkMetaImageReader()
reader2.SetFileName('Data/seg.mha')
reader2.Update()

opacity_transfer_function = vtk.vtkPiecewiseFunction()
opacity_transfer_function.AddPoint(0.0, 0.0)
opacity_transfer_function.AddPoint(90, 0.0)
opacity_transfer_function.AddPoint(100, 0.2)
opacity_transfer_function.AddPoint(120, 0.0)

#Render brain as wireframe
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
actor.GetProperty().SetOpacity(0.25);

#Render tumor
marchingCubes2 = vtk.vtkMarchingCubes()
marchingCubes2.SetInputConnection(reader2.GetOutputPort())
marchingCubes2.SetValue(0, 135)
marchingCubes2.ComputeNormalsOn()
marchingCubes2.Update()

polyMapper2 = vtk.vtkPolyDataMapper()
polyMapper2.SetInputConnection(marchingCubes2.GetOutputPort())
polyMapper2.SetScalarVisibility(0)
polyMapper2.Update()

colors = vtk.vtkNamedColors()
actor2 = vtk.vtkActor()
actor2.SetMapper(polyMapper2)
actor2.GetProperty().SetDiffuseColor(colors.GetColor3d("Tomato"))

renderer = vtk.vtkRenderer()
renderer.SetBackground(0.5, 0.5, 0.5)
renderer.ResetCamera()
renderer.AddActor(actor)
renderer.AddActor(actor2)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.SetRenderWindow(window)

window.Render()

interactor.Start()
