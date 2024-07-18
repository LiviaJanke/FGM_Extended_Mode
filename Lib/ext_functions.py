# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 11:04:31 2024

@author: Livia
"""
import numpy as np

import pandas as pd

import os, fnmatch

import sys

sys.path.append('C:/FGM_Extended_Mode/Lib')

from matplotlib.pyplot import suptitle,xlabel,ylabel,plot,grid,legend,subplot,subplots

from datetime import datetime, timedelta

def s16(val):
    
    value = int(val)
    
    return -(value & 0x8000) | (value & 0x7fff)



def packet_decoding_even(ext_bytes, number):
    
    packig = ext_bytes[number][68:7180]
    
    x_vals = []
    
    y_vals = []
    
    z_vals = []
    
    range_vals = []
    
    reset_vals = []
    
    reset_vals_hex = []
    
    
    for i in np.arange(0,len(packig), 16):
        
        byte_num = i/2
        
        if byte_num < 3552:
            
            x = s16(int(packig[i:i+4],16))
            
            y = s16(int(packig[i+4:i+8],16))
            
            z = s16(int(packig[i+8:i+12],16))
            
            range_val = s16(int(packig[i+12],16))
            
            reset_val = s16(int(packig[i+13:i+16],16))
            
            reset_val_hex = packig[i+13:i+16]
            
        else:

            x= s16(int(packig[i:i+4],16))
            
            y = s16(int(packig[i+4:i+8],16))

            z = 'af'
            
            range_val = 'af'
            
            reset_val = 'af'
            
            reset_val_hex = 'af'
            
        
        x_vals.append(x)
        
        y_vals.append(y)
        
        z_vals.append(z)
        
        range_vals.append(range_val)
        
        reset_vals.append(reset_val)
        
        reset_vals_hex.append(reset_val_hex)
        
    
    df_p = pd.DataFrame(zip(reset_vals_hex, reset_vals, range_vals, x_vals, y_vals, z_vals))
    
    df_p.columns = ['reset_hex', 'reset', 'resolution', 'x', 'y', 'z']    
         
    return df_p


def packet_decoding_odd(ext_bytes, number):
    
    packig = ext_bytes[number][76:7180]
    
    partial_vec_end = ext_bytes[number][68:76]
    
    x_vals = ['bef']
    
    y_vals = ['bef']
    
    z_vals = [s16(int(partial_vec_end[0:4],16))]
    
    range_vals = [s16(int(partial_vec_end[4],16))]
    
    reset_vals = [s16(int(partial_vec_end[5:8],16))]
    
    reset_vals_hex = [partial_vec_end[5:8]]
    
    for i in np.arange(0, len(packig), 16):
                
        x = s16(int(packig[i:i+4],16))
            
        y = s16(int(packig[i+4:i+8],16))
            
        z = s16(int(packig[i+8:i+12],16))
            
        range_val = s16(int(packig[i+12],16))
            
        reset_val = s16(int(packig[i+13:i+16],16))
            
        reset_val_hex = packig[i+13:i+16]

        x_vals.append(x)
        
        y_vals.append(y)
        
        z_vals.append(z)
        
        range_vals.append(range_val)
        
        reset_vals.append(reset_val)
        
        reset_vals_hex.append(reset_val_hex)
    
    df_p = pd.DataFrame(zip(reset_vals_hex, reset_vals, range_vals, x_vals, y_vals, z_vals))
    
    df_p.columns = ['reset_hex', 'reset', 'resolution', 'x', 'y', 'z']    
         
    return df_p


def quickplot(titletext,xlabeltext,ylabeltext, t, r, x, y, z):
    subplots(5,1,sharex=True,height_ratios=[2,2,2,2,1])
    subplot(5,1,1);plot(t,x,label='x');grid();legend();ylabel(ylabeltext)
    subplot(5,1,2);plot(t,y,label='y');grid();legend();ylabel(ylabeltext)
    subplot(5,1,3);plot(t,z,label='z');grid();legend();ylabel(ylabeltext)
    b = np.sqrt(x**2+y**2+z**2)
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

def make_t(ext_entry, t_spin, ext_exit, x):
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

    t = np.array(t)
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    r = np.array(r)
    return t,x,y,z,r


def apply_calparams(t, calparams, r,x,y,z):
    #global x,y,z
    for i in range(0,len(t)):
        Ox = calparams['x_offsets'][r[i]-2]
        Gx = calparams['x_gains'][r[i]-2]
        Gyz = calparams['yz_gains'][r[i]-2]
        x[i] = (x[i] - Ox) / Gx
        y[i] = y[i] / Gyz
        z[i] = z[i] / Gyz
    return x, y, z


def FGMEXT_to_SCS(x, y, z):
    #global x,y,z
    zSCS = np.copy(x)
    xSCS = np.copy(-y)
    ySCS = np.copy(-z)
    x = xSCS
    y = ySCS
    z = zSCS
    return x, y, z

def rotate_SCS(x,y,z):
    #global x,y,z
    degrees = 146.5
    theta = 2*np.pi*degrees/360
    xx,yy = np.copy(x),np.copy(y)
    x = xx*np.cos(theta) - yy*np.sin(theta)
    y = xx*np.sin(theta) + yy*np.cos(theta)
    return x,y,z

def find_cal_file(pentry, pexit, path):

    pattern_entry = '* __' + pentry + '*'
    pattern_exit = '*' + pexit + '*'
    pattern_month_exit = '*' + pexit[:-1] + '*'
    pattern_month_entry = '*' + pexit[:-1] + '*'
    pattern_month_whole = '*' + pexit[:-2] + '*'
    for root, dirs, files in os.walk(path):
        
        for name in files:
                
            if fnmatch.fnmatch(name, pattern_entry):
                return(os.path.join(root, name))
                      
            elif fnmatch.fnmatch(name, pattern_exit):
                return(os.path.join(root, name))
                
            elif fnmatch.fnmatch(name, pattern_month_exit):
                return(os.path.join(root, name))
            
            elif fnmatch.fnmatch(name, pattern_month_entry):
                return(os.path.join(root, name))       
            
            elif fnmatch.fnmatch(name, pattern_month_whole):
                return(os.path.join(root, name))  
            

            

def find_BS_file(date, craft, path):

    pattern_B = craft + '_' + date + '_B.BS'
    
    pattern_K = craft + '_' + date + '_K.BS'
    
    pattern_A = craft + '_' + date + '_A.BS'

    for root, dirs, files in os.walk(path):
        
        for name in files:
                
            if fnmatch.fnmatch(name, pattern_B):
                return(os.path.join(root, name))
                      
            elif fnmatch.fnmatch(name, pattern_K):
                return(os.path.join(root, name))
                
            elif fnmatch.fnmatch(name, pattern_A):
                return(os.path.join(root, name))
            


    



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


def closest_higher_date(date_list, test_date):
    sorted_list = sorted(date_list)
    for date in sorted_list:
        if date >= test_date:
            return date

    return sorted_list[-1]



def get_calibrated_ext_data(index, craft):
    
    Ext_entries_filepath = 'C:/FGM_Extended_Mode/Lib/' + craft + '_Ext_Entries'

    Ext_exits_filepath = 'C:/FGM_Extended_Mode/Lib/' + craft + '_Ext_Exits'

    MSA_dumps_filepath = 'C:/FGM_Extended_Mode/Lib/' + craft + '_MSA_Dump_times'

    starts_stops_spins_df = pd.read_csv('C:/FGM_Extended_Mode/Lib/' + craft + '_SATT_start_stop_spins',names = ['Starts', 'Stops', 'Spins'])

    ext_entries_df = pd.read_csv(Ext_entries_filepath, header = None)

    ext_entries = pd.to_datetime(ext_entries_df[0])

    ext_exits_df = pd.read_csv(Ext_exits_filepath, header = None)

    ext_exits = pd.to_datetime(ext_exits_df[0])

    MSA_dumps_df = pd.read_csv(MSA_dumps_filepath, header = None)

    MSA_dumps = pd.to_datetime(MSA_dumps_df[0])
        

    ext_entry = ext_entries[index]

    next_ext_entry = ext_entries[index + 1]


    if index > 1:
        prev_ext_entry = ext_entries[index - 1]
        
        prev_ext_exit = closest_higher_date(ext_exits, prev_ext_entry)
        
        prev_MSA_dump =  closest_higher_date(MSA_dumps, prev_ext_exit)

    ext_exit = closest_higher_date(ext_exits, ext_entry)

    next_ext_exit = closest_higher_date(ext_exits, next_ext_entry)


    MSA_dump = closest_higher_date(MSA_dumps, ext_exit)

    next_MSA_dump =  closest_higher_date(MSA_dumps, next_ext_exit)

    duration = ext_exit - ext_entry

    if ext_exit > next_ext_entry:
        
        raise Exception("Unmatched Entry")

    if MSA_dump > next_ext_exit:
        
        raise Exception("No Dump")
        
    if duration <= timedelta(seconds = 0):
        
        raise Exception("Negatve/Zero Duration")
        
    early_half = False

    late_half = False

    if MSA_dump.strftime('%Y%m%d') == next_MSA_dump.strftime('%Y%m%d'):
        
        early_half = True
        
    if index > 1:
        
        if MSA_dump.strftime('%Y%m%d') == prev_MSA_dump.strftime('%Y%m%d'):
            
            late_half = True



    closest_start = np.min(abs(pd.to_datetime(starts_stops_spins_df['Starts']) - ext_entry))

    diffs_to_start = abs(pd.to_datetime(starts_stops_spins_df['Starts']) - ext_entry)

    closest_stop = np.min(abs(pd.to_datetime(starts_stops_spins_df['Stops']) - ext_exit))

    diffs_to_stop = abs(pd.to_datetime(starts_stops_spins_df['Stops']) - ext_exit)

    if closest_start < closest_stop:
        
        SATT_index = list(diffs_to_start).index(closest_start)
        
    else:
        
        SATT_index = list(diffs_to_stop).index(closest_stop)

    t_spin = 60 / starts_stops_spins_df['Spins'].iloc[SATT_index]



    dumpdate = MSA_dump.strftime('%Y%m%d')

    year = MSA_dump.strftime('%Y')

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

    packet_resets = []

    if early_half == True:
        
        for i in packets:
            
            if i.status == 15:
                
                packet_resets.append(i.reset)
                
                if len(packet_resets) < 2:
            
                    ext_packets.append(i)
                    
                elif np.abs(packet_resets[-1] - packet_resets[-2]) < 10:
                    
                    ext_packets.append(i)
                    
    if late_half == True:
        
        for i in packets:
            
            if i.status == 15:
                
                packet_resets.append(i.reset)
                
                if len(packet_resets) > 1:
            
                    if np.abs(i.reset - packet_resets[0]) > 200:
                    
                        ext_packets.append(i)

    if early_half == False and late_half == False:

        for i in packets:
        
            packet_resets.append(i.reset)
        
            if i.status == 15:
            
                ext_packets.append(i)
            

    del packets 


    ext_bytes = []

    for i in ext_packets:
        
        hex_vals = i.payload.hex()
        
        ext_bytes.append(hex_vals)


    packet_range = np.arange(0, len(ext_bytes))


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
        
        if eunique < 25:
            
            all_valid_dfs.append(even_df_i)
            
            valid_nums_even_decoded.append(i)
            
        elif ounique < 25:
            
            all_valid_dfs.append(odd_df_i)
            
            valid_nums_odd_decoded.append(i)
            
        else:
            
            no_valid_decode.append(i)
            

        
    sequential_data = pd.concat(all_valid_dfs)

    sequential_data.drop_duplicates(keep = 'first', inplace = True)

    sequential_data.reset_index(drop = True, inplace = True)


    bef_indices = sequential_data.loc[sequential_data['x'] == 'bef'].index.tolist()

    af_indices = sequential_data.loc[sequential_data['z'] == 'af'].index.tolist()


    for i in af_indices:
        
        if i <  len(sequential_data['reset']) - 1 and sequential_data.loc[i+1, 'x'] == 'bef':
        
            sequential_data.loc[i,'reset'] = sequential_data.loc[i+1, 'reset']
            
            sequential_data.loc[i,'reset_hex'] = sequential_data.loc[i+1, 'reset_hex']
        
            sequential_data.loc[i,'resolution'] = sequential_data.loc[i+1, 'resolution']
        
            sequential_data.loc[i,'z'] = sequential_data.loc[i+1,'z']
        
        else:
            
            bef_indices.append(i)
            


    sequential_data.drop(labels = bef_indices, axis = 0, inplace = True)



    sequential_data['reset'] = sequential_data['reset'].astype(float)

    sequential_data['resolution'] = sequential_data['resolution'].astype(int)

    sequential_data['x'] = sequential_data['x'].astype(float)

    sequential_data['y'] = sequential_data['y'].astype(float)

    sequential_data['z'] = sequential_data['z'].astype(float)


    reset_vecs = sequential_data['reset']

    plt.plot(reset_vecs, linewidth = 0, marker = '.')


    sequential_data.reset_index(drop = True, inplace = True)

    max_good_res = int(np.mean(sequential_data['resolution'].values) + np.std(sequential_data['resolution'].values))

    badrange_indices = sequential_data.loc[sequential_data['resolution'] > max_good_res].index.tolist()
            
    for i in badrange_indices:
        
        if i > 5:
        
            sequential_data.loc[i,'resolution'] = sequential_data.loc[i - 5,'resolution'] 
        
        else:
            
            sequential_data.loc[i,'resolution'] = np.median(sequential_data['resolution']) 
            



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
        
    # apply approximate cal using orbit cal see notes 30-Jan-24

    x, y, z = apply_calparams(t, calparams, r, x, y, z)
    quickplot(name+'_calibrated','time [UTC]','[nT]', t,r, x, y, z)


    x, y, z = FGMEXT_to_SCS(x,y,z)
    quickplot(name +'_nominal_scs','time [UTC]','[nT]', t, r, x, y, z)


    x,y,z = rotate_SCS(x,y,z)
    quickplot(name +'_rotated_scs','time [UTC]','[nT]', t, r, x, y, z)

    # Does theta change for rotate_SCS?


    savename = filebase_cal +  '/' + name + '_calibrated.txt'

    fgmsave(savename,t,x,y,z)
        

    print('saved as fgm dp format')
        


        





