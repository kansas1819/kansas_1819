#! /usr/bin/env python

import pandas as pd
import argparse


def summarizeRun(ifile, rcsv, ofile):
	'''
	cleaning the processed file we read above. brining only selected columns &
	changing the column name to match the file we need to merge it with
	'''
	
	#reading the file to compare our running data
	dfx = pd.read_csv(rcsv)
        
	#reading the running data file (processed)
	dfp = pd.read_csv(ifile)
        
	dfp = dfp[['schid', 'stuid', 'lang']]
	dfp = dfp.rename(columns = {'schid' : 'SCHOOL_ID'})

	#merging the file
	dfm = dfp.merge(dfx, on = 'SCHOOL_ID')
        
	#grouping the dfm file as per the requirements
	dfc = dfm.groupby(['DISTRICT_NAME', 
                   'BRC_NAME', 'CRC_NAME', 'SCHOOL_ID', 
                   'SCHOOL_NAME', 'lang']).SCHOOL_ID.count().reset_index(name = 'counts')
	#pivoting the dataframe above
	dfc= dfc.pivot_table('counts', ['DISTRICT_NAME', 'BRC_NAME', 
                           'CRC_NAME', 'SCHOOL_ID','SCHOOL_NAME'], 'lang').reset_index()
        
	#exporting the file as csv
        dfc.sort_values(by=['DISTRICT_NAME', 'BRC_NAME', 'CRC_NAME'], inplace=True)
	dfc.to_csv(ofile, encoding = 'utf-8', index = False)
	
	
def main():
	parser = argparse.ArgumentParser(description='This generates a summarized csv file.')
	parser.add_argument('--inputcsv', required = True)
	parser.add_argument('--refcsv', required = True)
	parser.add_argument('--outputcsv', required = True)
	
	opts = parser.parse_args()
	print(opts.inputcsv)
	summarizeRun(opts.inputcsv, opts.refcsv, opts.outputcsv)


main()
	
