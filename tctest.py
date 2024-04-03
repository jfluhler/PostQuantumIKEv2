import subprocess
import shlex
import tcconfig

# Example tc command to invoke a delay of 200ms
SetCon = "tc qdisc add dev ens160 root netem delay 200ms"


interface="ens160"
constraint1="delay"
Cvalue1="200ms"

# Example of building a command from variables
BuildCon = ("tc qdisc add dev " + interface + " root netem " 
            + constraint1 + " " + Cvalue1)

# Example of updating an existing constraint.
ChangeCon = ("tc qdisc replace dev " + interface + " root netem " 
            + constraint1 + " " + Cvalue1)

# Example of removing all contrainsts from an interface
ClearCon = "tc qdisc del dev ens160 root"

# Example of displaying any constraints on an interface.
ShowCon = "tc qdisc show dev ens160"

# Clear all constraints on the interface.
#    NOTE This is kinda important because the constraints are appliied at
#    the system level! This means if python crashes for example the constraints
#    still exist. 
print(" -- CLEARING tc Constraints -- ")
print(ClearCon)
subprocess.run(shlex.split(ClearCon))



print("adding constrain:")
print(BuildCon)

subprocess.run(shlex.split(BuildCon))

# Example loop that updated the delay constraint and then pings google.
for Val1 in range(0,200,50):
    ChangeCon = ("tc qdisc replace dev " + interface + " root netem " 
            + constraint1 + " " + str(Val1)+"ms")
    print(ChangeCon)
    subprocess.run(shlex.split(ChangeCon))
    subprocess.run(shlex.split("ping -c 5 google.com"))


# Clear all constraints on the interface.
#    NOTE This is kinda important because the constraints are appliied at
#    the system level! This means if python crashes for example the constraints
#    still exist. 
print(" -- CLEARING CHANGES -- ")
print(ClearCon)
subprocess.run(shlex.split(ClearCon))
subprocess.run(shlex.split("ping -c 5 google.com"))
