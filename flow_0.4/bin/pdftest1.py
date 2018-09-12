#!/usr/bin/env python
import pandas as pd
import numpy as np
import os, sys
import subprocess
from collections import defaultdict
import tempfile
from multiprocessing import Pool
import argparse
import shutil

def sampleSize(
    population_size,
    margin_error=.05,
    confidence_level=.99,
    sigma=1/2
):
    """
    Calculate the minimal sample size to use to achieve a certain
    margin of error and confidence level for a sample estimate
    of the population mean.
    Inputs
    -------
    population_size: integer
        Total size of the population that the sample is to be drawn from.
    margin_error: number
        Maximum expected difference between the true population parameter,
        such as the mean, and the sample estimate.
    confidence_level: number in the interval (0, 1)
        If we were to draw a large number of equal-size samples
        from the population, the true population parameter
        should lie within this percentage
        of the intervals (sample_parameter - e, sample_parameter + e)
        where e is the margin_error.
    sigma: number
        The standard deviation of the population.  For the case
        of estimating a parameter in the interval [0, 1], sigma=1/2
        should be sufficient.
    """
    alpha = 1 - (confidence_level)
    # dictionary of confidence levels and corresponding z-scores
    # computed via norm.ppf(1 - (alpha/2)), where norm is
    # a normal distribution object in scipy.stats.
    # Here, ppf is the percentile point function.
    zdict = {
        .90: 1.645,
        .91: 1.695,
        .99: 2.576,
        .97: 2.17,
        .94: 1.881,
        .93: 1.812,
        .95: 1.96,
        .98: 2.326,
        .96: 2.054,
        .92: 1.751
    }
    if confidence_level in zdict:
        z = zdict[confidence_level]
    else:
        from scipy.stats import norm
        z = norm.ppf(1 - (alpha/2))
    N = population_size
    M = margin_error
    numerator = z**2 * sigma**2 * (N / (N-1))
    denom = M**2 + ((z**2 * sigma**2)/(N-1))
    return int(numerator/denom)

def getCsvFiles(folder):
    '''
    Return a list of the CSV files in the folder
    '''
    csvfiles = []
    for rootdir, subdirs, cfiles in os.walk(folder):
        for csvf in cfiles:
            if csvf.endswith(".csv"):
                csvfiles.append('{}/{}'.format(rootdir, csvf))
    return csvfiles

def xtract(pdf,page,npdf,tmpdir):
    cmd = ['pdftk', pdf, 'cat', str(page), 'output', '{}/{}'.format(tmpdir,npdf)]
    print(' '.join(cmd))
    p = subprocess.run(' '.join(cmd), shell=True, check=True)



def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def pdfTypes(df):
    pdfd = defaultdict(list)
    std45 = df[df.STANDARD.isin([4,5])]
    for i,chunk in enumerate(chunks (std45.npdf.values.tolist(), 50)):
        pdfd['std45{}'.format(i)] = chunk
    std69 = df[df.STANDARD.isin([6,7,8,9,0])]
    for i,chunk in enumerate(chunks (std69.npdf.values.tolist(), 50)):
        pdfd['std69{}'.format(i)] = chunk
    return pdfd
        
def extractPages(opts):
    df = opts.df
    testdir = '{}/test'.format(opts.rundir)
    papertype = opts.papertype
    data = df[['pdf', 'page','npdf']].values.tolist()
    district = df.DISTRICT_NAME.unique().tolist()[0].replace(' ','_')
    pdfd = pdfTypes(df)

    with tempfile.TemporaryDirectory() as tmpdir:
        z = [x.append(tmpdir) for x in data]
        with Pool(processes=4) as pool:
            pdf = pool.starmap(xtract, data)

        for key, value in pdfd.items():
            if key.startswith('std45'):
                pt = '45'
            else:
                pt = '69'
            opath = '{}/{}/{}/{}/{}.pdf'.format(testdir, district, papertype, key, pt)
            dirname = os.path.dirname(opath)
            os.makedirs(dirname, exist_ok=True)
            pdfs = ['{}/{}'.format(tmpdir,x) for x in value]
            cmd = ['pdftk'] + pdfs + ['cat', 'output', opath]
            subprocess.run(' '.join(cmd), shell=True, check=True)
            
            stmppdf = '{}/forms/{}-{}-stamp.pdf'.format(opts.flowdir, pt, papertype)
            opaths = '{}/{}/{}/{}/{}-stamp.pdf'.format(testdir, district, papertype,key,pt)
            cmd = ['pdftk', opath, 'multistamp', stmppdf, 'output', opaths]
            subprocess.run(' '.join(cmd), shell=True, check=True)
            dbdpath = os.path.dirname(opaths)
            dbspath = '{}/forms/{}/{}/db'.format(opts.flowdir, papertype, pt)
            cmd = 'cp -r {} {}'.format(dbspath, dbdpath)
            subprocess.run(cmd, shell=True, check=True)


def processDistrict(opts):
        
    df = pd.read_csv(opts.csv).sort_values(['SCHOOL_ID', 'STANDARD','STU_NAME'])
    df['page'] = df.groupby(['SCHOOL_ID']).cumcount() + 2

    popsize = df.shape[0]
    conflevel = 95
    confinter = 5
    sigma = 1/2
    nsamples = sampleSize(popsize)
    #nsamples=600
    print("Sampling {} sheets.".format(nsamples))
    for ptype in ['core', 'lang']:
        sdf = df.sample(nsamples)
        sdf['npdf'] = sdf.apply(lambda x: '{}-{}-{}.pdf'.format(x.SCHOOL_ID,x.STANDARD, x.page),axis=1)
        sdf['pdf'] = sdf.apply(lambda x: '{}/{}/{}-{}.pdf'.format(
            opts.pdfdir,x.SCHOOL_ID, x.SCHOOL_ID, ptype),axis=1)
        opts.papertype=ptype
        opts.df = sdf
        extractPages(opts)

        
def main():
    parser = argparse.ArgumentParser(
        '''Generate test environment for checking pdf by sampling the 
        generated pdf with a confidence level of 95% and error margin of +- 5%.
        ''')
    parser.add_argument("--rundir", nargs='?', default=os.getcwd(), help="Create the tree in this dir.")
    parser.add_argument("--flowdir",required=True, help="Flow directory path for config files, etc.")
    parser.add_argument("--csv",required=True, help="csv file to process.")
    optstring = '--rundir sample --csvdir ../sample_csvs --flowdir /home/sikshana/sas/flow'
    #opts = parser.parse_args(optstring.split())
    opts = parser.parse_args()
    if not os.path.isfile(opts.csv):
        print('Csv file {} does not exist'.format(opts.csv))
        sys.exit(1)
    if not os.path.isdir(opts.rundir):
        print('Run folder {} does not exist'.format(opts.rundir))
        sys.exit(1)
        
    #csvfiles = getCsvFiles(opts.csvdir)
    #csvl = len(csvfiles)
    distname = os.path.splitext(os.path.basename(opts.csv))[0]
    print('Processing PDF({}) for testing.'.format(distname))
    opts.pdfdir = '{}/pdfgen/{}'.format(opts.rundir, distname)
    processDistrict(opts)
        
if __name__=='__main__':
    main()
