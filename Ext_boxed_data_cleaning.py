# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 22:24:36 2024

@author: Livia
"""

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

#%%

unique_reset_vecs_cutoff = 100

res_std_cutoff = 1


#%%

filebase = 'C:\FGM_Extended_Mode\ICME_Event_Data\Ext_010421'

filename = '\C3_010421_ext'

extension = 'txt'

data_file = filebase + filename #+ '.' + extension

#%%

df_raw = pd.read_csv(data_file,  names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'],  on_bad_lines='warn')


#%%

df_raw_no_headers = df_raw.dropna(axis = 0, how = 'any')

df = df_raw_no_headers.reset_index(drop = True)

number_of_packets = len(df['count']) / 445

packet_list = np.arange(1, number_of_packets + 1)

#%%


even_packet_nums = []

bef_indices = []

incomplete_indices = []

bef_reset_vecs = []

bef_res = []

bef_z = []

for i in packet_list:
    
    packet_num = i

    packet_lower_index = (packet_num - 1) * 445

    packet_higher_index = (packet_num * 445) - 1

    packet_index_list = np.arange(packet_lower_index, packet_higher_index + 1)
    
    packet = df.loc[packet_lower_index:packet_higher_index] 
    
    packet.reset_index(inplace = True, drop = True)
    
    packet_count = packet['count']
    
    if packet_count.loc[0] == 'bef ':
        
        even_packet_nums.append(packet_num)
        
        bef_indices.append(packet_lower_index)
        
        prev_reset_vector = packet.loc[0]["reset_vector"]
        
        bef_reset_vecs.append(prev_reset_vector)
        
        prev_resolution = packet.loc[0]["resolution"]
        
        bef_res.append(prev_resolution)
        
        prev_z = packet.loc[0]["resolution"]
        
        bef_z.append(prev_z)
        
 
    else:
        
        
        incomplete_indices.append(packet_higher_index)
        
#%%

df_no_bef = df.drop(labels = bef_indices, axis = 0)


#%%

for i in np.arange(0, len(incomplete_indices)):
    
    if i < len(bef_reset_vecs):

        df_no_bef.loc[incomplete_indices[i], 'reset_vector'] = bef_reset_vecs[i]
    
        df_no_bef.loc[incomplete_indices[i], 'resolution'] = bef_res[i]
    
        df_no_bef.loc[incomplete_indices[i], 'z'] = bef_z[i]
    
    else:
        
        df_no_bef.drop(df_no_bef.tail(1).index,inplace=True)
        


#%%

    
df_continuous = df_no_bef.reset_index(drop = True)    

df_continuous['count'] = df_continuous['count'].astype(float)

packet_starts = df_continuous.loc[df_continuous['count'] == 0].index.tolist()

df_continuous['resolution'] = df_continuous['resolution'].astype(float)

df_continuous['x'] = df_continuous['x'].astype(float)

df_continuous['y'] = df_continuous['y'].astype(float)

df_continuous['z'] = df_continuous['z'].astype(float)

#%%


bad_indices = []


for i in np.arange(1, len(packet_starts) + 1):
    
    if i < len(packet_starts):
    
        packet = df_continuous.loc[packet_starts[i-1] : packet_starts[i] - 1]
        
        
    else:
        
        packet = df_continuous.loc[packet_starts[i-1] : ]
    
    packet_indices = list(packet.index.values)
 
    count, unique, top, freq = packet["reset_vector"].describe()
    
    res = packet["resolution"]
    
    res_std = np.std(res)
    
    if unique > unique_reset_vecs_cutoff or res_std > res_std_cutoff:

        bad_indices.extend(packet_indices)
        
    else:

        print(unique)
        print(res_std)


#%%

df_filtered = df_continuous.drop(labels = bad_indices, axis = 0)


#%%

savename = filebase + filename + '_cleaned'

savetxt = savename + '.txt'

savecsv = savename + '.csv'


np.savetxt(savetxt, df_filtered.values, fmt = '%s')

df_filtered.to_csv(savecsv, index=False)  

#%%

# could try putting entry and exit times for timestamping into csv file?

# or make a data file?

# maybe data file more straightforward
















