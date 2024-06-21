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

df_with_pos = pd.read_csv('C:\FGM_Extended_Mode\BS_data_files\C1_010421_B_BS.txt', delimiter = ' ', names = [ 'position_code',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

df = df_with_pos.drop('position_code', axis = 1)

# every packet has 49 bytes of header

# total length of 3611

#%%

def byte_location(val):
    
    row, col = divmod(val, 16)
    
    return row, col


def byte_val(val):
    
    div, rem = divmod(val, 16)
    
    col = rem
     
    row = div    
    
    value = df[col].iloc[row]
    
    return value

def packet_decoding_even(packet):
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    for i in np.arange(0, len(packet), 8):
        
        x = int(packet[i] + packet[i + 1], 16)
        
        x_vals.append(x)
        
    for i in np.arange(2, len(packet), 8):
        
        y = int(packet[i] + packet[i + 1], 16)
        
        y_vals.append(y)
        
    for i in np.arange(4, len(packet), 8):
        
        if i < 3557:
        
            z = int(packet[i] + packet[i + 1], 16)
        
        else:
            
            z = 'bef'
        
        z_vals.append(z)
        
    for i in np.arange(6, len(packet), 8):
        
        if i < 3557:
        
            range_val = int(packet[i][0], 16)
        
        else:
            
            range_val = 'bef'
        
        range_vals.append(range_val)
        
    for i in np.arange(6, len(packet), 8):
        
        if i < 3557:
        
            reset_val = packet[i][1] + packet[i+1]
            
        else: reset_val = 'bef'
        
        reset_vals.append(reset_val)
        
        
    return x_vals, y_vals, z_vals, range_vals, reset_vals

#%%

def packet_decoding_odd(packet):
    
    x_vals = ['prev',]
    
    y_vals = ['prev',]
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    for i in np.arange(4, len(packet) - 8, 8):
        
        x = int(packet[i] + packet[i + 1], 16)
        
        x_vals.append(x)
        
    for i in np.arange(6, len(packet) - 8, 8):
        
        y = int(packet[i] + packet[i + 1], 16)
        
        y_vals.append(y)
        
    for i in np.arange(0, len(packet) -8, 8):

        
        z = int(packet[i] + packet[i + 1], 16)
        
        z_vals.append(z)
        
    for i in np.arange(0, len(packet) -8, 8):
        
        range_val = int(packet[i][0], 16)
        
        range_vals.append(range_val)
        
    for i in np.arange(6, len(packet) - 8, 8):
        
        reset_val = packet[i][1] + packet[i+1]
        
        reset_vals.append(reset_val)
             
    return x_vals, y_vals, z_vals, range_vals, reset_vals

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


packet_lower_indices = np.arange(0, num_of_packets * 3611, 3611) + 49

packet_higher_indices = np.arange(3611 , (num_of_packets * 3611) +1, 3611)


low_high = np.column_stack((packet_lower_indices, packet_higher_indices))

#%%

def get_packet(num):
    
    packet = []

    for i in np.arange(int(low_high[num][0]), int(low_high[num][1])):
        
        bite = byte_val(i)
         
        packet.append(bite)
    
    return packet


def decode_packet_even(num):
    
    p = get_packet(num)

    x,y,z, resolution, reset = packet_decoding_even(p)
    
    df_p = pd.DataFrame(zip(reset, resolution, x, y, z))
    
    return df_p

def decode_packet_odd(num):
    
    p = get_packet(num)

    x,y,z, resolution, reset = packet_decoding_odd(p)
    
    df_p = pd.DataFrame(zip(reset, resolution, x, y, z))
    
    return df_p
    
    

#%%

even_dfs = []

for i in packet_range:
    
    decdf = decode_packet_even(int(i))
    
    even_dfs.append(decdf)

even_df = pd.concat(even_dfs)

even_df.columns = ['reset', 'resolution', 'x', 'y', 'z']

#%%

odd_dfs = []

for i in packet_range:
    
    decdf = decode_packet_odd(int(i))
    
    odd_dfs.append(decdf)

odd_df = pd.concat(odd_dfs)

odd_df.columns = ['reset', 'resolution', 'x', 'y', 'z']

#%%

even_df.to_csv('even_decoding.csv', index=False)  

odd_df.to_csv('odd_decoding.csv', index = False)








