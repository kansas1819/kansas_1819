#!/usr/bin/env python
from sys import argv
import zbar
from PIL import Image
from PIL import ImageSequence
import glob
import os, shutil
import re
import argparse
from collections import defaultdict
from collections import namedtuple

Code=namedtuple('Code',['pagenum', 'type', 'value' ,'comment'])

def find_all(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result

def classifyImage(img, pagenum):
    id = []
    Code=namedtuple('Code',['pagenum', 'type', 'value' ,'comment'])
    tiffimg = img.convert("L")
    width, height = tiffimg.size
    raw = tiffimg.tobytes()
    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)
    scanner = zbar.ImageScanner()
    # scan the image for barcodes
    scanner.scan(image)
    for symbol in image:
        if str(symbol.type) == 'CODE128':
            data = symbol.data[:-4]
            id.append(Code(pagenum, 'code128', data, 'omr sheet')) 
        elif str(symbol.type) == 'QRCODE':
            id.append(Code(pagenum, 'qrcode', symbol.data, 'school code')) 
        else:
            id.append(Code(pagenum, 'error', '', 'not an omr sheet'))
    del(image)
    return id

def classifyTiff(tiffile):
    print "TIFF:" , tiffile, os.getcwd()
    ids = defaultdict(list)
    pagenum = 0
    # images = Image.open(tiffile).convert('L')
    images = Image.open(tiffile)
    for tiffimg in ImageSequence.Iterator(images):
        code = classifyImage(tiffimg, pagenum)
        if len(code) ==  0:
            code = [Code(pagenum, 'error', '', 'cannot read survey id')]
        for c in code:
            ids[c.type].append(c)
        pagenum+=1
    return ids

def mapClassifiedTiff(ids, opts):
    ''' Takes a classified dict of the survey ids of the tiff file 
    and maps the ids to errors or the right standards associated 
    with the bar code from the config file.
    '''
    omrtiff = defaultdict(list)
    #print ids
    for code in ids['code128']:
        try:
            std = opts.cfg.get(code.value, 'Std')
            omrtiff[std].append(str(code.pagenum))
        except ConfigParser.NoSectionError:
            omrtiff['error'].append(code)
            print "Not the right OMR sheet."
            print code
    for e in ('qrcode', 'error'):
        if ids.has_key(e):
            for item in ids[e]:
                omrtiff['error'].append(item)
    return omrtiff

def get_idsinfo(path):
    ids = {}
    survey = re.compile('survey_id\s+=\s+(\d+)')
    std = os.path.basename(os.path.dirname(os.path.dirname(path)))
    with open(path, "r") as fp:
        lines = fp.readlines()
        for l in lines:
            m = survey.match(l)
            if m:
                id = m.groups()[0]
                print id
                ids[id] = std
                print m.groups()[0], std
                break
    print std, ids
    return (std, id)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def popDirs(tiffiles, args):
    for dir, files in tiffiles.iteritems():
        tiffdir = "{}/{}/tiff/".format(args.dir, dir)
        dst = args.dir + "/"
        src = args.db + "/" + dir
        print dir
        print files
        mkdir_p(tiffdir)
        print src, dst
        #shutil.copytree(src, dst)
        for file in files:
            shutil.move(file, tiffdir)
            #shutil.copytree(src, dst)
def main():
    parser = argparse.ArgumentParser("Sort the tif files in the directory and move them to the appropriate sub directories.")
    parser.add_argument("dir", nargs='?', default=os.getcwd(), help="Process the files in the directory.")
    parser.add_argument("--db",required=True, help="Get the assessment ids from DB directory.")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print "Directory {} does not exist.".format(args.dir)
        exit
    tifFiles = {}

    if not os.path.isdir(args.db):
        print "Directory {} does not exist.".format(args.dir)
        exit
    print args.db
    y = find_all("info", args.db)
    Ids = {}
    for a in y:
        std,id = get_idsinfo(a)
        Ids[id] = std
    print Ids
    # create a reader
    scanner = zbar.ImageScanner()
    # configure the reader
    scanner.parse_config('enable')
    imgfiles = glob.glob(args.dir + "/*.tif")
    print "imagefiles:", imgfiles
    survey_id = None
    for img in imgfiles:
        survey_ids = classify_image(img,Ids)
        idexists=None
        for id in survey_ids:
            survey_id = None
            if Ids.has_key(id):
                survey_id = id
                break
        if survey_id == None:
            print "Barcode cannot be read or is incompatible in the Tif file {}.".format(img)
            continue
        std = Ids[survey_id]
        if tifFiles.has_key(std):
            tifFiles[std] += [img]
        else:
            tifFiles[std] = [img]
    print tifFiles
    popDirs(tifFiles, args)

print "asdfasD"
ids = classifyTiff("output.tif")

if __name__ == '__main__':
    print "asdfasD"
    classifyTiff("/tmp/std4.tif")
