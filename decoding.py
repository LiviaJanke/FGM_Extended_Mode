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

df = pd.read_csv('C:\FGM_Extended_Mode\BS_data_files\C1_010421_B_BS.txt', delimiter = ' ', names = [1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19])

df[2]=df[1].str.slice(start=2, stop = 4)

df[3]=df[1].str.slice(start=4)

df[1]=df[1].str.slice(stop=2)

#%%


cols = np.arange(1,20)

df = df[cols]

df.index = df.index + 1


#%%

# Decoding as Even

# 34 bytes for FGM Science Header
# 49 bytes including the DDS Header


# 49-3610 BS Science Data (3562 bytes)
# A full byte (octet) is represented by two hexadecimal digits (00–FF)










