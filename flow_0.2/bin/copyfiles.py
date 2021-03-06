#!/usr/bin/env python
import pandas as pd
import re
import argparse
import os
import subprocess
import errno
import glob
from multiprocessing import Pool
import sys
import pickle

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def repl(x):
    c = re.sub(r'\W+',' ',x)
    c = re.sub(r'\s+','_',c)
    return c

def copyfiles(key,group,opts):
    dist,crc,brc = key
    foldergrp = '/'.join(key)
    folder = '{}/{}/'.format(opts.to,foldergrp)
    print "Copying to {}.".format(folder)
    # create folder
    mkdir_p(folder)
    print "making folder {}".format(folder)
    schools = list(group['SCHOOL_ID'].unique())
    for school in schools:
        langpdf = '{}/{}/{}-lang.pdf'.format(opts.dir, school, school)
        corepdf = '{}/{}/{}-core.pdf'.format(opts.dir, school, school)
        for pdf in [langpdf,corepdf]:
            cmdstr = '/bin/cp {} {}'.format(pdf, folder)
            print cmdstr
            subprocess.check_output(cmdstr.split())

def sizepdf(pdf):
    cmd = 'pdftk {} dump_data output'.format(pdf)
    #print cmd
    output = subprocess.check_output(cmd.split())
    outarr = output.split("\n")
    for e in outarr:
        if re.match('NumberOf', e):
            break
    n,pages = e.split(':')
    pages = int(pages)
    fname = os.path.basename(pdf)
    f = os.path.splitext(fname)[0]
    return (f,pages)
    
def checkNumpages(df,opts):
    csv = os.path.basename(opts.csv)
    block = os.path.splitext(csv)[0]
    gpath = '{}/*/*/*paper*.pdf'.format(opts.dir, block)
    files = glob.glob(gpath)
    pool = Pool(4)
    data = pool.map(sizepdf, files)
    fdata = []
    for x,y in data:
        d,t = x.split('_')
        fdata.append((int(d), t , int(y)))
    pdf = pd.DataFrame(fdata,columns=['SCHOOL_ID', 'paper', 'count'])
    #with open("pickle.db","wb") as fp:
    #   pickle.dump(pdf,fp)
    #print pdf.columns
    xpdf = pdf.pivot_table(index='SCHOOL_ID', columns='paper', values='count').reset_index()
    odf = df.groupby('SCHOOL_ID').size().reset_index(name='count')
    odf.sort_values(['SCHOOL_ID'], inplace=True)
    mdf = pd.merge(odf,xpdf, on='SCHOOL_ID')
    mdf['ncount'] = mdf['count'] + 1
    if not mdf['ncount'].equals(mdf['paper2']):
        print "Counts donot match on core pdf"
        sys.exit(1)
    if not mdf['ncount'].equals(mdf['paper1']):
        print "Counts donot match on lang pdf"
        sys.exit(1)
    mdf.to_csv(opts.ocsv)
    schs = mdf.SCHOOL_ID.size()
    students = mdf.ncounts.sum() - schs
    print "Page Counts match for the schools in {} district.".format(os.path.basename(opts.dir))
    print "Total Schools: {}".format(schs)
    print "Total Students: {}".format(students)


def main():
    parser = argparse.ArgumentParser("Check Pagecounts in the pdfs with the csv used to generate the pdfs.")
    parser.add_argument("--dir", required=True, help="District run directory to process.")
    parser.add_argument("--csv", required=True, help="CSV for the district.")
    parser.add_argument("--ocsv", required=True, help="Output csv by school and count..")
    opts = parser.parse_args()

    # check options
    if not os.path.isdir(opts.dir):
        print "Directory {} does not exist.".format(opts.dir)
        sys.exit(1)
    if not os.path.isfile(opts.csv):
        print "File {} does not exist.".format(opts.csv)
        sys.exit(1)

    df = pd.read_csv(opts.csv)
    checkNumpages(df,opts):


main()
