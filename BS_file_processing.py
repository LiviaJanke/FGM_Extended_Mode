# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 09:32:16 2024

@author: Livia
"""


# Importing things

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import datetime

#%%

# Currently uneeded imports

from datetime import date

from fgmfiletools import fgmsave, fgmopen_cef, fgmopen_dp, fgmopen

from pandas import read_csv
from matplotlib.pyplot import savefig,suptitle,xlabel,ylabel,plot,grid,legend,subplot,subplots
from datetime import datetime,timedelta
from numpy import sqrt,array,delete,zeros,size,pi,copy,sin,cos

from datetime import datetime,timedelta
from scipy.stats import linregress
import sys

#%%

# Defining things

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


def quickplot(titletext,xlabeltext,ylabeltext):
    subplots(5,1,sharex=True,height_ratios=[2,2,2,2,1])
    subplot(5,1,1);plot(t,x,label='x');grid();legend();ylabel(ylabeltext)
    subplot(5,1,2);plot(t,y,label='y');grid();legend();ylabel(ylabeltext)
    subplot(5,1,3);plot(t,z,label='z');grid();legend();ylabel(ylabeltext)
    b = sqrt(x**2+y**2+z**2)
    subplot(5,1,4);plot(t,b,label='B');grid();legend();ylabel(ylabeltext)
    subplot(5,1,5);plot(t,r,label='range');grid();legend()
    xlabel(xlabeltext)
    suptitle(titletext,y=0.94)
    return

def quicksave(filename,t,x,y,z,r):
    file = open(filename,'w')
    for i in range(0,len(t)):
        # aline = t[i].isoformat(timespec='milliseconds')[0:23] + 'Z'
        aline = t[i].isoformat(timespec='milliseconds')
        aline += ", {0: 5f}, {1: 5f}, {2: 5f}, {3: 1f}\n".format(x[i],y[i],z[i],r[i])
        file.write(aline)
    file.close()
    return

def make_t():
    t = []
    for i in range(0,len(x)):
        t.append(ext_entry + timedelta(seconds=i*t_spin))
    print('Last vector time {}'.format(t[len(t)-1]))
    print('Ext Exit time {}'.format(ext_exit))
    print('Difference {}'.format(ext_exit - t[len(t)-1]))
    return t


def quickopen(filename):
    lines = [] 
    with open(filename) as f:
        for row in f:
            lines.append(row)    
        
    t = []
    x = []
    y = []
    z = []
    r = []
    for i in range(0,len(lines)):
        aline = lines[i]
        alist = aline.split(',')
        timestring = alist[0][0:len(alist[0])-1]
        t.append(datetime.fromisoformat(timestring).replace(tzinfo=None))
        x.append(int(float(alist[1])))
        y.append(int(float(alist[2])))
        z.append(int(float(alist[3])))
        r.append(int(float(alist[4])))

    t = array(t)
    x = array(x)
    y = array(y)
    z = array(z)
    r = array(r)
    return t,x,y,z,r


def apply_calparams():
    global x,y,z
    for i in range(0,len(t)):
        Ox = calparams['x_offsets'][r[i]-2]
        Gx = calparams['x_gains'][r[i]-2]
        Gyz = calparams['yz_gains'][r[i]-2]
        x[i] = (x[i] - Ox) / Gx
        y[i] = y[i] / Gyz
        z[i] = z[i] / Gyz
    return


def FGMEXT_to_SCS():
    global x,y,z
    zSCS = copy(x)
    xSCS = copy(-y)
    ySCS = copy(-z)
    x = xSCS
    y = ySCS
    z = zSCS
    return

def rotate_SCS():
    global x,y,z
    degrees = 146.5
    theta = 2*pi*degrees/360
    xx,yy = copy(x),copy(y)
    x = xx*cos(theta) - yy*sin(theta)
    y = xx*sin(theta) + yy*cos(theta)
    return

    
#%%

# Change here to desired spacecraft and dump date 

craft = 'C1'

# Time of data dump

year = '2001'
month = '03'
day = '31'

dumpdate = '010331' # in format yymmdd

code = '_B' # Can also be _K for CD data or _A for 1 day pull data 

# Times at which spacecraft entered and left extended mode


ext_entry = datetime.fromisoformat('2001-03-29T14:19:29.000')
ext_exit = datetime.fromisoformat('2001-03-30T13:19:35.000')

datadate = '010329'

# from SATT
# for the datadate, not the dump date

t_spin = 60 / 14.976073


# C1 cal file for 2002-02-27 to 28
calparams = {'x_offsets':   [-2.737,0,0,0,0,0],\
             'x_gains':     [0.95026,1,1,1,1,1],\
             'yz_gains':    [(0.95260+0.96908)/2,1,1,1,1,1]}




#%%

folder =  year + '_' + craft + '/'

BS_filepath = 'C:/FGM_Extended_Mode/BS_raw_files/' + folder

BS_filename = craft + '_' + dumpdate + code + '.BS'

BS_file_location = BS_filepath + BS_filename

file = open(BS_file_location,"rb")

# this is the entire BS file retrieved on the dump date, including Burst Science data 

# D Burst Science packets have size 2232

# Normal Science and Data Dump (aka Extended Mode ?) both have size 3596


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
    

del data

#%%

ext_packets = []

other_packets = []

for i in packets:
    
    if i.status == 15:
        
        ext_packets.append(i)
        
    else:
        
        other_packets.append(i)



del packets 
del other_packets

#%%

ext_bytes = []

for i in ext_packets:
    
    hex_vals = i.payload.hex()
    
    ext_bytes.append(hex_vals)



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

filebase_decoded = 'C:/FGM_Extended_Mode/BS_ext_decoded_files'

ext = '.csv'

filepath = filebase_decoded +'/' + craft + '_' + dumpdate + code + '_clean_decode' + ext

df_complete.to_csv(filepath)

del filepath

#%%

# timestamping and scaling decoded file

r = df_complete['resolution']
x = df_complete['x']
y = df_complete['y']
z = df_complete['z']

# change to array

r = array(r)
x = array(x)
y = array(y)
z = array(z)
# make a default time-axis
t = range(0,len(x))

t = make_t()

#%%

name = craft + '_' + datadate + code 

quickplot(name +'_raw','sample #','count [#]')

filebase_cal = 'C:/FGM_Extended_Mode/BS_ext_calibrated_files'

filename = filebase_cal + '/' + name + '_raw_timestamped.txt'

quicksave(filename,t,x,y,z,r)

#%%

t,x,y,z,r = quickopen(filename)

quickplot(name +'_raw_timestamped_despiked','time [UTC]','count [#]')


#%% nominal scaling

#nominal change from engineering units to nanotesla

# using +/-64nT with 15 bits in range 2

x = x * (2*64/2**15) * 4**(r-2)
y = y * (2*64/2**15) * 4**(r-2) * (pi/4)
z = z * (2*64/2**15) * 4**(r-2) * (pi/4)

quickplot(name +'_scaled','time [UTC]','[nT]')
    
# Does scaling also need to be made more versatile to apply to all ranges?

#%% apply approximate cal using orbit cal see notes 30-Jan-24

# May need to change cal params in start of script


apply_calparams()
quickplot(name+'_calibrated','time [UTC]','[nT]')
    
    
#%%

FGMEXT_to_SCS()
quickplot(name +'_nominal_scs','time [UTC]','[nT]')

#%%

rotate_SCS()
quickplot(name +'_rotated_scs','time [UTC]','[nT]')

#%%

savename = filebase_cal +  '/' + name + '_calibrated.txt'

fgmsave(savename,t,x,y,z)
    

#%%

print('saved as fgm dp format')
    
    
    
    
    
    