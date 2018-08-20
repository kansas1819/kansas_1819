#!/usr/bin/env python
import timeit
import sys, os
import argparse
import errno, glob
import configparser
import subprocess
import pandas as pd
from collections import namedtuple, defaultdict
#from itertools import izip

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

#from multiprocessing import Pool
#from multiprocessing.dummy import Pool as ThreadPool

def readQrCode(img):
    '''
    Read the barcodes from the img.
    '''
    data = None
    cmdstr = 'zbarimg -Sdisable -Sqr.enable --raw -q {}'.format(img)
    try:
        data = subprocess.check_output(cmdstr.split())
    except subprocess.CalledProcessError as e:
        raise
    if data:
        data = data.rstrip()
    return (img, data)


def readQrCodes(opts):
    '''
    Read QR codes of all the images in opts.dir and
    return a list.
    '''
    #pool = Pool(maxtasksperchild=1)
    images = glob.iglob('{}/{}'.format(opts.dir, opts.pattern))
    imgqr = []
    for x,y in pairwise(sorted(list(images))):
        imgqr.append(x)
    data = map(readQrCode, imgqr)
    #pool.close()
    #pool.join()
    return data

def qrDatatoDf(data, opts):
    ''' 
    Convert the data to a pandas data frame ignoring the 
    'Nones' with the columns:
    ['QRCODE', 'SCHOOL_ID', 'STANDARD', 'CHILD_ENROLL_NO']

    '''
    d = []
    
    for x in data:
        #print(x)
        img,val = x
        if not val: continue
        pagenum = int(img.split("-")[1])
        #(qr,sid, std, cid, t) = val.decode('utf-8').split(':')
        d.append([int(pagenum), val.decode('utf-8')])
    cols = ['PAGE', opts.col]
    df = pd.DataFrame(d, columns=cols)
    df.sort_values(['PAGE'], ascending=True).to_csv("qrdata_{}.csv".format(opts.ptype))

def verifyQR(args):
    cols = [args.col]
    #print qdf.dtypes
    df = pd.read_csv(args.csv)
    #print df.dtypes
    #print df.head()
    # there is a bug in pandas, so we have to write out a file and
    # read it back for the comparison. Else it fails while comparing
    # the columns.
    qdf = pd.read_csv("qrdata_{}.csv".format(args.ptype))
    #print(qdf[cols], df[cols])
    if not qdf[cols].equals(df[cols]):
        msg = (
            'There is a mismatch in data read from tiff. Please compare '
            'the column  in <qrdata.csv> '
            'with the school data {} used to generate the pdf.').format(args.csv)
        print(msg)
        sys.exit(1)
    return True

def main():
    parser = argparse.ArgumentParser('''
    Check the QR codes in the images against a csv file used to generate the pdf.
    ''')
    parser.add_argument("--dir",
                        required=True,
                        default=os.getcwd(),
                        help="Process the files in the directory.")
    parser.add_argument("--csv",
                        required=True,
                        help="Check against this csv.")
    parser.add_argument("--pattern",
                        default="*.tif",
                        help="Pattern to identify the images.")
    parser.add_argument("--encrypt",
                        action='store_true',
                        help="Pattern to identify the images.")
    # args = parser.parse_args('--dir pdfimg --csv sch.csv'.split())
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print ("Directory {} does not exist.".format(args.dir))
        sys.exit(1)
    if not os.path.exists(args.csv):
        print ("csvfile {} does not exist.".format(args.csv))
        sys.exit(1)
    if args.pattern.startswith('core'):
        args.ptype = 'core'
        if args.encrypt:
            col = 'EQR_C'
        else:
            col = 'QR_CODE_C'
    else:
        args.ptype = 'lang'
        if args.encrypt:
            col = 'EQR_L'
        else:
            col = 'QR_CODE_L'
    args.col = col
    print(args.ptype)
        
    qrdf = (qrDatatoDf(readQrCodes(args), args))
    verifyQR(args)
    print ('Verified QR.')

#main()

if __name__ == '__main__':
    main()

