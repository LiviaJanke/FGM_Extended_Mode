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

validphid=(0x1F,0x47,0x6F,0x97,0x26,0x4E,0x76,0x9E,0x2D,0x55,0x7D,0xA5)
sciphid=(0x1F,0x47,0x6F,0x97,0x26,0x4E,0x76,0x9E)
fgmhkphid=(0x2D,0x55,0x7D,0xA5)

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
    
    
#%%

file = open('C1_020227_B.BS',"rb")

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

def packet_decoding_even(number):
    
    packig = ext_bytes[number]
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    
    for i in np.arange(34, 3590, 8):
        
        if i < 3601:
            
            x = packig[i:i+2]
            
            y = packig[i+2:i+4]
            
            z = packig[i+4:i+6]
            
            range_val = packig[i+6][0]
            
            reset_val = packig[i+6][0] + packig[i+7]
            
        else:

            x= packig[i:i+2]
            
            y = packig[i+2:i+4]

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
    
    packig = ext_bytes[number]
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    
    for i in np.arange(34, 3590, 8):
        
        if i > 41:
        
            x= packig[i:i+2]
            
            y = packig[i+2:i+4]
            
            z = packig[i+4:i+6]
            
            range_val = packig[i+6][0]
            
            reset_val = packig[i+6][0] + packig[i+7]
            
        else:
            
            x = 'bef'
            
            y = 'bef'
            
            z = packig[i+4:i+6]
            
            range_val = packig[i+6][0]
            
            reset_val = packig[i+6][0] + packig[i+7]

    
        x_vals.append(x)
        
        y_vals.append(y)
        
        z_vals.append(z)
        
        range_vals.append(range_val)
        
        reset_vals.append(reset_val)
        
    
    df_p = pd.DataFrame(zip(reset_vals, range_vals, x_vals, y_vals, z_vals))
    
    df_p.columns = ['reset', 'resolution', 'x', 'y', 'z']    
         
    return df_p


#%%

    

# filtering for quality and only getting sequential even/odd

valid_nums_even_decoded = []

valid_nums_odd_decoded = []

no_valid_decode = []

all_valid_dfs = []

for i in packet_range:
    
    even_df_i = packet_decoding_even(int(i))
    
    even_df_i['reset'] = even_df_i['reset'].astype(str)
    
    ecount, eunique, etop, efreq = even_df_i['reset'].describe()
    
    odd_df_i = packet_decoding_odd(int(i))
    
    odd_df_i['reset'] = odd_df_i['reset'].astype(str)
    
    ocount, ounique, otop, ofreq = odd_df_i['reset'].describe()
    
    if eunique < 100:
        
        all_valid_dfs.append(even_df_i)
        
        valid_nums_even_decoded.append(i)
        
    elif ounique < 100:
        
        all_valid_dfs.append(odd_df_i)
        
        valid_nums_odd_decoded.append(i)
        
    else:
        
        no_valid_decode.append(i)
        
#%%    
    
all_valid_df = pd.concat(all_valid_dfs)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    