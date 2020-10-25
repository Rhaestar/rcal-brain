import vtk
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

region = reader.GetOutput().GetLargestPossibleRegion()
size = region.GetSize()

#Save as mha
WriterMHA = itk.ImageFileWriter[RescaleImageType]
writer = WriterMHA.New()
writer.SetInput(closingFilter.GetOutput())
writer.SetFileName(output_file)
writer.Update()

#Save all slices as png for manual inspection
fnames = itk.NumericSeriesFileNames.New()
fnames.SetStartIndex(0)
fnames.SetEndIndex(size[2] - 1)
fnames.SetIncrementIndex(1)
fnames.SetSeriesFormat(fileNameFormat)

OutputImageType = itk.Image[OutputPixelType, 2]

WriterType = itk.ImageSeriesWriter[RescaleImageType, OutputImageType]
writer = WriterType.New()
writer.SetInput(closingFilter.GetOutput())
writer.SetFileNames(fnames.GetFileNames())

writer.Update()
