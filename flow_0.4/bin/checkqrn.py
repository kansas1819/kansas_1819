#!/usr/bin/env python
import timeit
import sys, os
import argparse
import errno, glob
import configparser
import subprocess
import pandas as pd
from collections import namedtuple, defaultdict

def readQrCode(i, img):
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
        data = data.rstrip().decode('utf-8')
    return (img, data)


def _readQrCodes(opts):
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

def readQrCodes(opts):
    '''
    Read QR codes of all the images in opts.dir and
    return a dataFrame.
    '''
    #pool = Pool(maxtasksperchild=1)
    images = sorted(glob.iglob('{}/{}'.format(opts.dir, opts.pattern)))
    data = (readQrCode(i, img) for i, img in enumerate(images) if i%2==0)
    df = pd.DataFrame(data, columns=['TIF', opts.col])
    return df

def verifyQR(args, qdf):
    cols = [args.col]
    df = pd.read_csv(args.csv)
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
    qrdf = readQrCodes(args)
    verifyQR(args, qrdf)
    print ('Verified QR for {}.'.format(args.ptype))

if __name__ == '__main__':
    main()

