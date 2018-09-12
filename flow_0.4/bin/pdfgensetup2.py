#!/usr/bin/env python
import sys
import os, errno
import pandas as pd
import numpy as np
import string
from string import Template
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from subprocess import call
import re
import argparse

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

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
                                 
def dirName(groupkeys, opts):
    if isinstance(groupkeys, tuple):
        return '/'.join(map(str, groupkeys))
    else:
        return '{}/{}'.format(opts.rundir,str(groupkeys))
    
def genBarCodePng(x):
    ''' 
    Generate two qrcodes. One for core and one for
    language in the <schid>/img directory.
    qrcode format: <schid>:<standard>:<studentid>:<l | c>
    Takes a tuple as input.
      x: (<dir>, <schoolid>,(<code-l>,<code-c>))
    '''
    print ("Processing school {}".format(x[1]))
    folder, schoolid, codes = x
    dir = "{}/{}/img".format(folder, schoolid)
    mkdir_p(dir)
    for sqrcode in codes:
        stuid = sqrcode[0]
        ptype = ['l','c']
        for qrcode,s in zip(sqrcode[1:], ptype):
            #print(qrcode, stuid, s)
            cmdstr = 'qrencode {} -lH -m1 -o {}/{}-{}.png'.format(qrcode, dir, stuid, s)
            # print cmdstr
            call(cmdstr.split())
    
def writetotals(sum,csvfile=".numsheets"):
    ''' Takes a sum and csv file and adds
    a "Total:", sum" to the csv. This is necessary
    for the cover sheet generation. Could have done
    this in pandas, but it is easier this way.
    '''
    with open(csvfile, "a") as fp:
        fp.write('Total:, {}\n'.format(sum))
    
def writeContextTables(df, fname):
    ''' 
    Take a dataframe and dumpout two context tables
    as buffers so that we can place them side by side
    instead of one after another. This enables us to
    squeeze the instructions.
    '''
    d = [df.columns]
    d += df.values.tolist()
    tot = df['Num. Sheets'].sum()
    
    buffer = ['\\startbuffer[a]']
    buffer.append('\\bTABLE[setups=booktabs, align=middle]')
    for a,b in d:
        buffer.append('\\bTR')
        buffer.append('\\bTD {} \\eTD'.format(a))
        buffer.append('\\bTD {} \\eTD'.format(b))
    buffer.append('\\bTR \\bTD Total: \\eTD \\bTD {} \\eTD \eTR'.format(tot))
    buffer.append('\\eTR\n\\eTABLE')
    buffer.append('\\stopbuffer')

    buffer.append('\\startbuffer[b]')
    buffer.append('\\bTABLE[setups=booktabs, align=middle]')
    for i,v in enumerate(d):
        a,b = v
        if i > 0:
            b = ''
        buffer.append('\\bTR')
        buffer.append('\\bTD {} \\eTD'.format(a))
        buffer.append('\\bTD {} \\eTD'.format(b))
    buffer.append('\\bTR \\bTD Total: \\eTD \\bTD \\eTD \eTR')
    buffer.append('\\eTR\n\\eTABLE')
    buffer.append('\\stopbuffer')
    # print(buffer)
    # create a folder if it does not exist
    with open(fname,"w") as fp:
        fp.write('\n'.join(buffer))
    

