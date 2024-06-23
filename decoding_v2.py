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
    
    vector_len = 3556
    
    offset = low_high[num][0]
    
    for i in np.arange(0, vector_len, 8):
        
        byte_num = int(offset + i)
        
        if i < 3557:
        
            x = s16(int((byte_val(byte_num) + byte_val(byte_num + 1)).lstrip('0'), 16))
            
            y = s16(int((byte_val(byte_num + 2) + byte_val(byte_num + 3)).lstrip('0'), 16))
            
            z = s16(int((byte_val(byte_num + 4) + byte_val(byte_num + 5)).lstrip('0'), 16))
            
            print((byte_val(byte_num + 4) + byte_val(byte_num + 5)))
            
            print(z)
            
            print(byte_num)
            
            range_val = s16(int(byte_val(byte_num + 6)[0], 16))
            
            reset_val = byte_val(byte_num + 6)[1] + byte_val(byte_num + 7)
            
        else:

            x = s16(int((byte_val(byte_num) + byte_val(byte_num + 1)).lstrip('0'), 16))
            
            y = s16(int((byte_val(byte_num + 2) + byte_val(byte_num + 3)).lstrip('0'), 16))            

            z = 'bef'
            
            range_val = 'bef'
            
            reset_val = 'bef'
            
        
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
    
    vector_len = 3556
    
    offset = low_high[num][0]
    
    for i in np.arange(0, vector_len, 8):
        
        byte_num = int(offset + i)
        
        if i > 5:
        
            x = s16(int((byte_val(byte_num + 4) + byte_val(byte_num + 5)).lstrip('0'), 16))
            
            y = s16(int((byte_val(byte_num + 6) + byte_val(byte_num + 7)).lstrip('0'), 16))
            
            z = s16(int((byte_val(byte_num) + byte_val(byte_num + 1)).lstrip('0'), 16))
            
            
            range_val = s16(int(byte_val(byte_num + 2)[0], 16))
            
            reset_val = byte_val(byte_num + 2)[1] + byte_val(byte_num + 3)
            
        else:
            
            x = 'prev'
            
            y = 'prev'
            
            z = s16(int((byte_val(byte_num) + byte_val(byte_num + 1)).lstrip('0'), 16))
            
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


not_working = packet_decoding_even(5)

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

even_df.to_csv('even_decoding_with_index.csv')  

#%%

odd_dfs = []

for i in packet_range:
    
    decdf = packet_decoding_odd(int(i))
    
    odd_dfs.append(decdf)

#%%

odd_df = pd.concat(odd_dfs)

 
#%%
odd_df.to_csv('odd_decoding_with_index.csv', index = False)

#%%

all_decoded_dfs = []

for i in packet_range:
    
    even_df = packet_decoding_even(int(i))
    
    print(i)
    
    all_decoded_dfs.append(even_df)
    
    print(i)
    
    odd_df = packet_decoding_odd(int(i))
    
    print(i)
    
    all_decoded_dfs.append(odd_df)
    
    print(i)

#%%
    
all_decoded_df = pd.concat(all_decoded_dfs)



#%%

filebase = 'C:\FGM_Extended_Mode\BS_decoded_files'

filename = 'C1_010421_B_BS'

ext = '.csv'

filepath = filebase +'/' + filename +'_decoded' + ext

all_decoded_df.to_csv(filepath)

#%%


data = int('0xffd2', 16)





