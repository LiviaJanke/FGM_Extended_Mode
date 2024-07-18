#!/usr/bin/env python
# coding: utf-8

#%% Load packages
# from datetime import timedelta
# from numpy import pi,sqrt,arccos,arctan2,array,linspace
# from matplotlib.pyplot import xlabel,ylabel,subplot,grid
# from matplotlib.pyplot import suptitle,subplots
# from matplotlib.pyplot import rcParams
# rcParams['text.usetex'] = False
# rcParams['mathtext.default'] = 'regular'
# from scipy.fft import fft,fftfreq
# from scipy.integrate import trapz
# from scipy.signal import spectrogram,welch
# from numpy import log10,shape,argmax,linspace,pi,arange
# from numpy import sqrt,argwhere
# from numpy.random import normal
# from matplotlib.pyplot import pcolormesh,colorbar,loglog,title
# from matplotlib.pyplot import semilogy

#%% filetools
from sys import path
orbitpath = '../Lib'
if not path.count(orbitpath):
    path.append(orbitpath)

from fgmfiletools import fgmopen
from fgmplottools import fgmplot
# from orbitinfo import get_orbit_times,filename_finder

from fgmplotparams import fgmplotParams
fgmplotParams['figsize'] = (10,12)

#%% Open a file processed with the DP software
# C1 = fgmopen('/Volumes/cmcarr/dp','C1_240511_NS.txt')
# C3 = fgmopen('/Volumes/cmcarr/dp','C3_240511_NS.txt')
# C4 = fgmopen('/Volumes/cmcarr/dp','C4_240511_NS.txt')

#%% Plot whole file
# fgmplot([C1,C3,C4])

#%% Plot interval
# interval_start = dataset['data_start'] + timedelta(minutes=10)
# interval_end = interval_start + timedelta(minutes=20)
# fgmplot(dataset, interval_start, interval_end)

#%% find a file
# NB see better methods in multispacecraft
# orbit_number = 3517
# orbit_start,orbit_end = get_orbit_times(orbit_number,fgmdatasetParams['orbitpath'])
# filenamelist = filename_finder(orbit_start,orbit_end,spacecraft=['C1'],product='5VPS',version=1,orbitpath=fgmdatasetParams['orbitpath'])
# print(filenamelist)
# filename = filenamelist[0]['filenames'][0]
# print(filename)

#%% open CEF files in this folder
# C1 = fgmopen('./','C1_CP_FGM_5VPS__20010102_055913_20010104_150531_V01.cef')
# C2 = fgmopen('./','C2_CP_FGM_5VPS__20010102_055913_20010104_150531_V01.cef')
# C3 = fgmopen('./','C3_CP_FGM_5VPS__20010102_055913_20010104_150531_V01.cef')
# C4 = fgmopen('./','C4_CP_FGM_5VPS__20010102_055913_20010104_150531_V01.cef')

#%% open CEF files in this folder
C1 = fgmopen('./','C1_CP_FGM_5VPS__20010104_150531_20010107_001002_V01.cef')
# C2 = fgmopen('./','C2_CP_FGM_5VPS__20010104_150531_20010107_001002_V01.cef')
# C3 = fgmopen('./','C3_CP_FGM_5VPS__20010104_150531_20010107_001002_V01.cef')
# C4 = fgmopen('./','C4_CP_FGM_5VPS__20010104_150531_20010107_001002_V01.cef')

#%% Plot all
fgmplotParams['rangemax']=7
# fgmplot([C1,C2,C3,C4])
fgmplot(C1)

#%% plot range 2
fgmplotParams['rangemax']=2
fgmplot(C1)

#%% Custom interval
# Here, need to specify range is passed as position is not
# fgmplot(dataset,interval_start=datetime(2010,9,6),interval_end=datetime(2010,9,6,1,0,0))





