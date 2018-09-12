#!/bin/bash
ips=($(hostname -I))
for ip in "${ips[0]}"
do
HOST=$ip
done

if [ ${HOST} == "192.168.0.14" ] # csas1
then
echo setting up the csv folder for csas1
cd ~/sas/new_data_sample/ && cp -t ~/test_$(date -I)/csv/ BAGALKOT.csv
elif [ ${HOST} == "192.168.0.15" ] # csas2
then
echo setting up the csv folder for csas2
cd ~/sas/new_data_sample/ && cp -t ~/test_$(date -I)/csv/ BALLARI.csv
elif [ ${HOST} == "192.168.0.13" ] # csas3
then
echo setting up the csv folder for csas3
cd ~/sas/new_data_sample/ && cp -t ~/test_$(date -I)/csv/ CHIKKODI.csv
elif [ ${HOST} == "192.168.0.16" ] # csas4
then
echo setting up the csv folder for csas4
cd ~/sas/new_data_sample/ && cp -t ~/test_$(date -I)/csv/ BEN_RURAL.csv
fi

