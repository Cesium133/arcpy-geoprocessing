'''
This script uses the arcpy mapping module to edit and adjust elements within a single map document. Use later for use 
with multiple gemstones in multiple provinces

Geology and Tourmaline in Nuristan
'''

import arcpy
arcpy.env.overwriteOutput = True

mxd = arcpy.mapping.MapDocument(r"C:\sample_mapping.mxd")

# list data frames
mainFrame = arcpy.mapping.ListDataFrames(mxd)[0]
insetFrame = arcpy.mapping.ListDataFrames(mxd)[1]


# Layer files
asianBndy = arcpy.mapping.Layer(r"C:\arcpyMappingProject\AsiaBoundaries.lyr")
afghanBndy = arcpy.mapping.Layer(r"C:\CountryBoundary.lyr")
tourmaline = arcpy.mapping.Layer(r"C:\New Gemstone Layer Files\tourmaline.lyr")
nuristanGeol = arcpy.mapping.Layer(r"C:\Geology layer files\Nuristan_geology.lyr")
nuristanBndy = arcpy.mapping.Layer(r"C:\Province boundaries\Province.gdb\Nuristan")

# reference layers to update other layers with
# afgGeol = arcpy.mapping.Layer(r"C:\arcpyMappingProject\afgeolmap.lyr")
refProvince = arcpy.mapping.Layer(r"C:\arcpyMappingProject\refProvince.lyr")

# add to 1st data frame
# asian countries boundary, country boundary, province geology layer, gemstone layer

arcpy.mapping.AddLayer(mainFrame, asianBndy, "BOTTOM")
arcpy.mapping.AddLayer(mainFrame, afghanBndy)  # auto-arrange
arcpy.mapping.AddLayer(mainFrame, nuristanGeol)
arcpy.mapping.AddLayer(mainFrame, tourmaline)

# add to second data frame
# asian countries boundary, country boundary, province boundary layer
arcpy.mapping.AddLayer(insetFrame, asianBndy, "BOTTOM")
arcpy.mapping.AddLayer(insetFrame, afghanBndy)
arcpy.mapping.AddLayer(insetFrame, nuristanBndy)

lyrlist = arcpy.mapping.ListLayers(mxd)

# Adjust the inset data frame size
insetFrame.elementHeight, insetFrame.elementWidth = 3, 3

# Adjust the position of the inset data frame size
insetFrame.elementPositionX, insetFrame.elementPositionY = 4.5, 0.7

# list layers according to data frame in which they appear
ProvinceLyrList = arcpy.mapping.ListLayers(mxd, "", mainFrame)  # layers in 1st data frame: main data frame
CountryInsetLyrList = arcpy.mapping.ListLayers(mxd, "", insetFrame)  # layers in 2nd data frame: inset


# Choose extents of data frames
# Select features in inset data frame and zoom to them
where = "\"COUNTRY\" = 'Afghanistan'"
arcpy.SelectLayerByAttribute_management(CountryInsetLyrList[2], "", where)
insetFrame.zoomToSelectedFeatures()
arcpy.SelectLayerByAttribute_management(CountryInsetLyrList[2], "CLEAR_SELECTION")

#select features in main data frame and zoom to them
where = "\"ADM1_EN\" = 'Nuristan'"
arcpy.SelectLayerByAttribute_management(ProvinceLyrList[2], "", where)
mainFrame.zoomToSelectedFeatures()
arcpy.SelectLayerByAttribute_management(ProvinceLyrList[2], "CLEAR_SELECTION")

# define layers for UpdateLayer method
# nuristan boundary layer object
nuristan_bndy = CountryInsetLyrList[0]

# Hide labels for province names in inset frame
country = CountryInsetLyrList[1]
country.showLabels = False

# Update symbology of layers in each data frame according to reference layers DOESNT WORK YET
arcpy.mapping.UpdateLayer(insetFrame, nuristan_bndy, refProvince)  # update the province layer symbology in the 2nd data frame

print("Printing names of layers: ")
for i in lyrlist:
    print i.name

print("Printing names and types of layout elements: ")
for elem in arcpy.mapping.ListLayoutElements(mxd):
    print elem.name + " " + elem.type

for elem in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
    elem.text = "Tourmaline and Geology Map of Nuristan, Afghanistan"

mxd.saveACopy(r"C:\nuristanExport.mxd")
print("Saved Map Document")

out_jpeg = r"C:\nuristanTourmaline.jpeg"
print("Exporting to JPEG....")
arcpy.mapping.ExportToJPEG(mxd, out_jpeg)

print("Done!")
