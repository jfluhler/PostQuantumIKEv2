import json
import os


# Open the JSON file
with open('PostQuantumIKEv2/DataCollect.json') as file:
    JSONConfig = json.load(file)

# Assign values to variables with default values
CoreConfig = JSONConfig.get('CoreConfig')
CarolConfig = JSONConfig.get('Carol_TC_Config')
MoonConfig = JSONConfig.get('Moon_TC_Config')

# Print the dictionary values
print("\n\nCORE CONFIG")
for x in CoreConfig:
  print("\t" + x + ':', CoreConfig[x])

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



