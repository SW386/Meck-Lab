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
    def __init__(self, Root, Location, Trial):
        # Root is the root location of the processed file
        # Location is the location of the unprocessed file
        # Destination is the folder of the final processed file
        # Trial is the trial name: FI or PI or FI
        self.Root = Root
        self.Location = Location
        self.Trial = Trial
        self.Subjects = defaultdict(list)
        self.Identifier = defaultdict(list)
        
        for FilePath in glob.glob(os.path.join(self.Root, self.Location, "*")):
            if os.path.isfile(FilePath):
                with open(FilePath) as File:
                    #Creates Identifiers For the Data File
                    FileData = File.read()
                    SubjectNumber = re.findall(r'(?<=Subject: ).*', FileData)
                    Date = re.findall(r'(?<=Start Date: ).*', FileData)
                    FileName = '_'.join([SubjectNumber[0], self.Trial, Date[0].replace('/', '_')])
                    self.Identifier[SubjectNumber[0]].append(Date[0].replace('/','_'))
                    self.Identifier[SubjectNumber[0]].append(Trial)
                    
                    #Extracts and Processes Data
                    AllNumbers = FileData.split('U:', 1)[1]
                    UnprocessedData = re.findall(r'([0-9]{1,})[\s.]', AllNumbers)
                    ProcessedData = np.array(UnprocessedData).reshape((int((len(UnprocessedData)) / 2), 2)) 
                    self.Subjects[SubjectNumber[0]].append(ProcessedData)
                    
                    #Creates File Directories if Nonexistent
                    SubjectPath = os.path.join(self.Root, 'Subjects', SubjectNumber[0])
                    TrialTypes = ['FI', 'PI']
                    for i in range(2):
                        if not os.path.exists(os.path.join(SubjectPath, 'Processed', TrialTypes[i])):
                            os.makedirs(os.path.join(SubjectPath, 'Processed', TrialTypes[i]))
                        if not os.path.exists(os.path.join(SubjectPath, 'Raw', TrialTypes[i])):
                            os.makedirs(os.path.join(SubjectPath, 'Raw', TrialTypes[i]))
                    
                    #Saves Processed and Unprocessed Files
                    ProcessedPath = os.path.join(SubjectPath, 'Processed', self.Trial[:2], FileName + '.txt')
                    RawPath = os.path.join(SubjectPath, 'Raw', self.Trial[:2])
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
       # SessionData.to_excel('C:\\Users\\Shufan Wen\\Desktop\\Test\\pandas.xlsx')    
        return FormattedData
    

            
        
if __name__ == "__main__":
    cropped = Process(Root = 'C:\\Users\\Shufan Wen\\Desktop\\Test', Location = 'Unprocessed', Trial = 'FI')
    cropped.MedPC_format()
        
        