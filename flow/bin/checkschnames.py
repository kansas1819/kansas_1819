#!/usr/bin/env python
import pandas as pd
import numpy as np
import argparse
import re
import ConfigParser
import sys
import os

def repl(x):
    c = re.sub(r'\W+', ' ', x)
    if len(c) > 60:
        c = re.sub(r'GOVER\w+\s+LOW\w+\s+PRI\w+\s+SCHOOL','GLPS',c)
        c = re.sub(r'GOVER\w+\s+HIG\w+\s+PRI\w+\s+SCHOOL','GHPS',c)
        c = re.sub(r'HIG\w+\s+PR\w+\s+SCHOOL','HPS',c)
        c = re.sub(r'LOW\w+\s+PR\w+\s+SCHOOL','LPS',c)
        c = re.sub(r'HIG\w+\s+SEC\w+\s+SCHOOL','HSS',c)
        c = re.sub(r'HIG\w+\s*SCHOOL','HS',c)
        c = re.sub(r'\s+',' ',c)
        c = c[0:60]
    return c

def ntrunc(x):
    c = x
    if len(x) > 30:
        c = x[0:30]
    return c

def lang(x):
    return (x.replace('5-Kannada', 'K').replace('18-Urdu', 'U')
            .replace('10-Marathi', 'M').replace('19-English', 'E')
            .replace('8-Malayalam', 'Y').replace('16-Tamil', 'T')
            .replace('3-Gujarati', 'G')
            .replace('17-Telugu', 'L').replace('4-Hindi', 'H'))

def checkIntFields(df,opts):
    sections = ['School Id', 'Student Id', 'Crc Id', 'Brc Id', 'District Id', 'Standard']
    for section in sections:
        checkIntField(df, section, opts)
        
def checkIntField(df, section, opts):
    field = opts.cfg.get(section, 'field')
    flen = opts.cfg.getint(section, 'length')
    print "Checking for maxlength of {} on field {}.".format(flen, field)
    ndf = df[df[field].astype(str).map(len) > flen]
    err = False
    if not ndf.empty:
        print "Length of field {} is greater than {}.".format(field, flen)
        print ndf
        err = True
    if section != 'Lang':
        if df[field].dtype != np.int64:
            print "Field {} contains non integers.".format(field)
            err = True

    
def main():
    parser = argparse.ArgumentParser(
        '''
        Check the school names, use acronymns for some combinations
        and finally if the length >55, truncate it to 55.
        ''')
    parser.add_argument("--csv",
                        required=True,
                        help="Work with this csv.")
    parser.add_argument("--mapping",
                        default='name_mapping.csv',
                        help="Write out the mapping info to this file.")
    parser.add_argument("--output",
                        default='out.csv',
                        help="Write the final data to this file.")
    parser.add_argument("--config",
                        required=True,
                        default='config.ini',
                        help="Read the config from this file.")
    #opts = parser.parse_args('--csv CHITRADURGA.csv'.split())
    opts = parser.parse_args()
    config = ConfigParser.ConfigParser()
    if not os.path.isfile(opts.config):
        print "File {} does not exist.".format(opts.config)
        sys.exit(1)
    config.read(opts.config)
    opts.cfg = config
    df = pd.read_csv(opts.csv)
    colstokeep = [
        u'DISTRICT_ID', u'DISTRICT_NAME', u'BRC_ID',
        u'BRC_NAME', u'CRC_ID', u'CRC_NAME', u'SCHOOL_ID',
        u'SCHOOL_NAME', u'STU_MEDIUM', u'STANDARD',
        u'CHILD_ENROLL_NO', u'STU_NAME']
    df = df[colstokeep]
    checkIntFields(df,opts)
    df['SCH_NAME_ORIG'] = df['SCHOOL_NAME']
    df['SCHOOL_NAME'] = df.SCHOOL_NAME.apply(repl)
    df['STU_NAME'] = df.STU_NAME.apply(repl)
    df['LANG'] = df.STU_MEDIUM.apply(lang)
    checkIntField(df,'Lang',opts)
    cols = ['SCHOOL_ID','SCH_NAME_ORIG','SCHOOL_NAME', 'LENGTH']
    schdf = df.copy()
    schdf.drop_duplicates(['SCHOOL_ID'], inplace=True)
    schdf.loc[:,'LENGTH'] = schdf['SCHOOL_NAME'].apply(lambda x: len(x))
    ss = schdf.sort_values(['LENGTH'], ascending=False)
    # #print ss.columns
    ss[cols].to_csv(opts.mapping)
    df.to_csv(opts.output, index=False)

if __name__ == '__main__':
    main()
    msg = '''
    Please check the  pdf for the top 10 schools in the csv mapping file to 
    make sure that the school name does not encroach into the question paper 
    set boxes.
    '''
    print msg
    
