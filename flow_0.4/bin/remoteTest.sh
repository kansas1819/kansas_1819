#!/bin/bash
USERNAME=sikshana
HOSTS="192.168.0.14 192.168.0.15 192.168.0.13 192.168.0.16" #the IP addresses of csas laptops in order csas1 through csas4
for HOSTNAME in ${HOSTS}
do
    ssh -o StrictHostKeyChecking=no -l ${USERNAME} ${HOSTNAME} "~/sas/flow/bin/rmtTst.sh" & 
done
