# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:34:02 2024

@author: Livia
"""


import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import datetime

from datetime import date

#%%

#the 6 digit thing at the start is just some kind of positioning code 


df = pd.read_csv('C:\FGM_Extended_Mode\BS_data_files\C1_010421_B_BS.txt', delimiter = ' ', names = [ 'position_code',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])

#df[2]=df[1].str.slice(start=2, stop = 4)

#df[3]=df[1].str.slice(start=4)

#df[1]=df[1].str.slice(stop=2)


#cols = np.arange(1,17)

#cols = np.arange(1,20)

#df = df[cols]


#%%



# 34 bytes for FGM Science Header
# 49 bytes including the DDS Header


# 49-3610 BS Science Data (3562 bytes)
# A full byte (octet) is represented by two hexadecimal digits (00–FF)


def byte_location(val):
    
    row, col = divmod(val, 16)
    
    return row, col


def byte_val(val):
    
    div, rem = divmod(val, 16)
    
#    if rem == 0:
        
#        col = 19
    
#    else:
        
    col = rem
     
    row = div    
    
    value = df[col].iloc[row]
    
    return value


#%%
    
header_bytes = []


for i in np.arange(0,49):
    
    location = byte_location(i)
    
    #print(location)
    
    bite = byte_val(i)
    
    #print(bite)
    
    header_bytes.append(bite)
    
    
#%%
    
# Decoding as Even

packet_1 = []

for i in np.arange(49, 3611):                #3601):
#for i in np.arange(678,4283):
    
    #location = byte_location(i)
    
    #print(location)
    
    bite = byte_val(i)
    
    #print(bite)
    
    packet_1.append(bite)
    
    
x1 = int(packet_1[0] + packet_1[1], 16) 
    
y1 = int(packet_1[2] + packet_1[3], 16)   

z1 = int(packet_1[4] + packet_1[5], 16) 

range1 = packet_1[6][0]

reset1 = packet_1[6][1] +  packet_1[7]
 

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
        
 #   for i in np.arange(len(packet_1) -10, len(packet_1))
        
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
        
 #   for i in np.arange(len(packet_1) -10, len(packet_1))
        
    return x_vals, y_vals, z_vals, range_vals, reset_vals
        
    
    
#%%

x,y,z,ra,re = packet_decoding_odd(packet_1)

# Even decoding is working!






