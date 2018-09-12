#!/bin/bash
USERNAME=sikshana
HOSTS="192.168.0.14 192.168.0.15 192.168.0.13 192.168.0.16" #the IP addresses of csas laptops in order csas1 through csas4
SCRIPT="source /home/sikshana/.bashrc; mkdir -p /home/sikshana/run_$(date -I)/csv;  /home/sikshana/sas/flow/bin/setupcsv.sh; cd /home/sikshana/run_$(date -I)/; ln -s /home/sikshana/sas/flow/pdf/Snakefile ./Snakefile; /opt/anaconda3/bin/snakemake -n --printshellcmds" 
#rsync -avz sikshana@192.168.0.15:/home/sikshana/sas/flow_0.3/ ~/sas/flow_0.3; 
for HOSTNAME in ${HOSTS}
do
ssh -o StrictHostKeyChecking=no -l ${USERNAME} ${HOSTNAME} "${SCRIPT}" & 
done
