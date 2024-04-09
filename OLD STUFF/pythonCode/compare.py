# This is code for University of Alabama in Huntsville course CS692 Capstone Project, Spring 2024, INSuRE Group 4
# Description : This compare.py file is a python file that checks the properties of files with like names in different folders.
# Possible arguments : compare.py [originalFolder (default:"./deliver")] [copyFolder (default:"./inbox")]

from __future__ import division
import sys
import os
 
# Get args
wasError = False
originalFolder = "./deliver"
copyFolder = "./inbox"
if len(sys.argv) > 1:
    originalFolder = sys.argv[1]
if len(sys.argv) > 2:
    copyFolder = sys.argv[2]
if not os.path.isdir(originalFolder):
    print("\nERROR! Specified path \"" + originalFolder + "\" could not be found!")
    wasError = True
elif not os.listdir(originalFolder):
    print("\nERROR! Specified path \"" + originalFolder + "\" is empty!")
    wasError = True
if not os.path.isdir(copyFolder):
    print("\nERROR! Specified path \"" + copyFolder + "\" could not be found!")
    wasError = True
elif not os.listdir(copyFolder):
    print("\nERROR! Specified path \"" + copyFolder + "\" is empty!")
    wasError = True
if wasError:
    sys.exit("\nStopping execution...")

# Get files from folders
originalFiles = os.listdir(originalFolder)
copyFiles = os.listdir(copyFolder)

# Check to see how much data made it.
for copyName in copyFiles:
    for originalName in originalFiles:
        if copyName == originalName:
            lossRatio = float(100) * (float(1) - (os.path.getsize(copyFolder + "/" + copyName) / os.path.getsize(originalFolder + "/" + originalName)))
            print("File " + originalName + f" was transmitted with {lossRatio:.5f}% data loss.")
