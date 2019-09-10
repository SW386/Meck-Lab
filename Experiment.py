# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 09:11:39 2019

@author: Shufan Wen
"""
import numpy as np
import pandas as pd
import os
import glob
import re
import shutil
from collections import defaultdict

class Process_Raw:
    def __init__(self, root, loc, dest):
        self.root = root
        self.path = dest
        self.subjects = defaultdict(list)
        self.identifier = defaultdict(list)

        for fpath in glob.glob(os.path.join(self.root, loc, '*')):
            if os.path.isfile(fpath) and fpath[-3:] != 'csv':
                with open(fpath) as f:
                    fdata = f.read()
                    subject = re.findall(r'(?<=Experiment: ).*', fdata)
                    date  = re.findall(r'(?<=Start Date: ).*', fdata)
                    cond = re.findall(r'PI|FI', fdata)
                    meta = '_'.join([subject[0], cond[0], date[0].replace('/', '_')])
                    data = re.findall(r'([0-9]{1,})[\s.]', fdata.split('U:', 1)[1])
                    data = np.array(data).reshape((int((len(data)) / 2), 2))     
                self.identifier[subject[0]].append(date[0].replace('/','_'))
                self.subjects[subject[0]].append(data)
                
                subject_path = os.path.join(self.root, 'Subjects', subject[0])
                session_types = ['FI', 'PI']
                for i in range(2):
                    if not os.path.exists(os.path.join(subject_path, 'Processed', session_types[i])):
                           os.makedirs(os.path.join(subject_path, 'Processed', session_types[i]))
                    if not os.path.exists(os.path.join(subject_path, 'Raw', session_types[i])):
                           os.makedirs(os.path.join(subject_path, 'Raw', session_types[i]))
                           
                processed_path = os.path.join(subject_path, 'Processed', cond[0], meta + '.txt')
                raw_path = os.path.join(subject_path, 'Raw', cond[0])
                np.savetxt(processed_path, data, fmt = '%s')
                shutil.copy(fpath, raw_path)       
            
    def MedPC_format(self):

        formatted = defaultdict(list)

        for sub, data in self.subjects.items():
            for session in data:
                all_data = session.astype(int)
                session_data = pd.DataFrame()
                curr_trial = 0               
                for event, press in all_data[1:, :]:
                    if event in [888, 666, 555, 333] and press == 0:
                        curr_trial = event
                        right_press = []
                        left_press = []
                    elif press in [2, 3]:
                        left_press.extend([event])     
                    elif press in [5, 6]:
                        right_press.extend([event])
                    elif event in [999] and press == 0:
                        index = pd.MultiIndex.from_tuples([(curr_trial , 'Left') , (curr_trial , 'Right')]) #Creates MultiIndex
                        new = pd.DataFrame([left_press, right_press], index = index) #Creates new DataFrame with MultiIndex
                        new = new.T #Transpose DataFrame
                        session_data = pd.concat([session_data, new], axis = 1) #Combines 2 DataFrames
                        
                formatted[sub].append(session_data)     
        return formatted
