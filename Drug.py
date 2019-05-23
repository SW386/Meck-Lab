'''
Created on May 21, 2019

@author: Shufan Wen
'''

import numpy as np
import random
import copy
import csv

def Trials(Animal, Drug, Dose, Injection):
    """
    Animal is an integer describing the number of animals to be tested
    Drug is a list of drug names
    Dose is a parallel list of lists containing the various concentrations of each drug to be tested
    Injection is an integer describing the number of times each Drug/Dose combination is to be injected
    
    Creates a CSV file where each row is an animal to be tested. Each animal will be treated with every 
    Drug:Dose:Injection combination though the order of injections will be randomized.
    
    Returns the CSV file in Matrix form
    """
    DoseCombinations = []
    for i in range(len(Drug)):
        for x in range(len(Dose[i])):
            DoseCombinations.append(Drug[i] + ":" + str(Dose[i][x]))
    InjectionCombinations = []
    for i in range(len(DoseCombinations)):
        for x in range(1, Injection + 1):
            InjectionCombinations.append(DoseCombinations[i] + ":" + str(x))
    Output = []
    for i in range(Animal):
        array = []
        a = copy.deepcopy(InjectionCombinations)
        for i in range(len(InjectionCombinations)):
            x = random.choice(a)
            a.remove(x)
            array.append(x)
        Output.append(array)
    
    with open('Trials.csv','w') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(Output)
    csvfile.close()
     
    return np.matrix(Output)
    


if __name__ == '__main__':
    print(Trials(10, ["A", "B", "C"], [[1,2],[1,2],[0]], 2))