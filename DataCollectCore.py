## Core Data Collection Script

# Import the required libraries
import os
import subprocess
import shlex
import time
import json
from python_on_whales import DockerClient
from tqdm import trange


max_run_time = 3600

docker = DockerClient(compose_files=["./strongX509/pq-strongswan/docker-compose.yml"])
docker.compose.ps()

## IMPORT CONFIGURATION FILE
# Open the JSON file
with open('PostQuantumIKEv2/DataCollect.json') as file:
    JSONConfig = json.load(file)

# Breakup the JSON file into different dictionaries
CoreConfig = JSONConfig.get('CoreConfig')
CarolConfig = JSONConfig.get('Carol_TC_Config')
MoonConfig = JSONConfig.get('Moon_TC_Config')

# Print the dictionary values
print("\n\nCORE CONFIG")
for x in CoreConfig:
  print("\t" + x + ':', CoreConfig[x])

# Because the Carol and Moon dictionaries are nested, 
#  we need to loop through the top level and the nested levels to print
print("\n\nCAROL CONFIG")
for x, obj in CarolConfig.items():
  print("\t" + x)
  for y in obj:
    print("\t\t" + y + ':', obj[y])

print("\n\nMOON CONFIG")
for x, obj in MoonConfig.items():
  print("\t" + x)
  for y in obj:
    print("\t\t" + y + ':', obj[y])

## SET TO FALSE IF DOCKER AND CHARON ARE ALREADY RUNNING
FreshRun = False


if FreshRun == True:
    ## Start Docker Containers
    print(" -- Starting Docker Containers -- ")
    docker.compose.up(detach=True)

    # Access Carol & moon to enable qdisc
    print(" -- Enable qdisc in Carol & Moon -- ")
    docker.execute("carol", shlex.split("ip link set eth0 qlen 1000"))
    docker.execute("moon", shlex.split("ip link set eth0 qlen 1000"))

    # Enable moon charon to accept IPSEC connections
    print(" -- Enable .charon deamon on moon-- ")
    docker.execute("moon", shlex.split("./charon"), detach=True)
    docker.execute("moon", shlex.split("swanctl --list-conns"))

    #Start Logging (Charon)
    docker.execute("carol", shlex.split("./charon"), detach=True)
    docker.execute("carol", shlex.split("swanctl --list-conns"))

    # Access Carol and add starting TC Constrains
    docker.execute("carol", shlex.split("tc qdisc add dev eth0 root netem delay 1000ms"))

    # Access Moon and add starting TC Constrains

time.sleep(1)

# Start Run Timer
print(" -- Starting Data Collection Run -- ")
startrun_tic = time.perf_counter()



#START Constraint 1 Loop
for i in trange(1):
    
    #Start Wireshark Logging

    L1_tic = time.perf_counter()

    # Update Carol Constraints (change)
    docker.execute("carol", shlex.split("tc qdisc change dev eth0 root netem delay 10ms"))

    # START Single Constraint Function
    # IPSEC LOOP N TIMES
    N = 10
    print(" -- Begin IPSec Loop -- ")
    for j in trange(1, N):
        # Initiate IPSEC Connection
        docker.execute("carol", shlex.split("swanctl --initiate --child net"))

        # Send data file
        docker.execute("carol", shlex.split("ping -c 5 strongswan.moon.com"))

        # Deactivate IPSEC Connection
        docker.execute("carol", shlex.split("swanctl --terminate --ike home"))

        # Check timer if > max time break loop
        if time.perf_counter() - startrun_tic > max_run_time:
            break

    # END IPSEC LOOP 
    # END Single Constraint Function

    #Stop Wireshark Logging

    # Move Data Files from Carol to local machine (or volume) and rename
    LogName = "./charon" + str(i) + ".log"
    docker.copy(("carol", "/var/log/charon.log"), LogName)

    #print run stats and estimated remaining time
    total_time = time.perf_counter() - startrun_tic
    L1_time = time.perf_counter() - L1_tic
    EstRemTime = (N-i) * L1_time
    print("Total Time: " + str(total_time) + " seconds")
    print("Last Run Time: " + str(L1_time) + " seconds")
    print("Estimated Remaining Time: " + str(EstRemTime) + " seconds")
    
    #check timer if > max time break loop
    if time.perf_counter() - startrun_tic > max_run_time:
        break

    #Remove Carol Charon Log File
    docker.execute("carol", shlex.split("rm /var/log/charon.log"))

#END Constraint 1 Loop

# If not done previously Move all Data Files from Carol to local machine

#print run stats
total_time = time.perf_counter() - startrun_tic
print("Total Time: " + str(total_time) + " seconds")

#save run stats to file
file1 = open("runstats.txt","w")
file1.writelines("Total Time: " + str(total_time) + " seconds")
file1.close()

#remove all TC constraints
try:
    docker.execute("carol", shlex.split("tc qdisc del dev eth0 root"))
    docker.execute("moon", shlex.split("tc qdisc del dev eth0 root"))
except:
    print("Possible Error removing TC constraints")

## Stop Docker Containers
docker.compose.down()
