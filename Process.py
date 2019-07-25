# -*- coding: utf-8 -*-
"""
Spyder Editor

@author: Shufan Wen
"""
from __future__ import print_function
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
                    subject = re.findall(r'(?<=Subject: ).*', fdata)
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
                           os.makedirs(os.path.join(subject_path, 'Raw', session_types[i])
                                
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
                        press_t = []
                    elif press in [2, 3, 5, 6]:
                        press_t.extend([event])                   
                    elif event in [999] and press == 0:
                        trial = pd.DataFrame({curr_trial: press_t})                       
                        session_data = pd.concat([session_data, trial], axis = 1)
                        
                formatted[sub].append(session_data)     
        return formatted
    
            
            
            
            
            
            
            
            
            
            
            
            
            
