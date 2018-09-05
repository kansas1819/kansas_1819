import pandas as pd
import numpy as np
import argparse
import random

def main():
    parser = argparse.ArgumentParser(
        '''
        Dump a sample set of school csv for testing purposes.
        ''')
    parser.add_argument("--csv",
                        required=True,
                        help="Work with this csv.")
    parser.add_argument("--output",
                        default='out.csv',
                        help="Write the final data to this file.")
    parser.add_argument("--sample",
                        default=30,
                        help="Sample num schools.")

    #opts = parser.parse_args('--csv CHITRADURGA.csv'.split())
    opts = parser.parse_args()
    df = pd.read_csv(opts.csv)
    slist =  list(df.SCHOOL_ID.unique())
    print len(slist)
    print slist, opts.sample
    schools = random.sample(slist, int(opts.sample))
    ndf = df[df['SCHOOL_ID'].isin(schools)]
    ndf.to_csv(opts.output, index=False)

if __name__ == '__main__':
    main()
    
