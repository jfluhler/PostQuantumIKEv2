# PostQuantumIKEv2
Advancing IKEv2 for the Quantum Age: Challenges in Post-Quantum Cryptography Implementation on Constrained Networks

This project contains the necesarry elements to setup and test the performance of an IPSEC, IKEv2 protocal based, tunnel implementing post-quantum cryptography. 


## Core Data Collection Script DataCollectCore.py
  This script is the core data collection script for the PostQuantumIKEv2 project.
  The script is designed to be run on a host machine and will interact with Docker
  to start and stop containers. The script will also interact with the containers
  to enable qdisc for tc, and to start strongswan the charon deamon. 
  The script then invokes a loop to change the tc constraints
  an inner loop then initiates and terminates the IPSEC connection a defined number of times. 
  once the IPSEC loop is complete the script will update the tc constraints and repeat the process.
  Once the tc constraint range has been covered, script will copy the charon log files 
  from the Carol container to the host machine. The script will also log the run stats to a file. 
  Finally the script will also remove all qdisc constraints and stop the containers.

  To run the script, the user must provide a YAML configuration file.
  this can be passed to python as an argument in the terminal or the default file will be used.
  The default file is DataCollect_baseline.yaml but can be changed in the code below.

  Example terminal command: python3 DataCollectCore.py DataCollect_baseline.yaml


