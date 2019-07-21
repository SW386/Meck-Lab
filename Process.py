# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 16:39:00 2019

@author: Shufan Wen
"""
import pandas as pd;
import numpy as np;
import glob;
import os;
import re;
import shutil;
from collections import defaultdict;

class Process:
    def __init__(self, root, location, session):
        # root is the root of the processed file
        # Location is the folder of the unprocessed file
        # Destination is the folder of the final processed file
        # Session is the trial name: FI or PI or FI
        self.root = root
        self.location = location
        self.session = session
        self.subjects = defaultdict(list)
        self.identifier = defaultdict(list)
        
        for file_path in glob.glob(os.path.join(self.root, self.location, "*")):
            if os.path.isfile(file_path):
                with open(file_path) as file:
                    #Creates Identifiers For the Data File
                    file_data = file.read()
                    subject_number = re.findall(r'(?<=Subject: ).*', file_data)
                    date = re.findall(r'(?<=Start Date: ).*', file_data)
                    file_name = '_'.join([subject_number[0], self.session, date[0].replace('/', '_')])
                    self.identifier[subject_number[0]].append(date[0].replace('/','_'))
                    self.identifier[subject_number[0]].append(self.session)
                    
                    #Extracts and Processes Data
                    all_numbers = file_data.split('U:', 1)[1]
                    unprocessed_data = re.findall(r'([0-9]{1,})[\s.]', all_numbers)
                    processed_data = np.array(unprocessed_data).reshape((int((len(unprocessed_data)) / 2), 2)) 
                    self.subjects[subject_number[0]].append(processed_data)
                    
                    #Creates File Directories if Nonexistent
                    subject_path = os.path.join(self.root, 'Subjects', subject_number[0])
                    session_types = ['FI', 'PI']
                    for i in range(2):
                        if not os.path.exists(os.path.join(subject_path, 'Processed', session_types[i])):
                            os.makedirs(os.path.join(subject_path, 'Processed', session_types[i]))
                        if not os.path.exists(os.path.join(subject_path, 'Raw', session_types[i])):
                            os.makedirs(os.path.join(subject_path, 'Raw', session_types[i]))
                    
                    #Saves Processed and Unprocessed Files
                    processed_path = os.path.join(subject_path, 'Processed', self.session[:2], file_name + '.txt')
                    raw_path = os.path.join(subject_path, 'Raw', self.session[:2])
                    np.savetxt(processed_path, processed_data, fmt = '%s')
                    shutil.copy(file_path, raw_path)
                    
    def MedPC_format(self):
        #Converts the Processed Data into a DataFrame which shows the Presses and their Times 
        #during each Long and Short Intervals
        
        #Added functionality inludes sepearation of Presses to Left Lever and Right Lever
        
        formatted_data = defaultdict(list)

        for subject, data_array in self.subjects.items():
            for session in data_array:
                all_data = session.astype(int)
                current_trial = 0
                session_data = pd.DataFrame()
                for event, press in all_data[1:, :]:
                    if event in [888, 666, 555, 333] and press == 0:
                        current_trial = event #Column in DataFrame
                        right_press = [] #Seperates Left and
                        left_press = []  #Right Lever Presses
                    elif press in [2, 3]:
                        left_press.extend([event]) 
                    elif press in [5, 6]:
                        right_press.extend([event])
                    elif event in [999] and press == 0:
                        index = pd.MultiIndex.from_tuples([(current_trial , 'Left') , (current_trial , 'Right')]) #Creates MultiIndex
                        new = pd.DataFrame([left_press, right_press], index = index) #Creates new DataFrame with MultiIndex
                        new = new.T #Transpose DataFrame
                        session_data = pd.concat([session_data, new], axis = 1) #Combines 2 DataFrames
                            
        formatted_data[subject].append(session_data)
       # SessionData.to_excel('C:\\Users\\Shufan Wen\\Desktop\\Test\\pandas.xlsx')    
        return formatted_data
    

            
        

        
