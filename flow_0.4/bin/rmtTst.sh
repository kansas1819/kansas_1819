#!/bin/bash
source /home/sikshana/.bashrc
mkdir -p /home/sikshana/test_$(date -I)/csv
/home/sikshana/sas/flow/bin/setupsample.sh
cd /home/sikshana/test_$(date -I)/
ln -s /home/sikshana/sas/flow/pdf/Snakefile /home/sikshana/test_$(date -I)/Snakefile && /opt/anaconda3/bin/snakemake -n --printshellcmds 