def genBarCodes(grps, opts):
    '''
    Generate QR codes for a dataframe group in 'grps' at a time.
    A png image per student is created using the following
    hierarchy. 
      <schoolid>/img/<student-id>.png
    
    The QRcode contains the following:
    "<schoolid>:<class>:<studentid>"
    
    The QRcode will be used to bin the image in the following
    hiearchy:
      <school-di>/<standard>/tiff
    
    This will all create a ConteXT "<schoolid>.tex" file and "sch.csv" 
    file foreach school which will be used to generate the pdf for the 
    school.

    The generation itself will be multi-threaded(32 threads) to speedup
    the QRcode generation.

    Currently, it takes about 80-90 minutes to generate half a million
    QR codes.
    '''
    print("Generating QR codes.")
    data = []
    for k,v in grps:
        key = str(k)
        fkey = '{}/{}'.format(opts.rundir,key)
        mkdir_p('{}/cover'.format(fkey))
        # need to link to the common context tex file
        # dump out the csv file for the school
        fname = '{}/sch.csv'.format(fkey)
        # sort the data froma by standard/name
        s = v.copy()
        s.sort_values(['STANDARD', 'STU_NAME'], inplace=True)
        s.to_csv(fname)
        # dump out the standard/sheet counts
        colnames = [u'DISTRICT_NAME', u'BRC_NAME',
                    u'CRC_NAME', 
                    u'SCHOOL_NAME', u'STANDARD']
        n = pd.DataFrame({'Num. Sheets': s.groupby(colnames).size()}).reset_index()
        fname = '{}/.numsheets'.format(fkey)
        #print n.head()
        numsheets = n[['STANDARD', 'Num. Sheets']]
        numsheets.to_csv(fname, index=False)
        writetotals(numsheets['Num. Sheets'].sum(), fname)
        # dump out a csv for the district/block/cluster/schname
        # the cover sheet
        h = ['District:','Block:', 'Cluster:', 'School:']
        s = list(n.iloc[0].values)[0:4]
        sinfo = pd.DataFrame(list(zip(h,s)))
        fname = '{}/.schinfo'.format(fkey)
        sinfo.to_csv(fname, index=False)
        if opts.encrypt:
            data.append((opts.rundir, key, v[['CHILD_ENROLL_NO', 'EQR_L', 'EQR_C']].values.tolist()))
        else:
            data.append((opts.rundir, key, v[['CHILD_ENROLL_NO', 'QR_CODE_L','QR_CODE_C']].values.tolist()))
        buffname = '{}/cover/buffers.tex'.format(fkey)
        writeContextTables(numsheets, buffname) 
        
    with Pool(processes=4) as pool:
        pool.map(genBarCodePng, data)

    pdfdata = genDataForPdfSetup(data, opts)
    with Pool(processes=4) as pool:
        pool.map(genPdfSetup,pdfdata)


def genDataForPdfSetup(data,opts):
    dat = []
    for d,k,x in data:
        dat.append((d, k, opts.flowdir))
    return dat

def genSchCode(dirname):
    schidc = '{}0'.format(os.path.basename(dirname))
    schidl = '{}1'.format(os.path.basename(dirname))
    for id,code in zip([schidc, schidl], ['core', 'lang']):
        cmdstr = '/usr/bin/barcode -b {} -e ean13 -E | ps2pdf -dEPSCrop - {}/img/{}.pdf'.format(
            id,dirname,code)
        print (cmdstr.split())
        os.system(cmdstr)

def genPdfSetup(grp):
    '''
    Generate two tex files(language/core) and create a soft link
    to the pdf gen Makefile.
    '''
    #dir = '{}'.format(grp[0], grp[1])
    dir = '{}/{}'.format(grp[0],grp[1])
    fldir = grp[2]
    genSchCode(dir)
    #cdir = os.getcwd()
    #os.chdir(dir)
    for s in ['lang', 'core']:
        tex = '{}/{}-{}.tex'.format(dir,grp[1],s)
        instex = '{}/cover/inst-{}.tex'.format(dir,s)
        src = '{}/pdf/tex/pdfgen-{}.tex'.format(fldir,s)
        instsrc = '{}/pdf/tex/inst-{}.tex'.format(fldir,s)
        os.symlink(src, tex)
        os.symlink(instsrc, instex)
    src = '{}/pdf/Makefile'.format(fldir)
    dst = '{}/makefile'.format(dir)
    os.symlink(src, dst)

def latex(x):
    ''' 
    Replace all the special characters in the string x to
    be "ConteXt" friendy inorder to generate pdf without errors.
    '''
    return (x.replace('\\', '\\textbackslash ').replace('_', '\textunderscore ')
            .replace('%', '\\\textpercent ').replace('$', '\\textdollar ')
            .replace('#', '\\#').replace('{', '\\textbraceleft ')
            .replace('}', '\\textbraceright ').replace('~', '\\textasciitilde ')
            .replace('^', '\\textasciicircum ').replace('&', '\\& ')
            .replace('|', '\\textbar '))

def qrcode(x):
    '''
    QR Code format
    '''
    code = '{}:{}:{}'.format(x['SCHOOL_ID'], x['STANDARD'], x['CHILD_ENROLL_NO'])
    return code

def mungeNames(x):
    '''
    munge the district/block/cluster to remove the special characters.
    '''
    return (re.sub(r'[\s . ( ) \\ /]+', '_', x))

