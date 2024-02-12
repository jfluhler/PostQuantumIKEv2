#!/bin/bash


UNIXTIME=$(date +%s)
LOC=
LOGNAME="${LOC}/TEST1_${UNIXTIME}.pcapng"


#Use dumpcap to capture packets on the interface ins160 
# and write the output to a file called ins160.pcap
# NOTE the & at the end of the command to run it in the background
dumpcap -i ens160 -w "${LOGNAME}" &

#Short pause so dumpcap can start capturing packets.
sleep 5

#Start the ipsec tunnel between VM1 and VM2
ipsec up VM1-VM2
ipsec status

# DO STUFF
ping 10.0.52.2 -c 30

# Stop the ipsec tunnel between VM1 and VM2
ipsec down VM1-VM2

#Stop the dumpcap process
killall dumpcap

chmod 777 ../../../../"${LOGNAME}"

su uah
#This is move command is not working
sudo mv ~/../../../../"${LOGNAME}" ~/LOGS/


