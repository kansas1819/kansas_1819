#!/usr/bin/env python
import pandas as pd
import numpy as np
import os
import sys

csvdir  = sys.argv[1]
csvodir = sys.argv[2]
csvfiles = []
for rootdir, subdirs, filenames in os.walk(csvdir):
    for f in filenames:
        if f.endswith(".csv"):
            csvfiles.append('{}/{}'.format(rootdir, f))

os.makedirs(csvodir, exist_ok=True)

for csvf in csvfiles:
    df = pd.read_csv(csvf)
    ocsv = '{}/{}'.format(csvodir,os.path.basename(csvf))
    df.groupby(['SCHOOL_ID','STANDARD']).head(1).to_csv(ocsv, index=False)

            
