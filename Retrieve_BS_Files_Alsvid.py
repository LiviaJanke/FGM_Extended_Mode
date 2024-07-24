# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 13:10:41 2024

@author: Livia
"""

import sys
import pandas as pd

craft = str(sys.argv[1])

import os, fnmatch

MSA_dumps_filepath = '/home/lme19/MSA_Dump_Times/' + craft + '_MSA_Dump_times'

MSA_dumps_df = pd.read_csv(MSA_dumps_filepath, header = None)

MSA_dumps = pd.to_datetime(MSA_dumps_df[0])

def find_BS_file(date, path):

    pattern_B = craft + '_' + date + '_B.BS'
    
    pattern_K = craft + '_' + date + '_K.BS'
    
    pattern_A = craft + '_' + date + '_A.BS'

    for root, dirs, files in os.walk(path):
        
        for name in files:
                
            if fnmatch.fnmatch(name, pattern_B):
                return(os.path.join(root, name))
                      
            elif fnmatch.fnmatch(name, pattern_K):
                return(os.path.join(root, name))
                
            elif fnmatch.fnmatch(name, pattern_A):
                return(os.path.join(root, name))


BS_locations = craft + '_BS_file_locations'

for i in MSA_dumps:
    
    dumpdate = i.strftime('%Y%m%d')
    
    year = i.strftime('%Y')
    
    month =  i.strftime('%m')
    
    day =  i.strftime('%d')
    
    BS_filepath =  '/cluster/data/raw/' + year + '/' + month + '/'
    
    BS_file_location = find_BS_file(day, BS_filepath)
    
    f = open(BS_locations, "w")
    f.write(BS_file_location)
    f.close() 
    

            




