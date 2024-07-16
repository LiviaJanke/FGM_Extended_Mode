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

entry_exit_dump_times = pd.DataFrame({'Entry Time':ext_entered, 'Exit Time': ext_left, 'Dump Time': dump_times, 'Duration': ext_durations})

ext = '.csv'

filename = filepath + '_Entry_Exit_Dump' + ext

entry_exit_dump_times.to_csv(filename)


#%%


SATT_strings = pd.read_csv('C:/FGM_Extended_Mode/SATT_Strings/C1_SATT_Strings', usecols = range(7), sep = '\s+', names = ['num','letter', 'start', 'stop', 'eh', 'huh', 'spins_per_min'])

SATT_starts = pd.to_datetime(SATT_strings['start'].str[:-1])

SATT_stops = pd.to_datetime(SATT_strings['stop'].str[:-1])

SATT_spins_per_min = SATT_strings['spins_per_min']

starts_stops_spins_df = pd.DataFrame({'Starts':SATT_starts, 'Stops': SATT_stops, 'Spins': SATT_spins_per_min})


#%%

tspins = []

for i in np.arange(0, len(entry_exit_dump_times['Entry Time'])):
    
    ext_entry = entry_exit_dump_times['Entry Time'][i]
    
    #print(ext_entry)
    
    ext_exit = entry_exit_dump_times['Exit Time'][i]
    
    closest_start = np.min(abs(starts_stops_spins_df['Starts'] - ext_entry))
    
    diffs_to_start = abs(starts_stops_spins_df['Starts'] - ext_entry)
    
    closest_stop = np.min(abs(starts_stops_spins_df['Stops'] - ext_exit))
    
    diffs_to_stop = abs(starts_stops_spins_df['Stops'] - ext_exit)
    
    if closest_start < closest_stop:
        
        SATT_index = list(diffs_to_start).index(closest_start)
        
    else:
        
        SATT_index = list(diffs_to_stop).index(closest_stop)

    tspin = 60 / starts_stops_spins_df['Spins'].iloc[SATT_index]
    
    tspins.append(tspin)
        
#%%

entry_exit_dump_duration_tspin = pd.DataFrame({'Entry Time':ext_entered, 'Exit Time': ext_left, 'Dump Time': dump_times,  'Duration': ext_durations, 'tspin': tspins})

ext = '.csv'

filename = filepath + '_Entry_Exit_Dump_Duration_Tspin' + ext

entry_exit_dump_duration_tspin.to_csv(filename)


#%%

calparams_filepath = 'C:/FGM_Extended_Mode/Calibration_files/2001_C1/'

entry_1 = entry_exit_dump_duration_tspin['Entry Time'][0]

formatted_entry = entry_1.strftime('%Y%m%d')
print(formatted_entry)

exit_1 = entry_exit_dump_duration_tspin['Exit Time'][0]

formatted_exit = exit_1.strftime('%Y%m%d')
print(formatted_exit)

#%%

import os, fnmatch


def find(pattern_entry, pattern_exit, path):
    result = []
    for root, dirs, files in os.walk(path):
        
        for name in files:
                
            if fnmatch.fnmatch(name, pattern_exit):
                result.append(os.path.join(root, name))
                
            elif fnmatch.fnmatch(name, pattern_entry):
                result.append(os.path.join(root, name))
                
            elif fnmatch.fnmatch(name, pattern_exit[-2]):
                result.append(os.path.join(root, name))

    return result


cal_filename = find('*' + str(formatted_entry) + '*', '*' + str(formatted_exit) + '*', calparams_filepath)[-1]

print(cal_filename)

#%%

cal_params = pd.read_csv(cal_filename, skiprows = 58, header = None, sep = ',|:', usecols = range(4), on_bad_lines = 'skip', engine = 'python') 

#%%

x_offsets = cal_params[cal_params[0] == 'Offsets (nT)'][1].values.tolist()
x_gains = cal_params[cal_params[0] == 'Gains       '][1].values.tolist()
y_gains = cal_params[cal_params[0] == 'Gains       '][2].values.tolist()
z_gains = cal_params[cal_params[0] == 'Gains       '][3].values.tolist()


#%%

while len(x_offsets) < 6:
    x_offsets.append(0)
    
while len(x_gains) < 6:
    x_gains.append(1)

while len(y_gains) < 6:
    y_gains.append(1)

while len(z_gains) < 6:
    z_gains.append(1)

#%%

yz_gains = []

for i in np.arange(0,6):

    yz_gain = (float(y_gains[i]) + float(z_gains[i])) / 2.0
    
    yz_gains.append(yz_gain)

#%%

calparams = {'x_offsets':  x_offsets,\
             'x_gains':    x_gains,\
             'yz_gains':   yz_gains}


#%%











