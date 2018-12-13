'''
Author: Kevin Cheriyan
Date: 10/19/2018
Purpose: This program goes through a list of country boundaries given in a geodatabase, then checks the Global Mining
Facilities Database to see if the "New_Country_Name" field contains the name, then clips the Mining Facilities database
to the country's boundaries. The program also updates the user on its progress.
'''
import arcpy # import arcpy module
import os
import sys

arcpy.env.workspace = r"C:\Users\kcheriyan\Desktop\Projects\GMAS\Mapping Initiative\Mapping\Data\CountryBndy.gdb" # Set workspace environment as gdb with country boundaries
arcpy.env.overwriteOutput = True  # Overwrite output

# Location for individual country boundaries, Source: Natural Earth, 50m resolution
cntyBndy = r"C:\Users\kcheriyan\Desktop\Projects\GMAS\Mapping Initiative\Mapping\Data\CountryBndy.gdb" 
# Location for Global Mining Facilities Geodatabase, all countries in one Master-gdb
minFac_global = r"C:\Users\kcheriyan\Desktop\Projects\GMAS\Mapping Initiative\Mapping\Data\GlobalMinFacGeoDBv2\GlobalMiningFacilities.gdb\GlobalMinFacDB"


#Output file for individual GlobalMinFac records for each country
outFC = "C:\Users\kcheriyan\Desktop\Projects\GMAS\Mapping Initiative\Mapping\Data\GlobalMinFacGeoDBv2\GlobalMinFac_country.gdb\\"
# All countries in Country boundary gdb
CntyFC = arcpy.ListFeatureClasses() 

# Field name in Global Mining Facilities DB to check for country name. Field containing edited country names
field = "New_Country_Name"

# Function to return unique country names from Global MinFac DB, sorted
def unique_values(minFac_global,field):
    with arcpy.da.SearchCursor(minFac_global,[field]) as cursor:
        return sorted({row[0] for row in cursor})


countryList = [] # set empty list for country names
noMatchList = [] # set empty list for country names that didn't match

for country in CntyFC:
    if country in unique_values(minFac_global, field):  # if country in boundary gdb is in MinFac DB, add to new empty list
        countryList.append(country)
        arcpy.Clip_analysis(minFac_global, country, outFC+country)  # Perform Clip
        print "The program has finished performing Clip on ******* " + country + " ******* "
    else:
        print "There are no records in Global MinFac DB for ******* " + country + " ******* "
        noMatchList.append(country)
print "\nThere are a total of " + str(len(countryList)) + " countries Clipped"
print "\nThere are a total of " + str(len(noMatchList)) + " countries that couldn't be matched or Clipped"

print "\n The countries that couldn't be clipped are: .........********* "
for i in noMatchList:
    print i + " couldn't be clipped. "

for i in countryList:
    print i
