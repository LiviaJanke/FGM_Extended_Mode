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

craft = 'C4'

filepath = filebase +'/' + craft 

Ext_entries = pd.read_csv(filepath + '_Ext_Entries',usecols = range(8), delimiter = ' ', names = ['Execution_Time', 'Uplink_Time', 'Command_Mnemonic', 'Command_Sequence_Name', 'Cat', 'Src', 'GS', 'Ver'])

Ext_entries_unique = Ext_entries.drop_duplicates(subset = 'Execution_Time', keep = 'first').reset_index(drop = True)

Ext_exits = pd.read_csv(filepath + '_Ext_Exits',usecols = range(8), delimiter = ' ', names = ['Execution_Time', 'Uplink_Time', 'Command_Mnemonic', 'Command_Sequence_Name', 'Cat', 'Src', 'GS', 'Ver'])

Ext_exits_unique = Ext_exits.drop_duplicates(subset = 'Execution_Time', keep = 'first').reset_index(drop = True)

MSA_dumps = pd.read_csv(filepath + '_MSA_Dumps',usecols = range(8), delimiter = ' ', names = ['Execution_Time', 'Uplink_Time', 'Command_Mnemonic', 'Command_Sequence_Name', 'Cat', 'Src', 'GS', 'Ver'])

MSA_dumps_unique = MSA_dumps.drop_duplicates(subset = 'Execution_Time', keep = 'first').reset_index(drop = True)


#%%


MSA_dump_times = pd.to_datetime(MSA_dumps_unique['Execution_Time'].str[:-1])


#%%

for i in np.arange(0, len(MSA_dump_times)):
    
    if i < len(MSA_dump_times) - 1:
        
        MSA_dumps_del_t = MSA_dump_times[i+1] - MSA_dump_times[i]
        
        if MSA_dumps_del_t < timedelta(seconds = 600):
            
            MSA_dump_times.drop(labels = i, inplace = True)


#%%

MSA_dump_times.reset_index(drop = True, inplace = True)


#%%

Ext_entry_times = pd.to_datetime(Ext_entries_unique['Execution_Time'].str[:-1])


#%%

for i in np.arange(0, len(Ext_entry_times)):
    
    if i < len(Ext_entry_times) - 1:
        
        Ext_entry_times_del_t = Ext_entry_times[i+1] - Ext_entry_times[i]
        
        if Ext_entry_times_del_t < timedelta(seconds = 600):
            
            Ext_entry_times.drop(labels = i, inplace = True)

#%%


Ext_entry_times.reset_index(drop = True, inplace = True)

#%%

Ext_exit_times = pd.to_datetime(Ext_exits_unique['Execution_Time'].str[:-1])

#%%

for i in np.arange(0, len(Ext_exit_times)):
    
    if i < len(Ext_exit_times) - 1:
        
        Ext_exit_times_del_t = Ext_exit_times[i+1] - Ext_exit_times[i]
        
        if Ext_exit_times_del_t < timedelta(seconds = 600):
            
            Ext_exit_times.drop(labels = i, inplace = True)

#%%

Ext_exit_times.reset_index(drop = True, inplace = True)

#%%

Ext_entry_times.to_csv('C:/FGM_Extended_Mode/Lib/' + craft + '_Ext_Entries', header = False, index = False)

        
Ext_exit_times.to_csv('C:/FGM_Extended_Mode/Lib/' + craft + '_Ext_Exits', header = False, index = False)

MSA_dump_times.to_csv('C:/FGM_Extended_Mode/Lib/' + craft + '_MSA_Dump_times', header = False, index = False)




SATT_strings = pd.read_csv('C:/FGM_Extended_Mode/SATT_Strings/' + craft + '_SATT_Strings', usecols = range(7), sep = '\s+', names = ['num','letter', 'start', 'stop', 'eh', 'huh', 'spins_per_min'])

SATT_starts = pd.to_datetime(SATT_strings['start'].str[:-1])

SATT_stops = pd.to_datetime(SATT_strings['stop'].str[:-1])

SATT_spins_per_min = SATT_strings['spins_per_min']

starts_stops_spins_df = pd.DataFrame({'Starts':SATT_starts, 'Stops': SATT_stops, 'Spins': SATT_spins_per_min})

starts_stops_spins_df.to_csv('C:/FGM_Extended_Mode/Lib/' + craft + '_SATT_start_stop_spins', header = False, index = False)














