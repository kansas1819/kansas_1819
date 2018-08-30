#!/usr/bin/env python

import pandas as pd
import numpy as np
import argparse
import sys

def main():
    parser = argparse.ArgumentParser("Check the output csv for all ones.")
    parser.add_argument('--rundir', required=True, help='sdaps run dir')
    opts = parser.parse_args()
    df = pd.read_csv('{}/db/data_1.csv'.format(opts.rundir))
    r,c = df.shape
    df1 = df.iloc[0:int(r/2),2:]
    df0 = df.iloc[int(r/2):,2:]
    arr0 = df0.values
    arr1 = df1.values
    print(df0.tail())
    print(df1.tail())
    if 1 in arr0 or 0 in arr1:
        print("CSV test for {}: FAILED".format(opts.rundir))
        sys.exit(1)
    else:
        print("CSV test for {}: PASSED.".format(opts.rundir))

if __name__ == '__main__':
    main()
