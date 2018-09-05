#!/usr/bin/env python

import pandas as pd
import numpy as np
import argparse
import re
import os
import subprocess

def check_log(opts):
    matches = []
    with open(opts.log, "r") as logfp:
        for line in logfp:
            mo = opts.errpattern.match(line)
            if not mo: continue
            matches.append([opts.log, mo.groups()])
    return matches

def classify_errs(errs,opts):
    errdata={}
    for logfile, err in errs:
        if not errdata.has_key(logfile):
            errdata[logfile] = []
        m = opts.wrongsurveyid.match(err[0])
        if m:
            errdata[logfile].append([m.group(1), "wrong survey"])
        n = opts.matrixerr.match(err[0])
        if n:
            errdata[logfile].append([n.group(1), "Scan problem or wrong sheet"])
    if not errdata:
        return errdata
    else:
        return cleanDupes(errdata)

def cleanDupes(errdata):
    '''
    There can be multiple warnings for a single sheet. This func makes sure that
    only one page is returned even if multiple errors point to the same sheet.
    '''
    nerrs = {}
    errarr = []
    logfile = errdata.keys()[0]
    for page, reason in errdata[logfile]:
        if not nerrs.has_key(page):
            nerrs[page] = reason
    for k,v in nerrs.iteritems():
        errarr.append([k,v])
    return {logfile: errarr}

def analyzeLog(opts):
    d = check_log(opts)
    data = classify_errs(d,opts)
    return data

def scoreQuestion(x):
    ans = ['A','B','C','D']
    d = np.where(x==1)[0]
    if len(d) > 1:
        return "M"
    if len(d) == 0:
        return "Z"
    return ans[d[0]]

def  score(x):
    y = np.reshape(x.values,(-1,4))
    data = [scoreQuestion(a) for a in y]
    return pd.Series(data)

def copyErrTiff(edf,opts):
    pageindex = list(edf.index)
    pages = ','.join(map(str,pageindex))
    cmd = 'tiffcp {}/tiff/full.tiff,{} {}/err.tiff'.format(
        opts.rundir, pages,opts.rundir)
    subprocess.check_output(cmd.split())

def main():
    parser = argparse.ArgumentParser(
    '''
    Transform the csv from sdaps into a readable format 
    and create an error file "err.csv" for recognition 
    problems by analyzing the sdaps log file.
    ''')
    parser.add_argument('--rundir', required=True)
    opts = parser.parse_args()

    # setup patterns to analyze the logfiles
    opts.errpattern = re.compile(r'(^Warning.*)')
    opts.wrongsurveyid = re.compile(r'.*wrong\s+survey\s+ID.*tif+,\s+(\d+).*')
    opts.matrixerr= re.compile(r'^Warning.*tif.*\s+(\d+).*Matrix.*')

    # setup input and output files in tthe opts dict
    rundir = opts.rundir
    opts.log = '{}/db/log'.format(rundir)
    opts.csv = '{}/db/data_1.csv'.format(rundir)
    opts.ocsv = '{}/final.csv'.format(rundir)
    opts.errcsv = '{}/err.csv'.format(rundir)
              
    #print logdata
    # read the sdaps csv and transform it
    df = pd.read_csv(opts.csv)
    sdf = pd.read_csv('{}/.pcsv'.format(rundir))
    sdf['error'] = False
    sdf = sdf[['schid','std','stuid','lang','group','error']]
    df.drop(df.columns[0:2], axis=1, inplace=True)
    zdf = df.apply(score, axis=1)
    fdf = pd.concat([sdf,zdf],axis=1)
    logdata = analyzeLog(opts)         
    # add err data if any
    for log,val in logdata.iteritems():
        for page,reason in val:
            fdf.iloc[int(page),5] = True
    errdf = fdf[fdf['error']==True].copy()
    errdf.drop(errdf.columns[6:],axis=1,inplace=True)
    errdf['reason'] = None
    for log,val in logdata.iteritems():
        for i,(page,reason) in enumerate(val):
            errdf.iloc[i,6] = reason
    errdf['log'] = opts.log
    # write out the csv files
    errdf.to_csv(opts.errcsv)
    copyErrTiff(errdf,opts)

    fdf.to_csv(opts.ocsv)
    errs,cols = errdf.shape
    if not errs:
        print "No recognition errors."
    else:
        print "{} Recognition errors found.".format(errs)

if __name__=='__main__':
    main()
