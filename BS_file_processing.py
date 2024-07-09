# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 09:32:16 2024

@author: Livia
"""

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import datetime

from datetime import date

from fgmfiletools import fgmsave, fgmopen_cef, fgmopen_dp, fgmopen


from datetime import datetime,timedelta
from scipy.stats import linregress
import sys

# ID definitions

validphid=(0x1F,0x47,0x6F,0x97,0x26,0x4E,0x76,0x9E,0x2D,0x55,0x7D,0xA5)
sciphid=(0x1F,0x47,0x6F,0x97,0x26,0x4E,0x76,0x9E)
fgmhkphid=(0x2D,0x55,0x7D,0xA5)

# Classes

class packet():

    counter=0

    # .cdds is the CDDS packet header bytes (15)
    # .size is the packet size from that CDDS header
    # .payload are the bytes of the payload packet, so everything that isn't the CDDS header
    # .reset is the packet reset count, from the appropriate part of the FGM header
    # .micros are the total microseconds from a combination of the days, milliseconds and microseconds
    # .scet is the time, in Python format, from the .micros
    # .pktcnt is a one-up count of each packet (ie order by presence in file)
    # counter is a count of all the packets ever initialised
    

    def __init__(self,d):
        self.cdds=d[0:15]
        self.size=int.from_bytes(d[9:12],"big")
        self.payload=d[15:15+self.size]
        self.status = d[16]
        
        if self.cdds[8] in sciphid:
            self.reset=int.from_bytes(self.payload[12:14],"big")
        elif self.cdds[8] in fgmhkphid:
            self.reset=(int.from_bytes(self.payload[8:10],"big")+65537)%65536
        else:
            self.reset=-1
        self.micros= int.from_bytes(self.cdds[0:2],"big")*86400*1000000+int.from_bytes(self.cdds[2:6],"big")*1000+int.from_bytes(self.cdds[6:8],"big")
        self.scet=timedelta(microseconds=self.micros)+datetime(1958,1,1)
        
        self.pktcnt=packet.counter
        packet.counter+=1
    
    def __str__(self):
        return("{:7s}".format("#"+str(self.pktcnt))+" | "+" ".join('{:02X}'.format(n) for n in self.cdds)+" | "+" ".join('{:02X}'.format(n) for n in self.payload[0:30]))



    
    

class odd_ext_packet():
    
    def __init__(self,d):
        
        self.pcktheader = d[0:34]
        
        self.prev = d[34:42]
        
        self.vectors = d[42:3590]
        
        self.end_str = d[3590:]
    
    
    def __str__(self):
        
        return('odd packet')        
        




class even_ext_packet():
    
    def __init__(self,d):
        
        self.pcktheader = d[0:34]
        
        self.vectors = d[34:3586]
        
        self.partial = d[3586:3590]
        
        self.end_str = d[3590:].hex()
        
        self.end_vals=int.from_bytes(d[3590:],"big")
        
    
    def __str__(self):
        
        return('even packet')
    
class ext_vector():
    
    def __init__(self,d):
        
        self.x = int.from_bytes(d[0:2], 'big')

        self.y = int.from_bytes(d[2:4], 'big')
        
        self.z = int.from_bytes(d[4:6], 'big')
        
        self.range = str(d[6])[0]
        
        self.reset = str(d[6])[1] + str(d[7])
    
    def __str__(self):
        return(self.x, self.y, self.z, self.range, self.reset)


# Functions

def s16(val):
    
    value = int(val)
    
    return -(value & 0x8000) | (value & 0x7fff)

def packet_decoding_even(number):
    
    packig = ext_bytes[number][68:7180]
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    
    for i in np.arange(0,len(packig), 16):
        
        byte_num = i/2
        
        if byte_num < 3552:
            
            x = s16(int(packig[i:i+4],16))
            
            y = s16(int(packig[i+4:i+8],16))
            
            z = s16(int(packig[i+8:i+12],16))
            
            range_val = s16(int(packig[i+12],16))
            
            reset_val = s16(int(packig[i+13:i+16],16))
            
        else:

            x= s16(int(packig[i:i+4],16))
            
            y = s16(int(packig[i+4:i+8],16))

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
    
    packig = ext_bytes[number][68:7180]
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    
    for i in np.arange(0, len(packig) - 16, 16):
        
        byte_num = i/2
        
        if byte_num > 4:
        
            x = s16(int(packig[i:i+4],16))
            
            y = s16(int(packig[i+4:i+8],16))
            
            z = s16(int(packig[i+8:i+12],16))
            
            range_val = s16(int(packig[i+12],16))
            
            reset_val = s16(int(packig[i+13:i+16],16))
            
        else:
            
            x = 'bef'
            
            y = 'bef'
            
            z = s16(int(packig[i:i+4],16))
            
            range_val = s16(int(packig[i+5],16))
            
            reset_val = s16(int(packig[i+6:i+8],16))
            

    
        x_vals.append(x)
        
        y_vals.append(y)
        
        z_vals.append(z)
        
        range_vals.append(range_val)
        
        reset_vals.append(reset_val)
        
    
    df_p = pd.DataFrame(zip(reset_vals, range_vals, x_vals, y_vals, z_vals))
    
    df_p.columns = ['reset', 'resolution', 'x', 'y', 'z']    
         
    return df_p



    
#%%

craft_dumpdate = 'C1_020227_B'

BS_filename = craft_dumpdate +'.BS'

file = open(BS_filename,"rb")

# this is the file dumped on 020227
# contains data from 2002-02-27T01:19:54.000Z Entry to 2002-02-27T08:25:54.000Z Exit
# data len  7.1 hours 
# plus an MSA dump (BM1)
# total num of packets in file is 2931

# D Burst Science packets have size 2232

# Normal Science and Data Dump both have size 3596



data=bytearray(file.read())
file.close()
datalen=len(data)    
    


packets=[]
offset=0

while True:
    packets.append(packet(data[offset:]))
    offset+=15+len(packets[-1].payload)
    if packets[-1].payload[0]==0 and packets[-1].payload[1]==0x0E:
        packets=packets[:-1]
    if offset>=datalen:
        break
    



#%%

del data

#%%

ext_packets = []

other_packets = []

for i in packets:
    
    if i.status == 15:
        
        ext_packets.append(i)
        
    else:
        
        other_packets.append(i)

#%%

del packets 
del other_packets

#%%

ext_bytes = []

for i in ext_packets:
    
    hex_vals = i.payload.hex()
    
    ext_bytes.append(hex_vals)




#%%

num_of_packets = len(ext_bytes) 

packet_range = np.arange(0, num_of_packets)



#%%

    

# filtering for quality and only getting sequential even/odd

valid_nums_even_decoded = []

valid_nums_odd_decoded = []

no_valid_decode = []

all_valid_dfs = []

for i in packet_range:
    
    even_df_i = packet_decoding_even(i)
    
    even_df_i['reset'] = even_df_i['reset'].astype(str)
    
    ecount, eunique, etop, efreq = even_df_i['reset'].describe()
    
    odd_df_i = packet_decoding_odd(i)
    
    odd_df_i['reset'] = odd_df_i['reset'].astype(str)
    
    ocount, ounique, otop, ofreq = odd_df_i['reset'].describe()
    
    if eunique < 60:
        
        all_valid_dfs.append(even_df_i)
        
        valid_nums_even_decoded.append(i)
        
    elif ounique <60:
        
        all_valid_dfs.append(odd_df_i)
        
        valid_nums_odd_decoded.append(i)
        
    else:
        
        no_valid_decode.append(i)
        
#%%    
    
all_valid_df = pd.concat(all_valid_dfs)

del all_valid_dfs

    
#%%

sequential_data = all_valid_df.reset_index(drop = True)

del all_valid_df



#%%

bef_indices = sequential_data.loc[sequential_data['x'] == 'bef'].index.tolist()

af_indices = sequential_data.loc[sequential_data['z'] == 'af'].index.tolist()


#%%

for i in af_indices:
    
    if i <  len(sequential_data['reset']) - 1:
    
        sequential_data.loc[i,'reset'] = sequential_data.loc[i+1, 'reset']
    
        sequential_data.loc[i,'resolution'] = sequential_data.loc[i+1, 'resolution']
    
        sequential_data.loc[i,'z'] = sequential_data.loc[i+1,'z']
    
    else:
        
        bef_indices.append(i)

    

#%%


df_complete_indexed = sequential_data.drop(labels = bef_indices, axis = 0)

del sequential_data

#%%

df_complete_indexed['reset'] = df_complete_indexed['reset'].astype(float)

df_complete_indexed['resolution'] = df_complete_indexed['resolution'].astype(float)

df_complete_indexed['x'] = df_complete_indexed['x'].astype(float)

df_complete_indexed['y'] = df_complete_indexed['y'].astype(float)

df_complete_indexed['z'] = df_complete_indexed['z'].astype(float)

#%%

reset_vecs = df_complete_indexed['reset']

plt.plot(reset_vecs, linewidth = 0, marker = '.')


#%%

df_complete = df_complete_indexed.reset_index(drop = True)


#%%

filebase = 'C:\FGM_Extended_Mode\BS_decoded_files'



ext = '.csv'

filepath = filebase +'/' + craft_dumpdate + '_clean_decode' + ext

df_complete.to_csv(filepath)

#%%

#timestamping code stuff

i=0
start=0
while i<(len(packets)-1):
    if (packets[i+1].reset)<(packets[i].reset):
        resets=[p.reset for p in packets[start:i+1]]
        listmicros=[p.micros for p in packets[start:i+1]]
        slope,intercept,rvalue, pvalue,stderr=linregress(resets,listmicros)
        regressionvalues=[p.reset*slope+intercept for p in packets[start:i+1]]

        print(min(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),max(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),sep=" ",end=" ")
        print("{:04X}".format(min(p.reset for p in packets[start:i+1])),"{:04X}".format(max(p.reset for p in packets[start:i+1])),end=" ")
        print("{:23.15f}".format(slope),"{:19.2f}".format(intercept))
        start=i+1
    i+=1
    


resets=[p.reset for p in packets[start:i+1]]
size=[p.size for p in packets[start:i+1]]
listmicros=[p.micros for p in packets[start:i+1]]
slope,intercept,rvalue, pvalue,stderr=linregress(resets,listmicros)
regressionvalues=[p.reset*slope+intercept for p in packets[start:i+1]]    
contents = [p.payload for p in packets[start:i+1]]
status = [p.status for p in packets[start:i+1]]

counts = [p.pktcnt for p in packets[start:i+1]]


print(min(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),max(p.scet for p in packets[start:i+1]).strftime("%Y-%m-%dT%H:%M:%SZ"),sep=" ",end=" ")
print("{:04X}".format(min(p.reset for p in packets[start:i+1])),"{:04X}".format(max(p.reset for p in packets[start:i+1])),end=" ")
print("{:23.15f}".format(slope),"{:19.2f}".format(intercept))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    