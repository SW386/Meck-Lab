# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 16:39:00 2019

@author: Shufan Wen

Contains the class Process- 
Functionality:
   Init
   1) Upload the MPC files to a folder (given by Root and Location)
   2) Set the Session type
   3) Extracts the subject rat and date of session creating a dictionary for identifiers
   4) Creates the directories for the processed and unprocessed Files
   5) Extracts the press data and exports the processed data as a NumPy array
   6) Saves the processed and unprocessed files
   7) Creates a dictionary with the subjects rats and processed arrays to be used in Plot.py
   MedPC_Format
   1) Takes the NP array and converts it into a dataframe
   2) The dataframe contains a MultiIndex based on presses and trials
   
"""
import pandas as pd;
import numpy as np;
import glob;
import os;
import re;
import shutil;
from collections import defaultdict;

class Process:
    def __init__(self, Root, Location, Session):
        # Root is the root of the folder containing Location
        # Location is the name of the folder containg the unprocessed files
        # Destination is the folder of the final processed file
        # Session is the trial name: FI or PI or FI
        self.Root = Root
        self.Location = Location
        self.Session = Session
        self.Subjects = defaultdict(list)
        self.Identifier = defaultdict(list)
        
        for FilePath in glob.glob(os.path.join(self.Root, self.Location, "*")):
            if os.path.isfile(FilePath):
                with open(FilePath) as File:
                    #Creates Identifiers For the Data File
                    FileData = File.read()
                    SubjectNumber = re.findall(r'(?<=Subject: ).*', FileData)
                    Date = re.findall(r'(?<=Start Date: ).*', FileData)
                    FileName = '_'.join([SubjectNumber[0], self.Session, Date[0].replace('/', '_')])
                    self.Identifier[SubjectNumber[0]].append(Date[0].replace('/','_'))
                    self.Identifier[SubjectNumber[0]].append(Session)
                    
                    #Extracts and Processes Data
                    AllNumbers = FileData.split('U:', 1)[1]
                    UnprocessedData = re.findall(r'([0-9]{1,})[\s.]', AllNumbers)
                    ProcessedData = np.array(UnprocessedData).reshape((int((len(UnprocessedData)) / 2), 2)) 
                    self.Subjects[SubjectNumber[0]].append(ProcessedData)
                    
                    #Creates File Directories if Nonexistent
                    SubjectPath = os.path.join(self.Root, 'Subjects', SubjectNumber[0])
                    SessionTypes = ['FI', 'PI']
                    for i in range(2):
                        if not os.path.exists(os.path.join(SubjectPath, 'Processed', SessionTypes[i])):
                            os.makedirs(os.path.join(SubjectPath, 'Processed', SessionTypes[i]))
                        if not os.path.exists(os.path.join(SubjectPath, 'Raw', SessionTypes[i])):
                            os.makedirs(os.path.join(SubjectPath, 'Raw', SessionTypes[i]))
                    
                    #Saves Processed and Unprocessed Files
                    ProcessedPath = os.path.join(SubjectPath, 'Processed', self.Session[:2], FileName + '.txt')
                    RawPath = os.path.join(SubjectPath, 'Raw', self.Session[:2])
                    np.savetxt(ProcessedPath, ProcessedData, fmt = '%s')
                    shutil.copy(FilePath, RawPath)
                    
    def MedPC_format(self):
        #Converts the Processed Data into a DataFrame which shows the Presses and their Times 
        #during each Long and Short Intervals
        
        #Added functionality inludes sepearation of Presses to Left Lever and Right Lever
        
        FormattedData = defaultdict(list)

        for Subject, DataArray in self.Subjects.items():
            for Session in DataArray:
                AllData = Session.astype(int)
                CurrentTrial = 0
                SessionData = pd.DataFrame()
                for Event, Press in AllData[1:, :]:
                    if Event in [888, 666, 555, 333] and Press == 0:
                        CurrentTrial = Event #Column in DataFrame
                        RightPressTime = [] #Seperates Left and
                        LeftPressTime = []  #Right Lever Presses
                    elif Press in [2, 3]:
                        LeftPressTime.extend([Event]) 
                    elif Press in [5, 6]:
                        RightPressTime.extend([Event])
                    elif Event in [999] and Press == 0:
                        index = pd.MultiIndex.from_tuples([(CurrentTrial , 'Left') , (CurrentTrial , 'Right')]) #Creates MultiIndex
                        New = pd.DataFrame([LeftPressTime, RightPressTime], index = index) #Creates new DataFrame with MultiIndex
                        New = New.T #Transpose DataFrame
                        SessionData = pd.concat([SessionData, New], axis = 1) #Combines 2 DataFrames
                            
        FormattedData[Subject].append(SessionData)   
        return FormattedData
    

            
        
        
        
