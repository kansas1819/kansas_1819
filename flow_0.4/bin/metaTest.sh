#!/bin/bash
rm -rf /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')
source /home/sikshana/.bashrc
mkdir -p /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')
cd /home/sikshana/run_$(date -d '1 day ago' '+%Y-%m-%d')/ && find . -iname *.log | xargs -i{} grep -i 'error\|mismatch' {}  >/tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/foo.log

if [ $(less /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/foo.log |wc -l) == 0 ]
then
	touch /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/NOerrors
else
	touch /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/Errors
fi 

cd /home/sikshana/run_$(date -d '1 day ago' '+%Y-%m-%d')/pdfgen/ && cd $(shuf -n1 -e *) && cd $(shuf -n1 -e *)
pdftk ${PWD##*/}-core.pdf cat 1 2 $(pdftk ${PWD##*/}-core.pdf dump_data | grep NumberOfPages | cut -c16-19) output /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/core.pdf 
pdftk ${PWD##*/}-lang.pdf cat 1 2 $(pdftk ${PWD##*/}-lang.pdf dump_data | grep NumberOfPages | cut -c16-19) output /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/lang.pdf
cp ~/sas/flow/forms/buffers/bufC1/overlay45.pdf /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/ 
cp ~/sas/flow/forms/buffers/bufC2/overlay-C2.pdf /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/
cp ~/sas/flow/forms/buffers/bufl1/overlayL1.pdf /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/
cp ~/sas/flow/forms/buffers/bufl1/overlayL1.pdf /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/
cp ~/sas/flow/forms/buffers/bufl2/overlay-L2.pdf /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')/
cd /tmp/pdfgen_$(date -d '1 day ago' '+%Y-%m-%d')
pdftk overlay* lang.pdf core.pdf output pdf2test_$(date -d '1 day ago' '+%Y-%m-%d').pdf

