'''
Author: Kevin Cheriyan
Date: 12/13/2018
Purpose: Clip Afghanistan Geology Map for each province in Afghanistan
'''

import arcpy
import os
arcpy.env.workspace = r"C:\Users\...\Province.gdb"
arcpy.env.overwriteOutput = True

outWorkspace = r"C:\Users\...\GeolAfghanProvince.gdb"
geolMap = r"C:\Users\...\afgeolmap.shp"

fc = arcpy.ListFeatureClasses()
counter = 0

for i in fc:
    outFC = os.path.join(outWorkspace,i+"_geology")
    arcpy.Clip_analysis(geolMap, i, outFC)
    counter = counter + 1
    print i + " has finished clipping: " + outFC + " **** " + str(counter) + "/34 provinces clipped. "

print "The script has finished clipping all features."
