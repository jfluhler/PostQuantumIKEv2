#!/bin/bash

echo "Initiating testing..."

user=$(whoami)
swanDir=/home/$user/docker/pq-strongswan
dateTime="date +%D,%t%T:%N"
function prompt_for_test_num {
	read -p "How many tests to run? : " testNum
}
dockCompUp="sudo docker-compose -f $swanDir/docker-compose.yml up -d"
function start_docker {
	$dateTime >> docker_log.txt
	$dockCompUp 2>> docker_log.txt
	echo "Started containers." >> docker_log.txt
	echo "" >> docker_log.txt
}
dockCompStop="sudo docker-compose -f $swanDir/docker-compose.yml stop"
function stop_docker {
	$dateTime >> docker_log.txt
	$dockCompStop 2>> docker_log.txt
	echo "Stopped containers." >> docker_log.txt
	echo "" >> docker_log.txt
}
ping_mTc="sudo docker exec -ti moon ping -c 10 carol"
ping_cTm="sudo docker exec -ti carol ping -c 10 moon"
function ping_test {
	$dateTime >> ping_results.txt
	$ping_mTc >> ping_results.txt
	echo "" >> ping_results.txt
	$dateTime >> ping_results.txt
	$ping_cTm >> ping_results.txt
	echo "" >> ping_results.txt
}

######## BEGIN EXECUTION ########

prompt_for_test_num
echo "Performing $testNum tests..."

### LOOP START ###
for i in $(seq 1 $testNum);
do
echo "Starting test $i of $testNum."

#echo "Starting moon and carol"
start_docker

#echo "Ping test in progress..."
ping_test

#echo "Stopping moon and carol"
stop_docker

echo "Test $i of $testNum complete."
done
### LOOP END ###

######## END EXECUTION ########

#echo ":::END OF SCRIPT:::"
echo "Exiting..."
