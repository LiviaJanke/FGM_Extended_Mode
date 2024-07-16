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


#%%

for i in np.arange(0, len(MSA_dump_times)):
    
    if i < len(MSA_dump_times) - 1:
        
        MSA_dumps_del_t = MSA_dump_times[i+1] - MSA_dump_times[i]
        
        if MSA_dumps_del_t < timedelta(seconds = 600):
            
            MSA_dump_times.drop(labels = i, inplace = True)


#%%

MSA_dump_times.reset_index(drop = True, inplace = True)


#%%

Ext_entry_times = pd.to_datetime(C1_Ext_entries_unique['Execution_Time'].str[:-1])


#%%

for i in np.arange(0, len(Ext_entry_times)):
    
    if i < len(Ext_entry_times) - 1:
        
        Ext_entry_times_del_t = Ext_entry_times[i+1] - Ext_entry_times[i]
        
        if Ext_entry_times_del_t < timedelta(seconds = 600):
            
            Ext_entry_times.drop(labels = i, inplace = True)

#%%


Ext_entry_times.reset_index(drop = True, inplace = True)

#%%

Ext_exit_times = pd.to_datetime(C1_Ext_exits_unique['Execution_Time'].str[:-1])

#%%

for i in np.arange(0, len(Ext_exit_times)):
    
    if i < len(Ext_exit_times) - 1:
        
        Ext_exit_times_del_t = Ext_exit_times[i+1] - Ext_exit_times[i]
        
        if Ext_exit_times_del_t < timedelta(seconds = 600):
            
            Ext_exit_times.drop(labels = i, inplace = True)

#%%

Ext_exit_times.reset_index(drop = True, inplace = True)

#%%


unmatched_entries = []

unmatched_exits = []

ext_entered = []

ext_left = []

ext_durations = []

unmatched_exit_counter = 0

unmatched_entry_counter = 0 

for i in np.arange(0, len(Ext_entry_times) - 55):
    
    print(i)
    print(unmatched_entry_counter)
    print(unmatched_exit_counter)
    
    time_diff_exit_to_next_entry = Ext_entry_times[i + 1 + unmatched_entry_counter] - Ext_exit_times[i + unmatched_exit_counter]
    
    if time_diff_exit_to_next_entry > timedelta(seconds = 0):
        
        exit_addon = 0
        
        if Ext_exit_times[i + unmatched_exit_counter] - Ext_entry_times[i + unmatched_entry_counter] > timedelta(seconds = 0) and Ext_exit_times[i + unmatched_exit_counter] - Ext_entry_times[i + unmatched_entry_counter] < timedelta(hours = 28):
        
            ext_duration = Ext_exit_times[i + unmatched_exit_counter] - Ext_entry_times[i + unmatched_entry_counter]
            
            ext_durations.append(ext_duration)
        
            ext_entered.append(Ext_entry_times[i + unmatched_entry_counter])
        
            ext_left.append(Ext_exit_times[i + unmatched_exit_counter])
            
        elif Ext_exit_times[i + unmatched_exit_counter + 1] - Ext_entry_times[i + unmatched_entry_counter] > timedelta(seconds = 0) and Ext_exit_times[i + unmatched_exit_counter + 1] - Ext_entry_times[i + unmatched_entry_counter] < timedelta(hours = 28):
            
            ext_duration = Ext_exit_times[i + unmatched_exit_counter + 1] - Ext_entry_times[i + unmatched_entry_counter]
            
            ext_durations.append(ext_duration)
        
            ext_entered.append(Ext_entry_times[i + unmatched_entry_counter])
        
            ext_left.append(Ext_exit_times[i + unmatched_exit_counter + 1])
            
            unmatched_exit_counter += 2
            
        else:
            
            print((Ext_entry_times[i + unmatched_entry_counter]))
            
            print(Ext_exit_times[i + unmatched_exit_counter])
            
            print(ext_duration)
            
            unmatched_exit_counter += 1
                
            unmatched_exits.append(i)
            
    else:
        
        unmatched_entry_counter += 1
            
        unmatched_entries.append(i)
                
        
        
#%%


dates = MSA_dump_times.values
df=pd.DataFrame(dates)
df=df.set_index(dates) 
df=df.sort_index(ascending=False)


#%%

dump_times = []

for i in np.arange(0, len(ext_left)):
    
    print(ext_left[i])

    result = df.truncate(before=ext_left[i])
    
#    print(result)
    
    val = result.iloc[-1]  #take the bottom value, or the 1st after the base date
   
    print(val[0])
        
    dump_times.append(val[0])


#%%

entry_exit_dump_times = pd.DataFrame({'Entry Time':ext_entered, 'Exit Time': ext_left, 'Dump Time': dump_times})

#%%


ext = '.csv'

filename = filepath + '_Entry_Exit_Dump' + ext

entry_exit_dump_times.to_csv(filename)


#%%


SATT_strings = pd.read_csv('C:/FGM_Extended_Mode/SATT_Strings/C1_SATT_Strings')


#%%




#%%

calparams_filepath = 'C:/FGM_Extended_Mode/Calibration_files/2001_C1/'

#%%