def formatData(csvfile):
    '''
    Cleanup the input csvfile and return
    a data frame.
    '''
    if not os.path.isfile(csvfile):
        print ('File {} does not exist.'.format(csvfile))
        sys.exit(1)
    df = pd.read_csv(csvfile)
    # drop these columns as they are not necessary
    colstodrop = ['STU_DOB', 'SCHOOL_MEDIUM',
                  'STU_RELEGION', 'GENDER',
                  'CATEGORY', 'BPL_STATUS',
                  'DISABILITY']
    #colstodrop=['SCHOOL_MEDIUM']
    df = df[df.columns.difference(colstodrop)]
    # drop all rows if any fields are NA
    # df.dropna(inplace=True)
    # munge text in cols
    df['SCHOOL_NAME'] = df['SCHOOL_NAME'].apply(latex)
    df['STU_NAME'] = df['STU_NAME'].apply(latex)
    cols = ['DISTRICT_NAME', 'BRC_NAME', 'CRC_NAME']
    for col in cols:
        df[col] = df[col].apply(mungeNames)
    df.to_csv("clean.csv")
    # correct data types in columns to int instead of float
    intcols = ['CHILD_ENROLL_NO', 'SCHOOL_ID', 'STANDARD']
    df[intcols] = df[intcols].astype(int)
    # df['QRCODE'] = df.apply(qrcode, axis=1)
    df['Images'] = df['CHILD_ENROLL_NO'].apply(lambda x: 'img/{}-l.png'.format(str(x)))
    # sort the dataFrame
    df.sort_values(['SCHOOL_ID','STANDARD','STU_NAME'], inplace=True)
    return df

def nmain():
    df = pd.read_csv('slist.csv')
    df.dropna(inplace=True)
    df['SCHOOL_NAME'] = df['SCHOOL_NAME'].apply(latex)
    df['STU_NAME'] = df['STU_NAME'].apply(latex)
    cols = ['DISTRICT_NAME', 'BRC_NAME', 'CRC_NAME']
    for col in cols:
        df[col] = df[col].apply(mungeNames)

    colstodrop = ['STU_DOB', 'SCHOOL_MEDIUM',
                  'STU_RELEGION', 'GENDER',
                  'CATEGORY', 'BPL_STATUS',
                  'DISABILITY']
    df = df.columns.difference(colstodrop)
        
    df.to_csv("clean.csv")
    # correct data types in columns to int instead of float
    intcols = ['CHILD_ENROLL_NO', 'SCHOOL_ID', 'STANDARD']
    df[intcols] = df[intcols].astype(int)
    df['Images'] = df['CHILD_ENROLL_NO'].apply(lambda x: 'img/{}-l.png'.format(str(x)))
    df['QRCODE'] = df.apply(qrcode, axis=1)
    data = []
    grps = df.groupby('SCHOOL_ID')
    genBarCodes(grps)

def popCfgFiles(opts):
    files = ['69-lang-sig.pdf', '69-core-sig.pdf', '45-lang-sig.pdf', '45-core-sig.pdf']
    for f in files:
        src = '{}/forms/{}'.format(opts.flowdir, f)
        dst = '{}/{}'.format(opts.rundir, f)
        os.symlink(src,dst)
    srcm = '{}/pdf/Makefile.SUB'.format(opts.flowdir)
    dstm = '{}/Makefile'.format(opts.rundir)
    os.symlink(srcm, dstm)

def main():
    parser = argparse.ArgumentParser("Generate the QR Codes and setup the flow for Pdf generation.")
    parser.add_argument("--rundir", nargs='?', default=os.getcwd(), help="Create the tree in this dir.")
    parser.add_argument("--flowdir",required=True, help="Flow directory path for config files, etc.")
    parser.add_argument("--csv",required=True, help="Csv file to process..")
    parser.add_argument("--encrypt",action='store_true', help="Encode encrypted QR codes.")
    #args = '--flowdir /home/sikshana/sas/flow --rundir sample --csvdir sample_csvs --encrypt'
    #opts = parser.parse_args(args.split())
    opts = parser.parse_args()
    if not os.path.isdir(opts.rundir):
        print ("Directory {} does not exist.".format(opts.rundir))
        print ('Creating run dir {}'.format(opts.rundir))
        os.makedirs(opts.rundir, exist_ok=True)
        
    if not os.path.isdir(opts.flowdir):
        print ("Directory {} does not exist.".format(opts.flowdir))
        sys.exit(1)
        
    if not os.path.isfile(opts.csv):
        print ("csv file {} does not exist.".format(opts.csv))
        sys.exit(1)

    
    rundirtop = opts.rundir
    print('Processing {}.'.format(opts.csv))
    opts.csvfile = opts.csv
    distname = os.path.basename(opts.csv)
    opts.rundir = '{}'.format(rundirtop)
    # create the dist folder
    os.makedirs(opts.rundir, exist_ok=True)
    # start the processing
    df = formatData(opts.csvfile)
    grps = df.groupby('SCHOOL_ID')
    genBarCodes(grps, opts)
    popCfgFiles(opts)
    
if __name__=='__main__':
    main()
    #getCsvFiles("./sample_csvs/")
