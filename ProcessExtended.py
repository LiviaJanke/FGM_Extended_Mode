#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 16:53:52 2024

@author: cmcarr
"""

# 
# Uses as input files from Tim's web-page tool 
# see email 24-Jan-24
# 

from pandas import read_csv
from matplotlib.pyplot import savefig,suptitle,xlabel,ylabel,plot,grid,legend,subplot,subplots
from datetime import datetime,timedelta
from numpy import sqrt,array,delete,zeros,size,pi,copy,sin,cos

#%% filetools
from sys import path
if not path.count("../../Lib"):
    path.append("../../Lib")
del path

#%%

#from fgmfiletools import fgmsave

#%% open
# filename = 'C1_150605_B_1.RawExtMd'
# filename = 'C2_150605_B_1.RawExtMd'
filepath,filebase,fileext = './020227','C1_020227_ext','txt'
#filename = filepath + '/' + filebase + '.' + fileext
filename = 'C1_020227_ext.txt'
data = read_csv(filename,header=None)
del filename
# decode
# vector_count = data[0][:]
# reset_count_h = data[1][:]
r = data[2][:]
x = data[3][:]
y = data[4][:]
z = data[5][:]
del data
# change to array
r = array(r)
x = array(x)
y = array(y)
z = array(z)
# make a default time-axis
t = range(0,len(x))

#%% quickplot
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
    #savefig(filepath+'/'+titletext+'.png',dpi=150)
    savefig(titletext+'.png',dpi=150)
    return

#quickplot(filebase+'_raw','sample #','count [#]')

quickplot(filebase,'sample #','count [#]')

# Now check plot for any major errors and edit the file if necessary, but try
# to avoid deleting any whole lines as this will mess-up the time-stamping following

#%% timing
# C1 extended mode period in Feb 02
ext_entry = datetime.fromisoformat('2002-02-27T23:34:54.000')#.replace(tzinfo=None)
ext_exit = datetime.fromisoformat('2002-02-28T22:35:00.000')#.replace(tzinfo=None)
# from SATT
t_spin = 4.0165231
# build timeline
def make_t():
    t = []
    for i in range(0,len(x)):
        t.append(ext_entry + timedelta(seconds=i*t_spin))
    print('Last vector time {}'.format(t[len(t)-1]))
    print('Ext Exit time {}'.format(ext_exit))
    print('Difference {}'.format(ext_exit - t[len(t)-1]))
    return t

t = make_t()
quickplot(filebase+'_raw_timestamped','time [UTC]','count [#]')

#%% temporary save for purposes of despiking
def quicksave(filename,t,x,y,z,r):
    file = open(filename,'w')
    for i in range(0,len(t)):
        # aline = t[i].isoformat(timespec='milliseconds')[0:23] + 'Z'
        aline = t[i].isoformat(timespec='milliseconds')
        aline += ", {0: 5d}, {1: 5d}, {2: 5d}, {3: 1d}\n".format(x[i],y[i],z[i],r[i])
        file.write(aline)
    file.close()
    return

#filename = filepath + '/' + filebase + '_raw_timestamped.txt'

filename = filebase + '_raw_timestamped.txt'

quicksave(filename,t,x,y,z,r)
del filename

# now edit and delete bad lines in TeXshop

#%% re-open
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
        x.append(int(alist[1]))
        y.append(int(alist[2]))
        z.append(int(alist[3]))
        r.append(int(alist[4]))

    t = array(t)
    x = array(x)
    y = array(y)
    z = array(z)
    r = array(r)
    return t,x,y,z,r

#filename = filepath + '/' + filebase + '_raw_timestamped.txt'
filename = filebase + '_raw_timestamped.txt'
t,x,y,z,r = quickopen(filename)
del filename
quickplot(filebase+'_raw_timestamped_despiked','time [UTC]','count [#]')

# check correctly despiked before proceeding
    
#%% nominal scaling
# using +/-64nT with 15 bits in range 2
x = x * (2*64/2**15) * 4**(r-2)
y = y * (2*64/2**15) * 4**(r-2) * (pi/4)
z = z * (2*64/2**15) * 4**(r-2) * (pi/4)

quickplot(filebase+'_scaled','time [UTC]','[nT]')

#%% apply approximate cal using orbit cal see notes 30-Jan-24
# C1 cal file for 2002-02-27 to 28
calparams = {'x_offsets':   [-2.737,0,0,0,0,0],\
             'x_gains':     [0.95026,1,1,1,1,1],\
             'yz_gains':    [(0.95260+0.96908)/2,1,1,1,1,1]}

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

apply_calparams()
quickplot(filebase+'_calibrated','time [UTC]','[nT]')
            
#%% data is in 'FGMEXT' coordinates
# make the nominal conversion to SCS
def FGMEXT_to_SCS():
    global x,y,z
    zSCS = copy(x)
    xSCS = copy(-y)
    ySCS = copy(-z)
    x = xSCS
    y = ySCS
    z = zSCS
    return

FGMEXT_to_SCS()
quickplot(filebase+'_nominal_scs','time [UTC]','[nT]')

#%% make the magic rotation
def rotate_SCS():
    global x,y,z
    degrees = 146.5
    theta = 2*pi*degrees/360
    xx,yy = copy(x),copy(y)
    x = xx*cos(theta) - yy*sin(theta)
    y = xx*sin(theta) + yy*cos(theta)
    return

rotate_SCS()
quickplot(filebase+'_rotated_scs','time [UTC]','[nT]')

#%% save data in 'fgm dp' format
savename = filepath + '/' + filebase + '_calibrated.txt'
#fgmsave(savename,t,x,y,z)
            
            