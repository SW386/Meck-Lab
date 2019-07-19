# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:47:11 2019

@author: Shufan Wen

Currently a Work in Progress!

Contains the fuction Clean
    1) Uses the Process Class
    2) Seperates the Dataframe created by MedPC_format() depending on short/long events and left/right lever presses
    3) Creates 2 or 4 Dataframes to be graphed depending on session type (FI,PI,FI2)
    4) Dataframes use the histogram function
"""

import os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, brute

import Process


def histogram(Data, BinSize):
    # DataFile is a dataframe
    # BinSize the number of Bins
    Data.columns = range(len(Data.columns))
    Flatten = Data.unstack().dropna()
    Sort = Flatten.sort_values()
    Sort = np.array(Flatten / 100)
    BinData = np.digitize(Sort, bins = range(BinSize))

def clean(Process, Condition, Multi = False):
    
    MedPC = Process.MedPC_format()
    
    for k, v in MedPC.items():
        if Multi:
            Loops = 1
        else:
            #If there are multiple loops, it will loop through each row of the DataFrame
            Loops = len(v)
        Press = [] 
        for i in range (Loops):
            if Multi :
                Data = pd.concat(v, axis = 1)
            else :
                Data = v[i]
                
            if Condition == 'FI':
                #The List will Contain 2 Dataframes
                Press.append(Data[888, 'Right'])
                Press.append(Data[555, 'Left'])
                BinSize = 150
                
            elif Condition == 'FI2':
                #The List will Contain 4 Dataframes
                Press.append(Data[888, 'Right'])
                Press.append(Data[888, 'Left'])
                Press.append(Data[555, 'Right'])
                Press.append(Data[555, 'Left'])
                BinSize = 150
                
            elif Condition == 'PI' :
                #The List will Contain 4 Dataframes
                Press.append(Data[666, 'Right'])
                Press.append(Data[666, 'Left'])
                Press.append(Data[333, 'Right'])
                Press.append(Data[333, 'Left'])
                BinSize = 149
                
        print(Press)
                
        
        #Following Creates the Diretory and Parts of the Binned Trial names
        Dict = {'FI': ['888R', '555L'], 'FI2': ['888R', '888L', '555R', '555L'], 
                'PI' : ['666R', '666L', '333R', '333L']}
        Path = Process.Root
        if Multi:
            Date = Process.Identifier[k][0] + "-" + Process.Identifier[k][-2]
        Date = Process.Identifier[k][0]
        if not os.path.exists(os.path.join(Path, 'Subjects', k, 'Bins')):
            os.makedirs(os.path.join(Path, 'Subjects', k, 'Bins'))
        
        #Following saves the Binned Data and Graphs
        for i in range(len(Press)):
            Omit = Press[i].dropna(axis = 'columns', thresh = 1)
            Filename = '_'.join([k, Condition, str(Dict[Condition][i]), Date])
            Omit.to_excel(os.path.join(Path, 'Subjects', k, 'Bins', Filename + '.xlsx'))
                
        return (histogram(Omit, BinSize))

            
        
        
        
        
    
    
    

if __name__ == "__main__":
    Cropped = Process.Process(Root = 'C:\\Users\\Shufan Wen\\Desktop\\Test', Location = 'Unprocessed', Trial = 'FI')
    print(clean(Cropped, "FI"))
    
    
