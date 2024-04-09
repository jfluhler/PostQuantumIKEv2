## Core Data Collection Script

# Import the required libraries
import os
import subprocess
import shlex
import time
import json
import yaml
import numpy as np
from python_on_whales import DockerClient
from tqdm import trange

# ConfigFile = "DataCollect_bandwidth.json"
ymlConfig = "DataCollect_bandwidth.yaml"

## IMPORT CONFIGURATION FILE
# Open the JSON file
# with open('PostQuantumIKEv2/' + ConfigFile) as file:
#     JSONConfig = json.load(file)

# Open the YAML config file
with open('PostQuantumIKEv2/' + ymlConfig) as file:
    YAMLConfig = yaml.safe_load(file)

# Breakup the JSON file into different dictionaries
# JCoreConfig = JSONConfig.get('CoreConfig')
# JCarolConfig = JSONConfig.get('Carol_TC_Config')
# JMoonConfig = JSONConfig.get('Moon_TC_Config')

CoreConfig = YAMLConfig.get('CoreConfig')
CarolConfig = YAMLConfig.get('Carol_TC_Config')
MoonConfig = YAMLConfig.get('Moon_TC_Config')

pLvl = CoreConfig['PrintLevel']

if pLvl > 0:
    # Print the dictionary values
    print("\n\nCORE CONFIG")
    for x in CoreConfig:
        print("\t" + x + ':', CoreConfig[x])

    # Because the Carol and Moon dictionaries are nested, 
    #  we need to loop through the top level and the nested levels to print
    print("\n\nCAROL CONFIG")
    if bool(CarolConfig):
        for x, obj in CarolConfig.items():
            print("\t" + x)

            for y in obj:
                print("\t\t" + y + ':', obj[y])

    print("\n\nMOON CONFIG")
    if bool(MoonConfig):
        for x, obj in MoonConfig.items():
            print("\t" + x)

            for y in obj:
                print("\t\t" + y + ':', obj[y])

# Define the maximum run time
if bool(CoreConfig['MaxTimeS']):
    max_run_time = CoreConfig['MaxTimeS']
else:
    max_run_time = 3600

print("Max Run Time: " + str(max_run_time/60) + " minutes")

# Define the Docker Client
docker = DockerClient(compose_files=CoreConfig['compose_files'])
docker.compose.ps()

## SET TO FALSE IF DOCKER AND CHARON ARE ALREADY RUNNING
FreshRun = False

if FreshRun == False:
    ## Start Docker Containers
    if pLvl > 0:
        print(" -- Starting Docker Containers -- ")
    docker.compose.up(detach=True)
    time.sleep(5)
else:
    docker.compose.restart()

