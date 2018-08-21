#!/bin/bash

csvfiles=`ls ../csv`
for csv in $csvfiles; do
    folder=${csv%.*}
    mkdir ${folder}
done

echo "Setting up the dists"	   
/usr/bin/time -o setup.txt make all > run.log 2>&1
echo "Done setting up the dists"

dists=`ls -d */`
for dist in $dists; do
    date
    echo "Generating pdf for $dist"
    pushd  $dist
    /usr/bin/time -o ${dist}.txt make all > all.log 2>&1
    popd
done

 
