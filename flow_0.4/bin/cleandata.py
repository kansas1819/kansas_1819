#!/usr/bin/env python

import pandas as pd

columns = [u'ACA_YEAR', u'DISTRICT_ID', u'DISTRICT_NAME', u'BRC_ID', u'BRC_NAME',
       u'CRC_ID', u'CRC_NAME', u'SCHOOL_ID', u'SCHOOL_NAME', u'SCHOOL_MEDIUM',
       u'STANDARD', u'CHILD_ENROLL_NO', u'STU_NAME', u'STU_DOB',
       u'STU_RELEGION', u'GENDER', u'CATEGORY', u'BPL_STATUS', u'DISABILITY']
dropcols = [u'STU_DOB',
            u'STU_RELEGION', u'GENDER',
            u'CATEGORY', u'BPL_STATUS',
            u'DISABILITY']

def select49(df):
    ndf = df[(df.STANDARD==4.0)|
             (df.STANDARD==5.0)|
             (df.STANDARD==6.0)|
             (df.STANDARD==7.0)|
             (df.STANDARD==8.0)|
             (df.STANDARD==9.0)]
    return ndf

def ra(x):
    r=['E', 'G', 'H', 'K', 'M', 'L', 'U', 'T', 'Y']
    s = random.sample(r,1)
    return s[0]

df = pd.read_csv('schoolfull.csv')
df.drop(dropcols, axis=1, inplace=True)
df = select49(df)
df.loc[:,'LANG'] = df.groupby('SCHOOL_ID')['SCHOOL_ID'].transform(ra)
for name, group in df.groupby(['DISTRICT_NAME']):
    group.to_csv('{}.csv'.format(name))