if True == True:
    # Access Carol & moon to enable qdisc
    if pLvl > 0:
        print(" -- Enable qdisc in Carol & Moon -- ")
    docker.execute("carol", shlex.split("ip link set eth0 qlen 1000"))
    docker.execute("moon", shlex.split("ip link set eth0 qlen 1000"))

    # Enable moon charon to accept IPSEC connections
    if pLvl > 0:
        print(" -- Enable .charon deamon on moon-- ")
    docker.execute("moon", shlex.split("./charon"), detach=True)
    docker.execute("moon", shlex.split("swanctl --list-conns"))

    #Start Logging (Charon)
    docker.execute("carol", shlex.split("./charon"), detach=True)
    docker.execute("carol", shlex.split("swanctl --list-conns"))


    # Access Carol and add starting TC Constrains
    # Because the Carol and Moon dictionaries are nested, 
    #  we need to loop through the top level and the nested levels to print
    
    C_ctype = ''
    C_constraint = ''
    C_interface = ''
    C_Min = 0
    C_Max = 0
    C_units = ''
    C_steps = 0
    C_AddParams = ''

    M_ctype = ''
    M_constraint = ''
    M_interface = ''
    M_Min = 0
    M_Max = 0
    M_units = ''
    M_steps = 0
    M_AddParams = ''

    for x, obj in CarolConfig.items():
        if x == 'Constraint1':
            C_ctype = obj['Type']
            C_constraint = obj['Constraint']
            C_interface = obj['Interface']
            C_Min = obj['StartRange']
            C_Max = obj['EndRange']
            C_units = obj['Units']
            C_steps = obj['Steps']
            C_AddParams = obj['AddParams']

            tc_string = ("tc qdisc " + "add" + " dev " + C_interface + " root " + C_ctype + " " +  
                C_constraint + " " + str(C_Min) + C_units + " " + C_AddParams)

            if pLvl > 1:
                print("Carol Starter Adjustable Constraint: " + tc_string)
            docker.execute("carol", shlex.split(tc_string))

            if CoreConfig['MirrorMoon'] == True:
                docker.execute("moon", shlex.split(tc_string))

        else:
            tmp_ctype = obj['Type']
            tmp_constraint = obj['Constraint']
            tmp_interface = obj['Interface']
            tmp_Min = obj['StartRange']
            tmp_units = obj['Units']
            tmp_AddParams = obj['AddParams']

            

            if tmp_ctype == C_ctype:
                # If the constraint type is the same then we need to tack on the additional constraints
                # forexample if we are using netem on both constraints EG delay and loss
                # then we cannot add both, so we combine them into one command and update AddParams with the 
                # additional constraints. Then we need replace the previous constraint
                # tc qdisc replace dev eth0 root netem delay 200ms loss 10%
                # but really the perefered placement would be the the AddParams field.

                C_AddParams = (C_AddParams + " " + tmp_constraint + " "  + str(tmp_Min) + tmp_units + " " + tmp_AddParams)

                if pLvl > 1:
                    print("Warning: New Constraint Type is the same as the adjustable constraint:" + tmp_ctype)
                tc_string = ("tc qdisc " + "replace" + " dev " + C_interface + " root " + C_ctype + " " +  
                    C_constraint + " " + str(C_Min) + C_units + " " + C_AddParams)
            else:
                tc_string = ("tc qdisc add dev " + tmp_interface + " root " + tmp_ctype + " " + 
                    tmp_constraint + " " + str(tmp_Min) + tmp_units + " " + tmp_AddParams)
            if pLvl > 1:
                print("Carol Starter Constraint: " + tc_string)

            docker.execute("carol", shlex.split(tc_string))

            if CoreConfig['MirrorMoon'] == True:
                docker.execute("moon", shlex.split(tc_string))
            

    # Access Moon and add starting TC Constrains
    if bool(MoonConfig):
        for x, obj in MoonConfig.items():
            if x == 'Constraint1':
                M_ctype = obj['Type']
                M_constraint = obj['Constraint']
                M_interface = obj['Interface']
                M_Min = obj['StartRange']
                M_Max = obj['EndRange']
                M_units = obj['Units']
                M_steps = obj['Steps']
                M_AddParams = obj['AddParams']

                tc_string = ("tc qdisc add dev " + M_interface + " root " + M_ctype + " " +  
                    M_constraint + " " + str(M_Min) + M_units + " " + M_AddParams)

                if pLvl > 1:
                    print("Moon Starter Adjustable Constraint: " + tc_string)
                docker.execute("moon", shlex.split(tc_string))
            else:
                tmp_ctype = obj['Type']
                tmp_constraint = obj['Constraint']
                tmp_interface = obj['Interface']
                tmp_Min = obj['StartRange']
                tmp_units = obj['Units']
                tmp_AddParams = obj['AddParams']

                if tmp_ctype == M_ctype:
                    # If the constraint type is the same then we need to tack on the additional constraints
                    # forexample if we are using netem on both constraints EG delay and loss
                    # then we cannot add both, so we combine them into one command and update AddParams with the 
                    # additional constraints. Then we need replace the previous constraint
                    # tc qdisc replace dev eth0 root netem delay 200ms loss 10%
                    # but really the perefered placement would be the the AddParams field.

                    M_AddParams = (M_AddParams + " " + tmp_constraint + " "  + str(tmp_Min) + tmp_units + " " + tmp_AddParams)

                    if pLvl > 1:
                        print("Warning: New Constraint Type is the same as the adjustable constraint:" + tmp_ctype)

                    tc_string = ("tc qdisc " + "replace" + " dev " + M_interface + " root " + M_ctype + " " +  
                        M_constraint + " " + str(M_Min) + M_units + " " + M_AddParams)
                else:
                    tc_string = ("tc qdisc add dev " + tmp_interface + " root " + tmp_ctype + " " + 
                        tmp_constraint + " " + str(tmp_Min) + tmp_units + " " + tmp_AddParams)

                if pLvl > 1:
                        print("Moon Starter Constraint: " + tc_string)

                docker.execute("moon", shlex.split(tc_string))

time.sleep(1)

# Start Run Timer
if pLvl > 0:
    print(" -- Starting Data Collection Run -- ")
