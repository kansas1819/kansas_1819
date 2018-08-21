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
    arr = df.drop(df.columns[[0,1]], axis=1).values
    if 0 in arr:
        print("CSV test for {}: FAILED".format(opts.rundir))
        sys.exit(1)
    else:
        print("CSV test for {}: PASSED.".format(opts.rundir))

if __name__ == '__main__':
    main()
