#!/bin/bash


MOON="192.168.0.2"
CAROL="192.168.0.3"


constrain_bandwidth() {

  
    sudo tc qdisc del dev docker0 root &>/dev/null


    sudo tc qdisc add dev docker0 root handle 1: htb default 10
    sudo tc class add dev docker0 parent 1: classid 1:1 htb rate "$3" quantum 3000000 # This value can be changed
    sudo tc filter add dev docker0 protocol ip parent 1: prio 1 u32 match ip src "$1" match ip dst "$2" flowid 1:1
}



# Start with a baseline bandwidth limit
BASE_BANDWIDTH_BITS=$((100 * 1000000))

constrain_bandwidth "$MOON" "$CAROL" "$BASE_BANDWIDTH_BITS"

# Incrementally decrease bandwidth every 5 seconds
for ((i=0; i<10; i++)); do
    NEW_BANDWIDTH_BITS=$(( (20 * (100 - i)) * 1000000 )) #the 20 here can be changed
    constrain_bandwidth "$MOON" "$CAROL" "$NEW_BANDWIDTH_BITS"
    echo "Bandwidth constrained to $((NEW_BANDWIDTH_BITS / 1000000)) Mbps"
    sleep 5
done

echo "done"