startrun_tic = time.perf_counter()



#START Constraint 1 Loop

# Calculate a linear range of values for Carol Constraint 1
C_vals = np.linspace(C_Min, C_Max, C_steps)

if pLvl > 0:
    print(" -- Begin Constraint 1 Loop -- ")

if pLvl > 1:
    print("Total Planned Iterations: " + str(len(C_vals)))
    print("Planned Values for Carol Constraint " + str(C_vals))

for i in trange(len(C_vals)):
    
    
    #Start Wireshark Logging

    L1_tic = time.perf_counter()

    # Update Carol Constraints (change)
    tc_string = ("tc qdisc change dev " + C_interface + " root " + C_ctype + " " + 
        C_constraint + " " + str(C_vals[i]) + C_units + " " + C_AddParams)
    
    docker.execute("carol", shlex.split(tc_string))
    if pLvl > 1:
        print("Updated Carol With: " + tc_string)

    if CoreConfig['MirrorMoon'] == True:
        # Update Moon Constraints (change) to match carol
        docker.execute("moon", shlex.split(tc_string))
        if pLvl > 1:
            print("Updated Moon With: " + tc_string)


    # START Single Constraint Function
    # IPSEC LOOP N TIMES
    ipsec_N = CoreConfig['TC_Interations']
    if pLvl > 1:
        print(" -- Begin IPSec Loop -- ")
    for j in trange(ipsec_N):
        # Initiate IPSEC Connection
        if pLvl > 3:
            print("swanctl --initiate --child net")
        
        try:
            docker.execute("carol", shlex.split("swanctl --initiate --child net"))

            # Send data file
            docker.execute("carol", shlex.split("ping -c 5 strongswan.moon.com"))

            # Deactivate IPSEC Connection
            if pLvl > 3:
                print("swanctl --terminate --ike home")
            docker.execute("carol", shlex.split("swanctl --terminate --ike home"))
        except:
            if pLvl > 1:
                print("Possible Error in IPSEC Loop")

        # Check timer if > max time break loop
        if time.perf_counter() - startrun_tic > max_run_time:
            break
        else:
            continue
    # END IPSEC LOOP 
    # END Single Constraint Function

    #Stop Wireshark Logging

    # Move Data Files from Carol to local machine (or volume) and rename
    date_time = time.strftime("%Y%m%d_%H%M")

    LogName = ("./charon." + date_time + "." + C_constraint + "_" + str(C_vals[i]) + 
        "." + "iter_" + str(ipsec_N) + ".log")
    docker.copy(("carol", "/var/log/charon.log"), LogName)

     #Reload Settings which forces a new Charon Log File
    docker.execute("carol", shlex.split("echo 'newlog' > /var/log/charon.log"))
    docker.execute("carol", shlex.split("swanctl --reload-settings"))

    #print run stats and estimated remaining time
    total_time = time.perf_counter() - startrun_tic
    L1_time = time.perf_counter() - L1_tic
    EstRemTime = (len(C_vals)-i) * L1_time
    if pLvl > 1:
        print("Total Time: " + str(total_time) + " seconds")
        print("Last Run Time: " + str(L1_time) + " seconds")
        print("Estimated Remaining Time: " + str(EstRemTime) + " seconds")
    
    #check timer if > max time break loop
    if time.perf_counter() - startrun_tic > max_run_time:
        break

   
    #docker.execute("carol", shlex.split("rm /var/log/charon.log"))
    #docker.execute("carol", shlex.split("touch /var/log/charon.log"))

    #save run stats to file
    file1 = open("runstats.txt","a")
    file1.writelines(LogName + "; " +
        "Additional Params: " + C_AddParams + 
        "; Total Time: " + str(total_time) + " seconds\n")
    file1.close()

#END Constraint 1 Loop

# If not done previously Move all Data Files from Carol to local machine

if pLvl > 0:
    print(" -- Wrapping Up Run -- ")

#print run stats
total_time = time.perf_counter() - startrun_tic
if pLvl > 1:
    print("Total Time: " + str(total_time) + " seconds")



#remove all TC constraints
try:
    docker.execute("carol", shlex.split("tc qdisc del dev eth0 root"))
    docker.execute("moon", shlex.split("tc qdisc del dev eth0 root"))
except:
    if pLvl > 1:
        print("Possible Error removing TC constraints")

## Stop Docker Containers
docker.compose.down()
