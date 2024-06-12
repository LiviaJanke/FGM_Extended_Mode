# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 17:48:42 2024

@author: Livia
"""

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt


#%%


#SC_1_01_01_2002 = np.loadtxt('Spacecraft_1_10_day_01_01_2002', dtype = str)


#%%

SC_1_01_01_2002_df = pd.read_csv('Spacecraft_1_10_day_01_01_2002', skiprows = 6, on_bad_lines='warn', header = None)


#%%

df = SC_1_01_01_2002_df


#%%

df_no_nan = df.dropna(axis = 0, how = 'any')

#%%

column_0 = np.array((df_no_nan[df_no_nan.columns[0]]))

column_1 = df_no_nan[df_no_nan.columns[1]]

column_2 = df_no_nan[df_no_nan.columns[2]]

column_3 = df_no_nan[df_no_nan.columns[3]]

column_4 = df_no_nan[df_no_nan.columns[4]]

column_5 = np.array((df_no_nan[df_no_nan.columns[5]]))



#%%

plt.plot(column_0, linewidth = 0, marker = '.')
plt.show()

#%%


df_no_nan[df_no_nan.columns[0]].plot()

#%%

figure, ax1 = plt.subplots()
ax1.plot(df[df.columns[0]],df[df.columns[4]],linewidth=0.5,zorder=1, label = "Force1")
ax1.plot(df[df.columns[0]],df[df.columns[5]],linewidth=0.5,zorder=1, label = "Force2")


#%%














