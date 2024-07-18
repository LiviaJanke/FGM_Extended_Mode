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


