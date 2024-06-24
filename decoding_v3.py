# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 20:31:15 2024

@author: Livia
"""

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import datetime

from datetime import date


#%%

filebase = 'C:\FGM_Extended_Mode\BS_data_files'

filename = 'C1_010421_B_BS'

ext = '.txt'

filepath = filebase +'/' + filename + ext

df_with_pos = pd.read_csv(filepath, delimiter = ' ', names = [ 'position_code',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

df = df_with_pos.drop('position_code', axis = 1)

# every packet has 49 bytes of header

# total length of 3611

#%%

def s16(val):
    
    value = int(val)
    
    return -(value & 0x8000) | (value & 0x7fff)


def byte_val(val):
    
    div, rem = divmod(val, 16)
    
    col = int(rem)
     
    row = int(div) 
    
    value = df[col].iloc[row]
    
    return value



def packet_decoding_even(number):
    
    num = int(number)
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    vector_len = 3555
    
    offset = low_high[num][0]
    
    for i in np.arange(0, vector_len, 8):
        
        byte_num = int(offset + i)
        
        if i < 3551:
            
            x_by = (byte_val(byte_num) + byte_val(byte_num + 1))
            
            x_by_nozero = x_by[:-1].lstrip('0')
            
            x_byte = x_by_nozero + x_by[-1]

            x = s16(int(x_byte, 16))
            
            y_by = (byte_val(byte_num + 2) + byte_val(byte_num + 3))
            
            y_nz = y_by[:-1].lstrip('0')
            
            y_byte = y_nz + y_by[-1]
            
            y = s16(int(y_byte, 16))
            
            z_by = (byte_val(byte_num + 4) + byte_val(byte_num + 5))
            
            z_nz = z_by[:-1].lstrip('0')
            
            z_byte = z_nz + z_by[-1]
            
            z = s16(int(z_byte, 16))
            
            range_val = s16(int(byte_val(byte_num + 6)[0], 16))
            
            reset_val = byte_val(byte_num + 6)[1] + byte_val(byte_num + 7)
            
        else:

            x_by = (byte_val(byte_num) + byte_val(byte_num + 1))
            
            x_by_nozero = x_by[:-1].lstrip('0')
            
            x_byte = x_by_nozero + x_by[-1]

            x = s16(int(x_byte, 16))
            
            y_by = (byte_val(byte_num + 2) + byte_val(byte_num + 3))
            
            y_nz = y_by[:-1].lstrip('0')
            
            y_byte = y_nz + y_by[-1]
            
            y = s16(int(y_byte, 16))

            z = 'af'
            
            range_val = 'af'
            
            reset_val = 'af'
            
        
        x_vals.append(x)
        
        y_vals.append(y)
        
        z_vals.append(z)
        
        range_vals.append(range_val)
        
        reset_vals.append(reset_val)
        
    
    df_p = pd.DataFrame(zip(reset_vals, range_vals, x_vals, y_vals, z_vals))
    
    df_p.columns = ['reset', 'resolution', 'x', 'y', 'z']    
         
    return df_p





def packet_decoding_odd(number):
    
    num = int(number)
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    vector_len = 3551
    
    offset = low_high[num][0]
    
    for i in np.arange(0, vector_len, 8):
        
        byte_num = int(offset + i)
        
        if i > 5:
        
            x_by = (byte_val(byte_num + 4) + byte_val(byte_num + 5))
            
            x_by_nozero = x_by[:-1].lstrip('0')
            
            x_byte = x_by_nozero + x_by[-1]
            
            x = s16(int(x_byte, 16))
            
            y_by = (byte_val(byte_num + 6) + byte_val(byte_num + 7))
            
            y_by_nz = y_by[:-1].lstrip('0')
            
            y_byte = y_by_nz + y_by[-1]
            
            y = s16(int(y_byte, 16))
            
            z_by = (byte_val(byte_num) + byte_val(byte_num + 1))
            
            z_by_nz = z_by[:-1].lstrip('0')
            
            z_byte = z_by_nz + z_by[-1]
            
            z = s16(int(z_byte, 16))
            
            range_val = s16(int(byte_val(byte_num + 2)[0], 16))
            
            reset_val = byte_val(byte_num + 2)[1] + byte_val(byte_num + 3)
            
        else:
            
            x = 'bef'
            
            y = 'bef'
            
            z_by = (byte_val(byte_num) + byte_val(byte_num + 1))
            
            z_by_nz = z_by[:-1].lstrip('0')
            
            z_byte = z_by_nz + z_by[-1]
            
            z = s16(int(z_byte, 16))
            
            range_val = s16(int(byte_val(byte_num + 2)[0], 16))
            
            reset_val = byte_val(byte_num + 2)[1] + byte_val(byte_num + 3)
            
        
        x_vals.append(x)
        
        y_vals.append(y)
        
        z_vals.append(z)
        
        range_vals.append(range_val)
        
        reset_vals.append(reset_val)
        
    
    df_p = pd.DataFrame(zip(reset_vals, range_vals, x_vals, y_vals, z_vals))
    
    df_p.columns = ['reset', 'resolution', 'x', 'y', 'z']    
         
    return df_p


#%%

#number of empties

nans = np.sum(df.isna().sum())

#total_bytes

rows = len(df[0])

columns = len(df.iloc[0])

num_of_bytes = (rows * columns) - nans


# packet separation

num_of_packets = num_of_bytes / 3611

#%%

packet_range = np.arange(0, num_of_packets)

packet_lower_indices = np.arange(49, num_of_packets * 3611, 3611) 

packet_higher_indices = np.arange(3610, (num_of_packets * 3611) + 500, 3611)


low_high = np.column_stack((packet_lower_indices, packet_higher_indices))



#%%

even_dfs = []

for i in packet_range:
    
    decdf = packet_decoding_even(int(i))
    
    even_dfs.append(decdf)

#%%

even_df = pd.concat(even_dfs)

#even_df.to_csv('even_decoding_with_index.csv')  

#%%

odd_dfs = []

for i in packet_range:
    
    decdf = packet_decoding_odd(int(i))
    
    odd_dfs.append(decdf)

#%%


odd_df = pd.concat(odd_dfs)

 
#odd_df.to_csv('odd_decoding_with_index.csv', index = False)

#%%

all_decoded_dfs = []

for i in packet_range:
    
    even_df = packet_decoding_even(int(i))
    
    
    all_decoded_dfs.append(even_df)
    
    
    odd_df = packet_decoding_odd(int(i))

    
    all_decoded_dfs.append(odd_df)
    


#%%
    
all_decoded_df = pd.concat(all_decoded_dfs)





#%%

# filtering for quality and only getting sequential even/odd

all_valid_dfs = []

for i in packet_range:
    
    even_df_i = packet_decoding_even(int(i))
    
    ecount, eunique, etop, efreq = even_df_i['reset'].describe()
    
    odd_df_i = packet_decoding_odd(int(i))
    
    ocount, ounique, otop, ofreq = odd_df_i['reset'].describe()
    
    if eunique < 100:
        
        all_valid_dfs.append(even_df_i)
        
    elif ounique < 100:
        
        all_valid_dfs.append(odd_df_i)
        
    else:
        
        print('yikes')
        
#%%    
    
all_valid_df = pd.concat(all_valid_dfs)


#%%

sequential_data = all_valid_df.reset_index()



#%%

incomplete_rows = np.arange(444, len(sequential_data), 889)

for i in incomplete_rows:
    
    #print(sequential_data.loc[i-1])
    print(sequential_data.loc[i])
    print(sequential_data.loc[i+1])


#%%

for i in incomplete_rows:
    
    
    sequential_data.loc[i,'reset'] = sequential_data.loc[i+1, 'reset']
    
    sequential_data.loc[i,'resolution'] = sequential_data.loc[i+1, 'resolution']
    
    sequential_data.loc[i,'z'] = sequential_data.loc[i+1,'z']
    
    
#%%

for i in incomplete_rows:
    
    print(sequential_data.loc[i])
    print(sequential_data.loc[i+1])
    

#%%


df_complete = sequential_data[sequential_data['x'] != "bef"]

#%%

for i in incomplete_rows:
    
    print(df_complete.loc[i-1])
   # print(df_complete.loc[i])


#%%

filebase = 'C:\FGM_Extended_Mode\BS_decoded_files'

filename = 'C1_010421_B_BS'

ext = '.csv'

filepath = filebase +'/' + filename +'_decoded_filtered_v2' + ext

df_complete.to_csv(filepath)


#%%


















