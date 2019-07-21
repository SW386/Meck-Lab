'''
Created on May 21, 2019

@author: Shufan Wen
'''

import numpy as np
import random
import copy
import csv

def trials(animal, drug, dose, injection):
    """
    animal is an integer describing the number of animals to be tested
    drug is a list of drug names
    dose is a parallel list of lists containing the various concentrations of each drug to be tested
    injection is an integer describing the number of times each Drug/Dose combination is to be injected
    
    Creates a CSV file where each row is an animal to be tested. Each animal will be treated with every 
    drug:dose:injection combination though the order of injections will be randomized.
    
    Returns the CSV file in Matrix form
    """
    dose_combinations = []
    for i in range(len(drug)):
        for x in range(len(dose[i])):
            dose_combinations.append(drug[i] + ":" + str(dose[i][x]))
    injection_combinations = []
    for i in range(len(dose_combinations)):
        for x in range(1, injection + 1):
            injection_combinations.append(dose_combinations[i] + ":" + str(x))
    output = []
    for i in range(animal):
        array = []
        a = copy.deepcopy(injection_combinations)
        for i in range(len(injection_combinations)):
            x = random.choice(a)
            a.remove(x)
            array.append(x)
        output.append(array)
    
    with open('trials.csv','w') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(output)
    csvfile.close()
     
    return np.matrix(output)
    

