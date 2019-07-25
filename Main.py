"""
# -*- coding: utf-8 -*-

@author: Shufan Wen
"""

import Process
import Plot

def run_analysis(cond, fit = True, normalize = True, multi = False, single_trial = False, save = False):
    """
    cond is the session type, PI or FI
    fit is whether the data should be fit to a guassian curve
    normalize is whether the data should be divided by the max value
    multi is whether 1 trial should be graphed or many
    single_trial indicates if the start and stop instances of high press volume should be identified
    save indicates whether the plot of the data should be saved or not
    """
    
    cropped = Process.Process_Raw(root = 'C:\\Users\\Shufan Wen\\Desktop\\Test', loc = 'Unprocessed', dest = '')
    Plot.plotMulti(cropped, cond, multi, single_trial, normalize, fit, save)
    return 

if __name__ == "__main__":
    run_analysis(cond = 'FI', multi = False, fit = True, normalize = True, single_trial = False, save = True)


