def main():
    import arcpy
    import os
    import time
    arcpy.env.overwriteOutput = True  # overwrite output

    start_time = time.time()

    def GemstoneInProvince():
        # input shapefile containing all gemstone feature classes (resulting layer after performing spatial join with Province
        # boundary layer)
        in_fc = r"C:\Gemstone-Geology maps\all_gemstones\join\gemstone_provinces.shp"
        # output shapefile for Sort_management to output
        fc = r"C:\Gemstone-Geology maps\all_gemstones\join\gemstone_provinces_sorted.shp"
        # Sort gemstone name in alphabetical order so that final list will be grouped by gemstone
        print("Sorting Master gemstone-province feature class in ascending order ")
        arcpy.Sort_management(in_fc,fc,[["Commodity1", 'ASCENDING']])
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
        print("***********************************")
        return gem_loc[:]

    gemstonelist = GemstoneInProvince()

    def mapScript(gemstonelist):

        # define Map Document to start script with. This Map Doc should have a basic template with layout elements already
        # set
        mxd = arcpy.mapping.MapDocument(r"C:\Gemstone-Geology maps\arcpyMappingProject\starter_mapdoc.mxd")

        # List and define data frames
        print("Defining Data Frames... ")
        mainFrame = arcpy.mapping.ListDataFrames(mxd)[0]
        insetFrame = arcpy.mapping.ListDataFrames(mxd)[1]

        # Layer files for Country and Asia
        print("Defining Asian Country Boundaries and Afghanistan Provinces Layers in starter Map Document...")
        asianBndy = arcpy.mapping.Layer(r"C:\Gemstone-Geology maps\arcpyMappingProject\AsiaBoundaries.lyr")
        afghanBndy = arcpy.mapping.Layer(r"C:\Gemstone-Geology maps\arcpyMappingProject\CountryBoundary.lyr")

        # Reference layer for province styling
        refProvince = arcpy.mapping.Layer(r"C:\Gemstone-Geology maps\arcpyMappingProject\refProvince.lyr")

        # location for gemstone layer files
        gemstoneLayersLoc = r"C:\Gemstone-Geology maps\arcpyMappingProject\New Gemstone Layer Files"
        # location for geology layer files for each county
        geologyLayersLoc = r"C:\Gemstone-Geology maps\arcpyMappingProject\Geology layer files"

        # location for province boundary feature classes (geodatabase)
        provinceBndyLoc = r"C:\Province boundaries\Province.gdb"
        # make new separate lists for gemstones and provinces
        gemstones = []
        provinces = []

        # add layers found in every map
        # to main data frame
        print("Adding Asian Boundaries and Afghan Provinces layer to both data frames...")

        arcpy.mapping.AddLayer(mainFrame, asianBndy, "BOTTOM")  # add Asia boundary layer
        arcpy.mapping.AddLayer(mainFrame, afghanBndy)  # place on top of Asian boundary layer

        # to inset data frame
        arcpy.mapping.AddLayer(insetFrame, asianBndy, "BOTTOM")
        arcpy.mapping.AddLayer(insetFrame, afghanBndy)


        # adjust the data frames' dimensions and positions
        # inset data frame dimension
        print("Changing Data Frames' Dimensions and Position... ")
        insetFrame.elementHeight, insetFrame.elementWidth = 3, 3
        # inset data frame position
        insetFrame.elementPositionX, insetFrame.elementPositionY = 4.5, 0.7


        # Choose extents of inset data frame. Stays same for all maps
        # select features in inset frame and zoom to them
        lstLayer = arcpy.mapping.ListLayers(mxd, "", insetFrame)
        where = "\"COUNTRY\" = 'Afghanistan'"
        arcpy.SelectLayerByAttribute_management(lstLayer[1], "", where)
        # zoom to selected feature: Afghanistan in inset frame
        print("Zooming in to Afghanistan in inset data frame... ")
        insetFrame.zoomToSelectedFeatures()
        arcpy.SelectLayerByAttribute_management(lstLayer[1], "CLEAR_SELECTION")

        # Hide labels for province names in inset data frame
        print("Setting labels for provinces in inset data frame... ")
        lstLayer[0].showLabels = False
        lstLayer[1].showLabels = True


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
            print("Adding Geology Layer for " + province + "...")
            print("Adding Gemstone Layer for " + gemstone + "...")
            arcpy.mapping.AddLayer(mainFrame, geologyLayer)
            arcpy.mapping.AddLayer(mainFrame, gemstoneLayer)


            # list layers in the map document by data frame
            ProvinceLyrList = arcpy.mapping.ListLayers(mxd, "", mainFrame)  # layers in main data frame
            CountryInsetLyrList = arcpy.mapping.ListLayers(mxd, "", insetFrame)  # layers in inset frame

            # for main data frame, zoom to province level
            # SQL expression for selecting province
            print("Zooming into Province scale in main data frame for " + province + "...")
            where_clause = "\"ADM1_EN\" = '" + province + "'"
            arcpy.SelectLayerByAttribute_management(ProvinceLyrList[2], "", where_clause)
            mainFrame.zoomToSelectedFeatures()
            arcpy.SelectLayerByAttribute_management(ProvinceLyrList[2], "CLEAR_SELECTION")

            # define symbology for province using UpdateLayer method with reference province layer
            print("Changing symbology of province polygon in inset data frame to orange for " + province + "...")
            arcpy.mapping.UpdateLayer(insetFrame, CountryInsetLyrList[0], refProvince)

            # lstLayer[1].showLabels = True
            # lstLayer[0].showLabels = False
            # Change title of Map
            for elem in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
                elem.text = gemstone + " and Geology Map of " + province + ", Afghanistan"

            print("Created map title for " + gemstone + " in " + province)

            # Export Map JPEG
            print("Exporting map to JPEG for " + gemstone + " in " + province + "...")
            jpeg_exportLoc = r"C:\Gemstone-Geology maps\arcpyMappingProject\MapJPEG"
            gemProvName = gemstone + "_" + province
            gemProvNameJPEG = gemProvName + ".jpeg"
            fullNameJPEG = os.path.join(jpeg_exportLoc, gemProvNameJPEG)
            arcpy.mapping.ExportToJPEG(mxd, fullNameJPEG, resolution=2000)

            # Save a copy of the map document
            print("Saving a copy of the Map Document for " + gemstone + " in " + province + "...")
            mxd_copy = r"C:\Gemstone-Geology maps\arcpyMappingProject\Map Documents"
            gemProvNameMXD = gemProvName + ".mxd"
            fullNameMXD = os.path.join(mxd_copy, gemProvNameMXD)
            mxd.saveACopy(fullNameMXD)

            # Remove layers from the map document before starting with the next object
            # inset data frame
            print("Removing layers before starting next map... ")
            arcpy.mapping.RemoveLayer(insetFrame, CountryInsetLyrList[0])
            # main data frame
            arcpy.mapping.RemoveLayer(mainFrame, ProvinceLyrList[0])
            arcpy.mapping.RemoveLayer(mainFrame, ProvinceLyrList[1])

            print("Completed map for " + gemstone + " and " + province)
            print("***********************************")

    mapScript(gemstonelist)
    print("ALL DONE!!! ")
    elapsed_time = time.time() - start_time
    print("This program took " + str(round(elapsed_time, 2)) + " seconds, or " + str(int(elapsed_time / 60)) + " minutes and " + str(round(elapsed_time % 60, 2)) + " seconds to run!")


main()
