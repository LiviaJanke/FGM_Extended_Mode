# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 09:32:16 2024

@author: Livia
"""


index = 5

craft = 'C1'


# Importing things

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import sys

sys.path.append('C:/FGM_Extended_Mode/Lib')

from fgmfiletools import fgmsave

# Currently uneeded imports

from datetime import datetime

from ext_functions import packet_decoding_even, packet_decoding_odd, quickplot, quicksave, make_t, quickopen, apply_calparams, FGMEXT_to_SCS, rotate_SCS, find_cal_file, find_BS_file, packet


Period_identification_filepath = 'C:/FGM_Extended_Mode/SCCH_strings/' + craft + '_Entry_Exit_Dump_Duration_Tspin.csv'

Entry_Exit_Dump_Duration_Tspin = pd.read_csv(Period_identification_filepath, index_col=0)

ext_entry = datetime.fromisoformat(Entry_Exit_Dump_Duration_Tspin['Entry Time'][index])
ext_exit = datetime.fromisoformat(Entry_Exit_Dump_Duration_Tspin['Exit Time'][index])

ext_dump = datetime.fromisoformat(Entry_Exit_Dump_Duration_Tspin['Dump Time'][index])
t_spin = Entry_Exit_Dump_Duration_Tspin['tspin'][index]

dumpdate = ext_dump.strftime('%Y%m%d')

year = ext_dump.strftime('%Y')

datadate = ext_entry.strftime('%Y%m%d')


calparams_filepath = 'C:/FGM_Extended_Mode/Calibration_files/2001_C1/'

formatted_entry = ext_entry.strftime('%Y%m%d')

formatted_exit = ext_exit.strftime('%Y%m%d')

cal_filename = find_cal_file(formatted_entry, formatted_exit, calparams_filepath)

cal_params = pd.read_csv(cal_filename, skiprows = 58, header = None, sep = ',|:', usecols = range(4), on_bad_lines = 'skip', engine = 'python') 

x_offsets = cal_params[cal_params[0] == 'Offsets (nT)'][1].astype(float).values.tolist()
x_gains = cal_params[cal_params[0] == 'Gains       '][1].astype(float).values.tolist()
y_gains = cal_params[cal_params[0] == 'Gains       '][2].astype(float).values.tolist()
z_gains = cal_params[cal_params[0] == 'Gains       '][3].astype(float).values.tolist()



while len(x_offsets) < 6:
    x_offsets.append(0.0)
    
while len(x_gains) < 6:
    x_gains.append(1.0)

while len(y_gains) < 6:
    y_gains.append(1.0)

while len(z_gains) < 6:
    z_gains.append(1.0)


yz_gains = []

for i in np.arange(0,6):

    yz_gain = (float(y_gains[i]) + float(z_gains[i])) / 2.0
    
    yz_gains.append(yz_gain)
    
x_offsets = [int(i) for i in x_offsets]
x_gains = [int(i) for i in x_gains]
yz_gains = [int(i) for i in yz_gains]

calparams = {'x_offsets':  x_offsets,\
             'x_gains':    x_gains,\
             'yz_gains':   yz_gains}


folder =  year + '_' + craft + '/'

BS_filepath = 'C:/FGM_Extended_Mode/BS_raw_files/' + folder

BS_filename = find_BS_file(dumpdate[2:], craft, BS_filepath)

BS_file_location = BS_filename

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


ext_packets = []

other_packets = []

for i in packets:
    
    if i.status == 15:
        
        ext_packets.append(i)
        
    else:
        
        other_packets.append(i)



del packets 
del other_packets


ext_bytes = []

for i in ext_packets:
    
    hex_vals = i.payload.hex()
    
    ext_bytes.append(hex_vals)


packet_range = np.arange(0, len(ext_bytes) )


# filtering for quality and only getting sequential even/odd

valid_nums_even_decoded = []

valid_nums_odd_decoded = []

no_valid_decode = []

all_valid_dfs = []

for i in packet_range:

    even_df_i = packet_decoding_even(ext_bytes, i)
    
    odd_df_i = packet_decoding_odd(ext_bytes, i)
    
    ecount, eunique, etop, efreq = even_df_i['reset_hex'].describe()
 
    ocount, ounique, otop, ofreq = odd_df_i['reset_hex'].describe()
    
    if eunique < 60:
        
        all_valid_dfs.append(even_df_i)
        
        valid_nums_even_decoded.append(i)
        
    elif ounique < 60:
        
        all_valid_dfs.append(odd_df_i)
        
        valid_nums_odd_decoded.append(i)
        
    else:
        
        no_valid_decode.append(i)
        

    
sequential_data = pd.concat(all_valid_dfs)


sequential_data.reset_index(drop = True, inplace = True)


bef_indices = sequential_data.loc[sequential_data['x'] == 'bef'].index.tolist()

af_indices = sequential_data.loc[sequential_data['z'] == 'af'].index.tolist()


for i in af_indices:
    
    if i <  len(sequential_data['reset']) - 1:
    
        if sequential_data.loc[i+1, 'x'] == 'bef':
    
            sequential_data.loc[i,'reset'] = sequential_data.loc[i+1, 'reset']
        
            sequential_data.loc[i,'reset_hex'] = sequential_data.loc[i+1, 'reset_hex']
    
            sequential_data.loc[i,'resolution'] = sequential_data.loc[i+1, 'resolution']
    
            sequential_data.loc[i,'z'] = sequential_data.loc[i+1,'z']
    
    else:
        
        bef_indices.append(i)

    

sequential_data.drop(labels = bef_indices, axis = 0, inplace = True)

sequential_data.drop_duplicates(keep = 'first', inplace = True)


sequential_data['reset'] = sequential_data['reset'].astype(float)

sequential_data['resolution'] = sequential_data['resolution'].astype(float)

sequential_data['x'] = sequential_data['x'].astype(float)

sequential_data['y'] = sequential_data['y'].astype(float)

sequential_data['z'] = sequential_data['z'].astype(float)



reset_vecs = sequential_data['reset']

plt.plot(reset_vecs, linewidth = 0, marker = '.')



sequential_data.reset_index(drop = True, inplace = True)



filebase_decoded = 'C:/FGM_Extended_Mode/BS_ext_decoded_files'



filepath = filebase_decoded +'/' + craft + '_' + dumpdate + '_clean_decode' + '.csv'

sequential_data.to_csv(filepath)

del filepath


# timestamping and scaling decoded file

r = sequential_data['resolution']
x = sequential_data['x']
y = sequential_data['y']
z = sequential_data['z']

# change to array

r = np.array(r)
x = np.array(x)
y = np.array(y)
z = np.array(z)
# make a default time-axis
t = range(0,len(x))

t = make_t(ext_entry, t_spin, ext_exit, x)


name = craft + '_' + datadate 

quickplot(name +'_raw','sample #','count [#]', t, r, x, y, z)

filebase_cal = 'C:/FGM_Extended_Mode/BS_ext_calibrated_files'

#filename = filebase_cal + '/' + name + '_raw_timestamped.txt'

#quicksave(filename,t,x,y,z,r)

#t,x,y,z,r = quickopen(filename)

quickplot(name +'_raw_timestamped_despiked','time [UTC]','count [#]', t, r, x, y, z)


#nominal scaling

#nominal change from engineering units to nanotesla

# using +/-64nT with 15 bits in range 2

x = x * (2*64/2**15) * 4**(r-2)
y = y * (2*64/2**15) * 4**(r-2) * (np.pi/4)
z = z * (2*64/2**15) * 4**(r-2) * (np.pi/4)

quickplot(name +'_scaled','time [UTC]','[nT]', t, r, x, y, z)
    
# Does scaling also need to be made more versatile to apply to all ranges?
# Apparently no

# apply approximate cal using orbit cal see notes 30-Jan-24

apply_calparams(t, calparams, r)
quickplot(name+'_calibrated','time [UTC]','[nT]', t,r, x, y, z)


FGMEXT_to_SCS()
quickplot(name +'_nominal_scs','time [UTC]','[nT]', t, r, x, y, z)


rotate_SCS()
quickplot(name +'_rotated_scs','time [UTC]','[nT]', t, r, x, y, z)

# Does theta change for rotate_SCS?


savename = filebase_cal +  '/' + name + '_calibrated.txt'

fgmsave(savename,t,x,y,z)
    

print('saved as fgm dp format')
    

    
    
    
    