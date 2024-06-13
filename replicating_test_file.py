# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 12:07:30 2024

@author: Livia
"""

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt


#%%

df_test_file = pd.read_csv('C1_020227_ext.txt', header = None)

df_test_file_with_names = pd.read_csv('C1_020227_ext.txt', names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'])

test_df = df_test_file_with_names
#%%

df_L_TO_R = pd.read_csv('C1_020227_ext_L_TO_R.txt',  names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'],  on_bad_lines='warn')

df_R_TO_L = pd.read_csv('C1_020227_ext_R_TO_l.txt',  names = ['count', 'reset_vector', 'resolution', 'x', 'y', 'z'],  on_bad_lines='warn')

#%%


df_L_TO_R_no_headers = df_L_TO_R.dropna(axis = 0, how = 'any')

#%%

# assigning uncleaned data file to 'df' for simplicity

# need to change this later maybe

df = df_L_TO_R_no_headers



count_444 = df['count'][449]

count_bef = df['count'][456]


# could try re-indexing df to simplify?


df.reset_index(inplace = True)

#this keeps the old index as a second 'index' column

#%%

for i in np.arange(0, len(df['count'])):
    
    try:    
        
        count_val = float(df['count'][456])
        
        df.replace(to_replace = df['count'][456], value = count_val)
        
    except ValueError:
        
        count_val = 445


























