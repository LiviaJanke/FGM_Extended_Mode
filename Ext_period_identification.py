# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 19:10:13 2024

@author: Livia
"""


# Importing things

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import datetime

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


filebase = 'C:/FGM_Extended_Mode/SCCH_strings'

craft = 'C1'


filepath = filebase +'/' + craft + '/'

df_with_pos = pd.read_csv(filepath,usecols = range(5), delimiter = ' ', names = [])



#%%




























