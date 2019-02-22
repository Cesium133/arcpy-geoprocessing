'''
This script uses the arcpy mapping module to edit and adjust elements within a single map document. Use later for use 
with multiple gemstones in multiple provinces

Geology and Tourmaline in Nuristan
'''

def main():
    import arcpy
    import os
    arcpy.env.overwriteOutput = True  # overwrite output

    def GemstoneInProvince():
        # input shapefile containing all gemstone feature classes (resulting layer after performing spatial join with Province
        # boundary layer)
        in_fc = r"C:\all_gemstones\join\gemstone_provinces.shp"
        # output shapefile for Sort_management to output
        fc = r"C:\all_gemstones\join\gemstone_provinces_sorted.shp"
        # Sort gemstone name in alphabetical order so that final list will be grouped by gemstone
        print("Sorting Master gemstone-province feature class in ascending order ")
        arcpy.Sort_management(in_fc,fc,[["Commodity1", 'ASCENDING']])
        print("Finished sorting ")
        fields = ["Commodity1", "ADM1_EN"] # Search Cursor reads through gemstone and province name fields
        gem_loc = []

        print("Searching through feature class attribute table for unique combinations of gemstones in provinces ")
        with arcpy.da.SearchCursor(fc, fields) as cursor:
            for row in cursor:
                if row not in gem_loc:  # don't add to gem_loc list if this gemstone is already in this province
                    gem_loc.append(row)
        # print gemstone-province pairs as strings
        # for i in gem_loc:
        #     print(' ... '.join(i))
        print("Finished compiling list of unique gemstone-province combinations")
        return gem_loc

    gemstonelist = GemstoneInProvince()


    def mapScript(gemstonelist):

        # define Map Document to start script with. This Map Doc should have a basic template with layout elements already
        # set
        print("Defined (Starter) Map Document ")
        mxd = arcpy.mapping.MapDocument(r"C:\arcpyMappingProject\starter_mapdoc.mxd")

        # List and define data frames
        print("Defined Data Frames ")
        mainFrame = arcpy.mapping.ListDataFrames(mxd)[0]
        insetFrame = arcpy.mapping.ListDataFrames(mxd)[1]

        # Layer files for Country and Asia
        print("Defined Asian Country Boundaries and Afghanistan Provinces Layers in starter Map Document")
        asianBndy = arcpy.mapping.Layer(r"C:\arcpyMappingProject\AsiaBoundaries.lyr")
        afghanBndy = arcpy.mapping.Layer(r"C:\arcpyMappingProject\CountryBoundary.lyr")

        # Reference layer for province styling
        refProvince = arcpy.mapping.Layer(r"C:\arcpyMappingProject\refProvince.lyr")

        # location for gemstone layer files
        gemstoneLayersLoc = r"C:\arcpyMappingProject\New Gemstone Layer Files"
        # location for geology layer files for each county
        geologyLayersLoc = r"C:\arcpyMappingProject\Geology layer files"

        # location for province boundary feature classes (geodatabase)
        provinceBndyLoc = r"C:\Province boundaries\Province.gdb"
        # make new separate lists for gemstones and provinces
        gemstones = []
        provinces = []

        # add layers found in every map
        # to main data frame

        arcpy.mapping.AddLayer(mainFrame, asianBndy, "BOTTOM")  # add Asia boundary layer
        arcpy.mapping.AddLayer(mainFrame, afghanBndy)  # place on top of Asian boundary layer

        # to inset data frame
        arcpy.mapping.AddLayer(insetFrame, asianBndy, "BOTTOM")
        arcpy.mapping.AddLayer(insetFrame, afghanBndy)
        print("Added Asian Boundaries and Afghan Provinces layer to both data frames")

        # adjust the data frames' dimensions and positions
        # inset data frame dimension
        insetFrame.elementHeight, insetFrame.elementWidth = 3, 3
        # inset data frame position
        insetFrame.elementPositionX, insetFrame.elementPositionY = 4.5, 0.7
        print("Changed Data Frames' Dimensions and Position ")

        # Choose extents of inset data frame. Stays same for all maps
        # select features in inset frame and zoom to them
        lstLayer = arcpy.mapping.ListLayers(mxd, "", insetFrame)
        where = "\"COUNTRY\" = 'Afghanistan'"
        arcpy.SelectLayerByAttribute_management(lstLayer[1], "", where)
        # zoom to selected feature: Afghanistan in inset frame
        insetFrame.zoomToSelectedFeatures()
        arcpy.SelectLayerByAttribute_management(lstLayer[1], "CLEAR_SELECTION")
        print("Zoomed to Afghanistan in inset data frame ")

        # Hide labels for province names in inset data frame
        lstLayer[0].showLabels = False
        lstLayer[1].showLabels = True
        print("Set labels for provinces in inset data frame ")

        for i in range(len(gemstonelist)):
            gemstones.append(gemstonelist[i][0])
            provinces.append(gemstonelist[i][1])

        # define Layer objects for gemstone and province
        for gemstone, province in zip(gemstones,provinces):
            # create path name for gemstone layer file
            gemPath = os.path.join(gemstoneLayersLoc, gemstone.lower())
            gemPath = gemPath + ".lyr"
            # create path name for geology layer file
            geolPath = os.path.join(geologyLayersLoc, province)
            geolPath = geolPath + "_geology.lyr"
            # create path name for province boundary layer
            provinceBndyPath = os.path.join(provinceBndyLoc, province)

            # create Layer files for gemstones, geology and provinces
            # gemstone
            gemstoneLayer = arcpy.mapping.Layer(gemPath)
            # geology
            geologyLayer = arcpy.mapping.Layer(geolPath)
            # province
            provinceBndyLayer = arcpy.mapping.Layer(provinceBndyPath)

            # add province boundary layer to inset frame
            arcpy.mapping.AddLayer(insetFrame, provinceBndyLayer)

            # add province-geology and gemstone layers to main data frame
            arcpy.mapping.AddLayer(mainFrame, geologyLayer)
            arcpy.mapping.AddLayer(mainFrame, gemstoneLayer)
            print("Added Geology Layer for " + province)
            print("Added Gemstone Layer for " + gemstone)

            # list layers in the map document by data frame
            ProvinceLyrList = arcpy.mapping.ListLayers(mxd, "", mainFrame)  # layers in main data frame
            CountryInsetLyrList = arcpy.mapping.ListLayers(mxd, "", insetFrame)  # layers in inset frame

            # for main data frame, zoom to province level
            # SQL expression for selecting province
            where_clause = "\"ADM1_EN\" = '" + province + "'"
            arcpy.SelectLayerByAttribute_management(ProvinceLyrList[2], "", where_clause)
            mainFrame.zoomToSelectedFeatures()
            arcpy.SelectLayerByAttribute_management(ProvinceLyrList[2], "CLEAR_SELECTION")

            print("Zoomed into Province scale in main data frame for " + province)

            # define symbology for province using UpdateLayer method with reference province layer
            arcpy.mapping.UpdateLayer(insetFrame, CountryInsetLyrList[0], refProvince)

            print("Changed symbology of province polygon in inset data frame to orange for " + province)

            # lstLayer[1].showLabels = True
            # lstLayer[0].showLabels = False
            # Change title of Map
            for elem in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
                elem.text = gemstone + " and Geology Map of " + province + ", Afghanistan"

            print("Created map title for " + gemstone + " in " + province)

            # Export Map JPEG
            jpeg_exportLoc = r"C:\arcpyMappingProject\MapJPEG"
            gemProvName = gemstone + "_" + province
            gemProvNameJPEG = gemProvName + ".jpeg"
            fullNameJPEG = os.path.join(jpeg_exportLoc, gemProvNameJPEG)
            arcpy.mapping.ExportToJPEG(mxd, fullNameJPEG)
            print("Exported map to JPEG for " + gemstone + " in " + province)

            # Save a copy of the map document
            mxd_copy = r"C:\arcpyMappingProject\Map Documents"
            gemProvNameMXD = gemProvName + ".mxd"
            fullNameMXD = os.path.join(mxd_copy, gemProvNameMXD)
            mxd.saveACopy(fullNameMXD)
            print("Saved a copy of the Map Document for " + gemstone + " in " + province)

            # Remove layers from the map document before starting with the next object
            # inset data frame
            arcpy.mapping.RemoveLayer(insetFrame, CountryInsetLyrList[0])
            # main data frame
            arcpy.mapping.RemoveLayer(mainFrame, ProvinceLyrList[0])
            arcpy.mapping.RemoveLayer(mainFrame, ProvinceLyrList[1])

            print("Removed layers before starting next map ")

            print("Completed map for " + gemstone + " and " + province)

    mapScript(gemstonelist)


main()
