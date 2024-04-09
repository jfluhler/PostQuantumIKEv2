# This is code for University of Alabama in Huntsville course CS692 Capstone Project, Spring 2024, INSuRE Group 4
# Description : This sender.py file is a python file that sends files to a machine running a corresponding receiver.py script.
# Possible arguments : sender.py ["one" / "all" / "target" (default:"one")] [folderPath (default:"./deliver")] [receiverIP (default:"X.X.X.X")]

import sys
import os
import socket
import time

# Process arguments, if they were provided. Use defaults if an argument was not provided.
wasError = False
sendMode = "one"
folderPath = "./deliver"
receiverIP = "127.0.0.1" #"10.0.51.2"
if len(sys.argv) > 1: # Check argument for sending mode
    sendMode = sys.argv[1]
    if (sendMode != "one") and (sendMode != "all") and (sendMode != "target"):
        print("\nERROR! First argument must be from this list:\n\"one\" -> Sends one file.\n\"all\" -> Sends all files in the folder.\n\"target\" -> Sends only a specified file.")
        wasError = True
if len(sys.argv) > 2: # Check argument for path to folder conatining images
    folderPath = sys.argv[2]
elif sendMode == "target": # Specified they wanted to send a specific file, but did not provide path
    print("\nERROR! Specified \"target\" mode, but failed to provide a file!")
    wasError = True
# Check if path is valid and has at least 1 .png file in it
if (sendMode != "target") and (not os.path.isdir(folderPath)):
    print("\nERROR! Specified path \"" + folderPath + "\" could not be found!")
    wasError = True
elif (sendMode != "target") and (not os.listdir(folderPath)):
    print("\nERROR! Specified path \"" + folderPath + "\" is empty!")
    wasError = True
if (sendMode == "target") and (not os.path.exists(folderPath)):
    print("\nERROR! Specified file \"" + folderPath + "\" could not be found!")
    wasError = True
if len(sys.argv) > 3: # Check if the user supplied an IP address
    receiverIP = sys.argv[3]
# Check if IP address is valid
try:
    socket.inet_aton(receiverIP)
except:
    socket.error
    print("\nERROR! Specified IP address \"" + receiverIP + "\" is not valid!")
    wasError = True
if wasError:
    sys.exit("\nStopping execution...")

# Create the socket
senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4 Address, UDP socket
receiverPort = 12345  # Arbitrary. Just make sure it matches the receiver, and isn't a reserved port.

# Send file or files
bufferSize = 1024   # How much to send at a time. 1KB = 1024
if sendMode == "one": # MODE: Grab any file in the folder and send it.
    fileName = os.listdir(folderPath)[0]
    sendingFile = open(folderPath + "/" + fileName, "rb") # Open as read binary
    # Tell receiver that a file is coming, with filename.
    initialContact = str.encode("SENDINGFILE/" + fileName)
    senderSocket.sendto(initialContact, (receiverIP, receiverPort))
    # Send file
    while True:
        sendingBytes = sendingFile.read(bufferSize)
        if not sendingBytes:    # If condition is true, all data is sent already.
            break
        senderSocket.sendto(sendingBytes, (receiverIP, receiverPort))
    print("\nAttempted to send one file, \"" + fileName + "\" to " + receiverIP + ":" + str(receiverPort) + " via UDP.")
if sendMode == "all": # MODE: Send all files in the folder.
    for fileName in os.listdir(folderPath):
        #print("\nSorry! This sending mode is not yet supported.")
        sendingFile = open(folderPath + "/" + fileName, "rb") # Open as read binary
        # Tell receiver that a file is coming, with filename and size.
        initialContact = str.encode("SENDINGFILE/" + fileName)
        senderSocket.sendto(initialContact, (receiverIP, receiverPort))
        while True:
            sendingBytes = sendingFile.read(bufferSize)
            if not sendingBytes:    # If condition is true, all data is sent already.
                break
            senderSocket.sendto(sendingBytes, (receiverIP, receiverPort))
        print("\nAttempted to send one file, \"" + fileName + "\" to " + receiverIP + ":" + str(receiverPort) + " via UDP.")
        time.sleep(3)
if sendMode == "target": # MODE: Send the specified file.
    fileName = folderPath.split("/")[-1]
    sendingFile = open(folderPath, "rb") # Open as read binary
    # Tell receiver that a file is coming, with filename and size.
    initialContact = str.encode("SENDINGFILE/" + fileName)
    senderSocket.sendto(initialContact, (receiverIP, receiverPort))
    while True:
        sendingBytes = sendingFile.read(bufferSize)
        if not sendingBytes:    # If condition is true, all data is sent already.
            break
        senderSocket.sendto(sendingBytes, (receiverIP, receiverPort))
    print("\nAttempted to send one file, \"" + folderPath.split("/")[-1] + "\" to " + receiverIP + ":" + str(receiverPort) + " via UDP.")