#!/bin/bash
ips=($(hostname -I))
for ip in "${ips[0]}"
do 
HOST=$ip
done

if [ ${HOST} == "192.168.0.14" ] # csas1
then 
echo setting up the csv folder for csas1
cd ~/sas/sas2018/ && cp -t ~/run_$(date -I)/csv/ BAGALKOT.csv BENGALURU_U_NORTH.csv CHIKKAMANGALURU.csv DHARWAD.csv KOLAR.csv SHIVAMOGGA.csv UTTARA_KANNADA.csv GADAG.csv RAICHUR.csv
elif [ ${HOST} == "192.168.0.15" ] # csas2
then 
echo setting up the csv folder for csas2 
cd ~/sas/sas2018/ && cp -t ~/run_$(date -I)/csv/ BALLARI.csv BENGALURU_U_SOUTH.csv CHITRADURGA.csv HASSAN.csv MANDYA.csv TUMAKURU.csv UTTARA_KANNADA_SIRSI.csv KOPPAL.csv
elif [ ${HOST} == "192.168.0.13" ] # csas3
then 
echo setting up the csv folder for csas3
cd ~/sas/sas2018/ && cp -t ~/run_$(date -I)/csv/ BELAGAVI_CHIKKODI.csv CHAMARAJANAGARA.csv DAKSHINA_KANNADA.csv HAVERI.csv MYSURU.csv TUMAKURU_MADHUGIRI.csv YADAGIRI.csv KALBURGI.csv
elif [ ${HOST} == "192.168.0.16" ] # csas4
then 
echo setting up the csv folder for csas4 
cd ~/sas/sas2018/ && cp -t ~/run_$(date -I)/csv/ BENGALURU_RURAL.csv CHIKKABALLAPURA.csv DAVANAGERE.csv KODAGU.csv RAMANAGARA.csv UDUPI.csv BIDAR.csv VIJAYAPURA.csv BELAGAVI.csv
fi

