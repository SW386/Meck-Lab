# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:47:11 2019

@author: Shufan Wen
"""

import os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, brute

import Process


def histogram(data, bin_size):
    # DataFile is a dataframe
    # BinSize the number of Bins
    data.columns = range(len(data.columns))
    Flatten = data.unstack().dropna()
    Sort = Flatten.sort_values()
    Sort = np.array(Flatten / 100)
    bin_data = np.digitize(Sort, bins = range(bin_size))

def clean(Process, session, multi = True):
    
    Med_PC = Process.MedPC_format()
    
    for k, v in Med_PC.items():
        if multi:
            loops = 1
        else:
            #If there are multiple loops, it will loop through each Dataframe in the list v
            loops = len(v)
        press = [] 
        for i in range (loops):
            if multi :
                data = pd.concat(v, axis = 1)
            else :
                data = v[i]
                
            if session == 'FI':
                #The List will Contain 2 Dataframes
                press.append(data[888, 'Right'])
                press.append(data[555, 'Left'])
                bin_size = 150
                
            elif session == 'FI2':
                #The List will Contain 4 Dataframes
                press.append(data[888, 'Right'])
                press.append(data[888, 'Left'])
                press.append(data[555, 'Right'])
                press.append(data[555, 'Left'])
                bin_size = 150
                
            elif session == 'PI' :
                #The List will Contain 4 Dataframes
                press.append(data[666, 'Right'])
                press.append(data[666, 'Left'])
                press.append(data[333, 'Right'])
                press.append(data[333, 'Left'])
                bin_size = 149
                
        #Following Creates the Diretory and Parts of the Binned Trial names
        press_names = {'FI': ['888R', '555L'], 'FI2': ['888R', '888L', '555R', '555L'], 
                'PI' : ['666R', '666L', '333R', '333L']}
        path = Process.root
        if multi:
            date = Process.identifier[k][0] + "-" + Process.identifier[k][-2]
        date = Process.identifier[k][0]
        if not os.path.exists(os.path.join(path, 'Subjects', k, 'Bins')):
            os.makedirs(os.path.join(path, 'Subjects', k, 'Bins'))
        
        #Following saves the Binned Data and Graphs
        for i in range(len(press)):
            omit = press[i].dropna(axis = 'columns', thresh = 1)
            file_name = '_'.join([k, session, str(press_names[session][i]), date])
            omit.to_excel(os.path.join(path, 'Subjects', k, 'Bins', file_name + '.xlsx'))
                
        return (histogram(omit, bin_size))

            
        
        
        
        
    
    
    


