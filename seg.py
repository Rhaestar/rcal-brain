import itk

brain_file = "Data/brats.mha"
#Saving to a file as itk/vtk interaction is broken
output_file = "Data/seg.mha"

#ITK

#Input handling
fileNameFormat = output_file + "-%d" + ".png"

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
radiusValue = 2
StructuringElementType = itk.FlatStructuringElement[Dimension]
structuringElement = StructuringElementType.Ball(radiusValue)

ErodeFilterType = itk.BinaryMorphologicalOpeningImageFilter[RescaleImageType,
                                             RescaleImageType,
                                             StructuringElementType]
openingFilter = ErodeFilterType.New()
openingFilter.SetInput(thresholdFilter.GetOutput())
openingFilter.SetKernel(structuringElement)
openingFilter.SetForegroundValue(255)
openingFilter.SetBackgroundValue(0)
openingFilter.Update()

ErodeFilterType = itk.BinaryMorphologicalClosingImageFilter[RescaleImageType,
                                             RescaleImageType,
                                             StructuringElementType]
closingFilter = ErodeFilterType.New()
closingFilter.SetInput(openingFilter.GetOutput())
closingFilter.SetKernel(structuringElement)
closingFilter.SetForegroundValue(255)
closingFilter.Update()

CCImageType = itk.Image[itk.US, Dimension]

CCImageFilterType = itk.ConnectedComponentImageFilter[RescaleImageType, CCImageType]
CCImageFilter = CCImageFilterType.New()
CCImageFilter.SetInput(closingFilter.GetOutput())
CCImageFilter.Update()

LabelFilterType = itk.LabelShapeKeepNObjectsImageFilter[CCImageType]
LabelFilter = LabelFilterType.New()
LabelFilter.SetInput(CCImageFilter.GetOutput())
LabelFilter.SetBackgroundValue(0)
LabelFilter.SetNumberOfObjects(1)
LabelFilter.SetAttribute("NumberOfPixels")
LabelFilter.Update()

OutputFilterType = itk.RescaleIntensityImageFilter[CCImageType, RescaleImageType]
OutputFilter = OutputFilterType.New()
OutputFilter.SetOutputMinimum(0)
OutputFilter.SetOutputMaximum(255)
OutputFilter.SetInput(LabelFilter.GetOutput())
OutputFilter.Update()

#Save as mha
WriterMHA = itk.ImageFileWriter[RescaleImageType]
writer = WriterMHA.New()
writer.SetInput(OutputFilter.GetOutput())
writer.SetFileName(output_file)
writer.Update()