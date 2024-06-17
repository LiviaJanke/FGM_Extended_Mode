# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 12:07:30 2024

@author: Livia
"""

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt


#%%

df_test_file = pd.read_csv('Data/C1_020227_ext.txt', header = None)

df_test_file_with_names = pd.read_csv('Data/C1_020227_ext.txt', names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'])

test_df = df_test_file_with_names


#%%

#left to right makes no difference; concerned with Even vs Odd packets

#df_L_TO_R = pd.read_csv('Data/C1_020227_ext_L_TO_R.txt',  names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'],  on_bad_lines='warn')

#df_R_TO_L = pd.read_csv('Data/C1_020227_ext_R_TO_l.txt',  names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'],  on_bad_lines='warn')

#df_raw = pd.read_csv('Data/C1_020227_ext_R_TO_l.txt',  names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'],  on_bad_lines='warn')

df_raw = pd.read_csv('Data/C1_020227_ext_L_TO_R.txt',  names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'],  on_bad_lines='warn')

#%%


df_raw_no_headers = df_raw.dropna(axis = 0, how = 'any')

#%%

# assigning uncleaned data file to 'df' for simplicity

# need to change this later maybe

df = df_raw_no_headers


#count_444 = df['count'][449]

#count_bef = df['count'][456]


# replacing empy values with NaN

#df_no_strings = df.replace(to_replace = '-----', value = np.nan)

# could try re-indexing df to simplify?


#%%

df.reset_index(inplace = True, drop = True)

#this keeps the old index as a second 'index' column

#%%

number_of_packets = len(df['count']) / 445

packet_list = np.arange(1, number_of_packets + 1)

#%%

good_packet_nums = []

even_packet_nums = []

bef_indices = []

incomplete_indices = []

bef_reset_vecs = []

bef_res = []

bef_z = []

for i in packet_list:
    
    packet_num = i
    
#    print(packet_num)
   
#    print(packet_num)
    packet_lower_index = (packet_num - 1) * 445
    
#    print(packet_lower_index)

    packet_higher_index = (packet_num * 445) - 1
    
#    print(packet_higher_index)

    packet_index_list = np.arange(packet_lower_index, packet_higher_index + 1)
    
#    print(packet_index_list)
    
#    print(len(packet_index_list))

    packet = df.loc[packet_lower_index:packet_higher_index] 
    
    packet.reset_index(inplace = True, drop = True)
    
    #identifying even vs odd packets
    
    packet_count = packet['count']
    
    if packet_count.loc[0] == 'bef ':
        
#        print('even')

        even_packet_nums.append(packet_num)
        
        bef_indices.append(packet_lower_index)
        
        print(packet.loc[0])
        
        prev_reset_vector = packet.loc[0]["reset_vector"]
        
        bef_reset_vecs.append(prev_reset_vector)
        
        prev_resolution = packet.loc[0]["resolution"]
        
        bef_res.append(prev_resolution)
        
        prev_z = packet.loc[0]["resolution"]
        
        bef_z.append(prev_z)
        
        
#        print(prev_reset_vector)
    
    else:
        
        print('odd packet')
        
        incomplete_indices.append(packet_higher_index)
        
        
#        print('odd')
        
#        print(packet.loc[0])
    
#    print(packet_count.loc[0])
    
    
#    print(packet["reset_vector"])
    
#    count, unique, top, freq = packet["reset_vector"].describe(include = 'all')
    
#    print(count)
    
#    print(unique)
    
#    print(top)
    
#    print(freq)
    
#    if unique < 355:
    
#        print(unique)
        
#        print(packet)
        
#        good_packet_nums.append(packet_num)


#%%

df_no_bef = df.drop(labels = bef_indices, axis = 0)


#%%

for i in np.arange(0, len(incomplete_indices)):
    
#    print(i)
    
#    print(df.loc[i])

    df_no_bef.loc[incomplete_indices[i], 'reset_vector'] = bef_reset_vecs[i]
    
    df_no_bef.loc[incomplete_indices[i], 'resolution'] = bef_res[i]
    
    df_no_bef.loc[incomplete_indices[i], 'z'] = bef_z[i]
        

#%%
    
    
df_continuous = df_no_bef.reset_index(drop = True)    
    

#counts = np.array((df_continuous['count']))

#packet_starts = df_continuous.loc[df_continuous['count'] == 0].index.tolist()

df_continuous['count'] = df_continuous['count'].astype(float)

packet_starts = df_continuous.loc[df_continuous['count'] == 0].index.tolist()

df_continuous['resolution'] = df_continuous['resolution'].astype(float)

df_continuous['x'] = df_continuous['x'].astype(float)

df_continuous['y'] = df_continuous['y'].astype(float)

df_continuous['z'] = df_continuous['z'].astype(float)

#%%

bad_reset_vector_packets = []

bad_indices = []

ok = []

for i in np.arange(1, len(packet_starts) + 1):
    
    if i < len(packet_starts):
    
        packet = df_continuous.loc[packet_starts[i-1] : packet_starts[i] - 1]
        
        
    else:
        
        packet = df_continuous.loc[packet_starts[i-1] : ]
    
    packet_indices = list(packet.index.values)
    
#    print(packet)
 
    count, unique, top, freq = packet["reset_vector"].describe()
    
    res = packet["resolution"]
    
    res_std = np.std(res)
    
    
    
    if unique > 200 or res_std > 1:
        
        #bad_indices.append(packet_indices)
        bad_indices.extend(packet_indices)
        
    else:
#    print(count)
        print(unique)
        print(res_std)
    
    
#%%

df_filtered = df_continuous.drop(labels = bad_indices, axis = 0)


#%%

for i in np.arange(0, len(bad_indices)):

    df_continuous.drop(labels = bad_indices[i], axis = 0)    
    
    
#%%

    if unique > 200:
        
        bad_reset_vector_packets.append(i)
        
        bad_indices.append(packet_indices)
        
        #df_reset_filter = df_continuous.drop(labels = packet_indices, axis = 0)
 
    else:
        
        ok.append(i)
    
#%%    
    
    
#    packet = df.loc[packet_num - 1 : 444 * packet_num]
    
#    packet_index_list = np.arange(packet_num - 1, packet_num + 444)
    
#    count, unique, top, freq = packet["reset_vector"].describe()
    
#    if unique > 60:
        
#        for i in packet_index_list:
            
#            df.drop([i])

#        print(unique)
            
#    else:
        
#        good_packet_nums.append(packet_num)
    
    
#%%

#for i in np.arange(0, len(df['count'])):
    
#    try:    
        
#        count_val = float(df['count'][456])
        
#        df.replace(to_replace = df['count'][456], value = count_val)
        
#    except ValueError:
        
#        count_val = 445


























