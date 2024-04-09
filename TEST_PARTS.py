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

ConfigFile = "DataCollect_delay.json"
ymlConfig = "DataCollect_delay.yaml"

## IMPORT CONFIGURATION FILE
# Open the JSON file
with open('PostQuantumIKEv2/' + ConfigFile) as file:
    JSONConfig = json.load(file)

with open('PostQuantumIKEv2/' + ymlConfig) as file:
    YAMLConfig = yaml.safe_load(file)

# Breakup the JSON file into different dictionaries
JCoreConfig = JSONConfig.get('CoreConfig')
JCarolConfig = JSONConfig.get('Carol_TC_Config')
JMoonConfig = JSONConfig.get('Moon_TC_Config')

CoreConfig = YAMLConfig.get('CoreConfig')
CarolConfig = YAMLConfig.get('Carol_TC_Config')
MoonConfig = YAMLConfig.get('Moon_TC_Config')

if JCoreConfig == CoreConfig:
    print("Core Configurations Match")

if JCarolConfig == CarolConfig:
    print("Carol Configurations Match")

if JMoonConfig == MoonConfig:
    print("Moon Configurations Match")

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