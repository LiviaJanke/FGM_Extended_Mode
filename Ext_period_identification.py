# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 19:10:13 2024

@author: Livia
"""


# Importing things

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import datetime

from datetime import date

import sys 

sys.path.append('C:/FGM_Extended_Mode/Lib') 

from fgmfiletools import fgmsave, fgmopen_cef, fgmopen_dp, fgmopen

from pandas import read_csv
from matplotlib.pyplot import savefig,suptitle,xlabel,ylabel,plot,grid,legend,subplot,subplots
from datetime import datetime,timedelta
from numpy import sqrt,array,delete,zeros,size,pi,copy,sin,cos

from datetime import datetime,timedelta
from scipy.stats import linregress
import sys

#%%


filebase = 'C:/FGM_Extended_Mode/SCCH_strings'

craft = 'C1'


filepath = filebase +'/' + craft 

C1_Ext_entries = pd.read_csv(filepath + '_Ext_Entries',usecols = range(8), delimiter = ' ', names = ['Execution_Time', 'Uplink_Time', 'Command_Mnemonic', 'Command_Sequence_Name', 'Cat', 'Src', 'GS', 'Ver'])

C1_Ext_entries_unique = C1_Ext_entries.drop_duplicates(subset = 'Execution_Time', keep = 'first').reset_index(drop = True)

C1_Ext_exits = pd.read_csv(filepath + '_Ext_Exits',usecols = range(8), delimiter = ' ', names = ['Execution_Time', 'Uplink_Time', 'Command_Mnemonic', 'Command_Sequence_Name', 'Cat', 'Src', 'GS', 'Ver'])

C1_Ext_exits_unique = C1_Ext_exits.drop_duplicates(subset = 'Execution_Time', keep = 'first').reset_index(drop = True)

C1_MSA_dumps = pd.read_csv(filepath + '_MSA_Dumps',usecols = range(8), delimiter = ' ', names = ['Execution_Time', 'Uplink_Time', 'Command_Mnemonic', 'Command_Sequence_Name', 'Cat', 'Src', 'GS', 'Ver'])

C1_MSA_dumps_unique = C1_MSA_dumps.drop_duplicates(subset = 'Execution_Time', keep = 'first').reset_index(drop = True)

#%%


MSA_dump_times = pd.to_datetime(C1_MSA_dumps_unique['Execution_Time'].str[:-1])

Ext_entry_times = pd.to_datetime(C1_Ext_entries_unique['Execution_Time'].str[:-1])

Ext_exit_times = pd.to_datetime(C1_Ext_exits_unique['Execution_Time'].str[:-1])


#%%


entry_exit_dump_times = pd.DataFrame({'Entry Time':Ext_entry_times, 'Exit Time': Ext_exit_times, 'Dump Time' :MSA_dump_times })

#%%





#%%

# Want to pair up entry, exit and MSA dump times

# this requires manual alteration of np.arange end value

entries = []

exits = []

dumps = []

unmatched_entries = []

unmatched_exits = []

unmatched_exit_counter = 0

unmatched_entry_counter = 0

# subtraction value needs to be one more than unmatched entry counter

for i in np.arange(0, len(Ext_entry_times) - 124):
    
    entry = Ext_entry_times[i + unmatched_entry_counter]
    
#    print(entry)
    
    next_entry = Ext_entry_times[i + 1 + unmatched_entry_counter]
    print(i)
    print(i + 1 + unmatched_entry_counter)
    
#    print(next_entry)
    
    exit_time =  Ext_exit_times[i + unmatched_exit_counter]
    
#    print(exit_time)
    
    next_exit_time = Ext_exit_times[i + 1 + unmatched_exit_counter]
    
#    print(next_exit_time)
        
    if exit_time > next_entry:
        
        unmatched_entry_counter +=1    
        
#        print(unmatched_entry_counter)
        
    elif next_exit_time < next_entry:
        
        unmatched_exit_counter +=1    
        
#        print(unmatched_exit_counter)    
            
    elif entry < exit_time < next_entry:
        
        entries.append(entry)
        
        exits.append(exit_time)
        
        
    else:
        
        print('yikes')
        
    

#%%


    















