import vtk
import itk

brain_file = "Data/brats.mha"
#Saving to a file as itk/vtk interaction is broken
temp_file = "Data/seg.mha"

#ITK


#Input handling
fileNameFormat = temp_file + "-%d" + ".png"

Dimension = 3
PixelType = itk.ctype('short')
InputImageType = itk.Image[PixelType, Dimension]

reader = itk.ImageFileReader[InputImageType].New()
reader.SetFileName(brain_file)
reader.Update()
inputImage = reader.GetOutput()

extractFilter = itk.ExtractImageFilter.New(inputImage)
extractFilter.SetDirectionCollapseToSubmatrix()

OutputPixelType = itk.UC
RescaleImageType = itk.Image[OutputPixelType, Dimension]

#Otsu thresholding
thresholdFilter = itk.OtsuMultipleThresholdsImageFilter[
        InputImageType,
        InputImageType].New()
thresholdFilter.SetInput(reader.GetOutput())
thresholdFilter.SetNumberOfThresholds(2)
thresholdFilter.Update()

rescaler = itk.RescaleIntensityImageFilter[InputImageType, RescaleImageType].New()
rescaler.SetInput(thresholdFilter.GetOutput())
rescaler.SetOutputMinimum(0)
rescaler.SetOutputMaximum(255)
rescaler.UpdateLargestPossibleRegion()

thresholdFilter = itk.BinaryThresholdImageFilter[RescaleImageType, RescaleImageType].New()

thresholdFilter.SetInput(rescaler.GetOutput())
thresholdFilter.SetLowerThreshold(128)
thresholdFilter.SetUpperThreshold(255)
thresholdFilter.SetOutsideValue(0)
thresholdFilter.SetInsideValue(255)

#Fill holes
#fillFilter = itk.BinaryFillholeImageFilter[RescaleImageType].New()
#fillFilter.SetInput(thresholdFilter


region = reader.GetOutput().GetLargestPossibleRegion()
size = region.GetSize()


#Save all slices as png for manual inspection
fnames = itk.NumericSeriesFileNames.New()
fnames.SetStartIndex(0)
fnames.SetEndIndex(size[2] - 1)
fnames.SetIncrementIndex(1)
fnames.SetSeriesFormat(fileNameFormat)

OutputImageType = itk.Image[OutputPixelType, 2]

WriterType = itk.ImageSeriesWriter[RescaleImageType, OutputImageType]
writer = WriterType.New()
writer.SetInput(thresholdFilter.GetOutput())
writer.SetFileNames(fnames.GetFileNames())

writer.Update()




#VTK Visualization
"""
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

interactor.Start()"""
