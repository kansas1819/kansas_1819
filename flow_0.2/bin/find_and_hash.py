#!/usr/bin/env python
import os
import hashlib
import re
import argparse
import pandas as pd
from shutil import copyfile
from multiprocessing import Pool

#\w+.tif
#no need to write r' in argument and no '' characters. 

#pd.set_option('display.width', 1000)

def read_tifs(pattern, dir_path):
    
    files = []
    for root, d, f in os.walk(dir_path):
        for item in f:
            if re.match(pattern, item):
                #print(item)
                files.append(os.path.join(root, item))
    #print(files)
    return files
        
def create_hash(file_path):
    
    blocksize = 2**20
    with open(file_path, encoding = "latin-1") as afile:
        hasher = hashlib.md5()
        while True:
            buf = afile.read(blocksize)
            if not buf:
                break
            hasher.update(buf.encode())
        fp = hasher.hexdigest()
    return (file_path, fp)

def create_hashes(all_files):

    return [create_hash(x) for x in all_files]
    
def to_df(files_fp, output_dir):
    
    df = pd.DataFrame.from_records(files_fp)
    
    df.rename({0 : 'File_Path',
               1 : 'Finger_Print'}, axis = 1, inplace = True)
    
    df.to_csv(output_dir + 'output.csv', index = False)
    
    return df  

def add_cols(df, dfo):
    
    df['SCHOOL_ID'] = df['File_name'].apply(lambda x : x.split('-')[0])
    
    df['SCHOOL_ID'] = df['SCHOOL_ID'].astype('int64')
    
    df = df.merge(dfo, on = 'SCHOOL_ID')
    
    return df

def create_paths(length_, df):
    
    if length_ == 1:
        
        return df[['output_dir','DISTRICT_NAME', 'File_name']].apply(lambda x : '/'.join(x), axis = 1)
    
    if length_ == 2:
        
        return df[['output_dir','DISTRICT_NAME', 'BRC_NAME', 
                   'File_name']].apply(lambda x : '/'.join(x), axis = 1)
    
    if length_ == 3:
        
        return df[['output_dir','DISTRICT_NAME', 'BRC_NAME', 
                   'CRC_NAME','File_name']].apply(lambda x : '/'.join(x), axis = 1)
    

def copy_files(t):
    ofp, tfp = t
    tdir = os.path.dirname(tfp)
    os.makedirs(tdir, exist_ok = True)
    copyfile(ofp, tfp)

def verify_copy(outputdir):
    l = []
    h = []
    for r, d, files in os.walk(outputdir):
        for f in files:
            if f.endswith('.pdf'):
                l.append(f)
                h.append(create_hash(os.path.join(r + '/' +f))[1])
                
    return l, h


def main():
    parser = argparse.ArgumentParser(description = "find and hash.")
    parser.add_argument('--dir', required = True)
    parser.add_argument('--pattern', required = True)
    parser.add_argument('--outputdir', required = True, help = "it should end with a forward slash [/]")
    parser.add_argument('--datascheme', required = True, type = int)
    
    opts = parser.parse_args()
    
    files =  read_tifs(opts.pattern, opts.dir)
    
    files_fp = create_hashes(files)
    
    df = to_df(files_fp, opts.outputdir)
    
    df['File_name'] = [re.search("\w+-\w+.pdf", x)[0] for x in df['File_Path']]
    
    df['output_dir'] = opts.outputdir
    
    df.to_csv(opts.outputdir + 'output.csv', index = False)
    
    dfo = pd.read_csv('/home/sikshana/sas/sch_dist_blk_crc.csv')
    
    df = add_cols(df, dfo)
    
    df.to_csv(opts.outputdir + 'output.csv', index = False)
    
    df['Target_Path'] = create_paths(opts.datascheme, df)

    df['Target_Path'] = df['Target_Path'].str.replace('//', '/')
    
    df.to_csv(opts.outputdir + 'output.csv', index = False)
    
    x = df[['File_Path', 'Target_Path']].values.tolist()
    
    with Pool(processes = 4) as pool:
    
        pool.map(copy_files, x)
        
    l, h = verify_copy(opts.outputdir)

    dfc = pd.DataFrame({'cfp' : l, 'hfp' : h})

    dfm = dfc.merge(df[['File_name', 'Finger_Print']],
             left_on = ['cfp', 'hfp'], right_on = ['File_name', 'Finger_Print'],
                   indicator = True)

    if dfm.loc[dfm['_merge'].isin(['right_only', 'left_only'])].shape[0] > 0:
            print('there are duplicate school ids.')

    dfm.to_csv(opts.outputdir + 'check2.csv', index = False)

    dfm.drop(dfm.loc[dfm['_merge'].isin(['left_only', 'right_only'])].index, inplace = True)

    print(dfm['hfp'].equals(dfm['Finger_Print']))
    
    
main()   



