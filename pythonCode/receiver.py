# This is code for University of Alabama in Huntsville course CS692 Capstone Project, Spring 2024, INSuRE Group 4
# Description : This receiver.py file is a python file that gets files from a machine running a corresponding sender.py script.
# Possible arguments : receiver.py ["one" / "all" (default:"one")] [folderPath (default:"./inbox")]

import sys
import os
import socket

# Process arguments, if they were provided. Use defaults if an argument was not provided.
wasError = False
receiverMode = "one"
folderPath = "./inbox"
if len(sys.argv) > 1: # Check argument for sending mode
    receiverMode = sys.argv[1]
    if (receiverMode != "one") and (receiverMode != "all"):
        print("\nERROR! First argument must be from this list:\n\"one\" -> Gets one file.\n\"all\" -> Waits for files indefinitely.")
        wasError = True
if len(sys.argv) > 2: # Check argument for path to folder conatining images
    folderPath = sys.argv[2]
if (not os.path.isdir(folderPath)):
    print("\nERROR! Specified folder for saving files \"" + folderPath + "\" could not be found!")
    wasError = True
if wasError:
    sys.exit("\nStopping execution...")

# Create the socket
receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiverSocket.bind(("", 12345)) # Any IP, port must match sender.

# Receive file or files
bufferSize = 1024   # How much to get at a time. 1KB = 1024
gettingFile = False
# Get one file
if receiverMode == "one":
    print("Waiting on data for a file...")
    while True:
        try:    
            try:
                data, senderAddress = receiverSocket.recvfrom(bufferSize)
            except KeyboardInterrupt:
                sys.exit("Interrupted. Closing...")
            receiverSocket.settimeout(2)
            if not data:
                if gettingFile:
                    print("Finished getting data for " + fileName)
                    writeFile.close()
                    sys.exit("\nFile saved.")
                gettingFile = False
            if gettingFile:
                writeFile.write(data)
            else:
                initialContact, fileName = (data.decode()).split("/")
                #print("Got data, Initial Contact?:" + initialContact + "\nFile Name?:" + fileName)
                if initialContact == "SENDINGFILE" and fileName:
                    print("File incoming! Getting file \"" + fileName + "\" and saving to folder \"" + folderPath + "\".")
                    gettingFile = True
                    writeFile = open(folderPath + "/" + fileName, "wb")
        except TimeoutError:
            print("Data has stopped transmitting. Assuming we are done.")
            print("Finished getting data for " + fileName + "\n")
            writeFile.close()
            gettingFile = False
            sys.exit("\nFile saved.")
# Keep getting files
if receiverMode == "all":
    print("Waiting on data...")
    while True:
        try:
            try:
                try:
                    data, senderAddress = receiverSocket.recvfrom(bufferSize)
                except KeyboardInterrupt:
                    sys.exit("\nInterrupted. Closing...")
                receiverSocket.settimeout(2)
                if not data:
                    if gettingFile:
                        print("Finished getting data for " + fileName)
                        writeFile.close()
                        print("File saved.\n\nWaiting on data...")
                    gettingFile = False
                if gettingFile:
                    writeFile.write(data)
                else:
                    initialContact, fileName = (data.decode()).split("/")
                    #print("Got data, Initial Contact?:" + initialContact + "\nFile Name?:" + fileName)
                    if initialContact == "SENDINGFILE" and fileName:
                        print("File incoming! Getting file \"" + fileName + "\" and saving to folder \"" + folderPath + "\".")
                        gettingFile = True
                        writeFile = open(folderPath + "/" + fileName, "wb")
            except TimeoutError:
                if gettingFile:
                    print("Data has stopped transmitting. Assuming we are done.")
                    print("Finished getting data for " + fileName + "\n")
                    writeFile.close()
                    gettingFile = False
        except KeyboardInterrupt:
            sys.exit("\nInterrupted. Closing...")