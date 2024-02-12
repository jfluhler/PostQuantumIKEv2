#!/bin/bash


UNIXTIME=$(date +%s)



#Use dumpcap to capture packets on the interface ins160 
# and write the output to a file called ins160.pcap
# NOTE the & at the end of the command to run it in the background
dumpcap -i ins160 -w /test1/LOG_${UNIXTIME}.pcapng &

#Start the ipsec tunnel between VM1 and VM2
ipsec up VM1-VM2
ipsec status

# DO STUFF
ping 10.0.51.2 -c 30

# Stop the ipsec tunnel between VM1 and VM2
ipsec down VM1-VM2

#Stop the dumpcap process
killall dumpcap

