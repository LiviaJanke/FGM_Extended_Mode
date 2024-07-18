# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 09:32:16 2024

@author: Livia
"""

# Importing things

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import sys

sys.path.append('C:/FGM_Extended_Mode/Lib')

from fgmfiletools import fgmsave

from datetime import datetime, timedelta

from ext_functions import get_calibrated_ext_data, closest_higher_date, packet_decoding_even, packet_decoding_odd, quickplot, quicksave, make_t, quickopen, apply_calparams, FGMEXT_to_SCS, rotate_SCS, find_cal_file, find_BS_file, packet



craft = 'C1'

Ext_entries_filepath = 'C:/FGM_Extended_Mode/Lib/' + craft + '_Ext_Entries'

ext_entries_df = pd.read_csv(Ext_entries_filepath, header = None)

ext_entries = pd.to_datetime(ext_entries_df[0])

indices = np.arange(0, len(ext_entries))

for i in indices:
    
    try:
        get_calibrated_ext_data(i, craft)

    except:
        
        pass
