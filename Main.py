"""
# -*- coding: utf-8 -*-

@author: Shufan Wen
"""

import Process
import Plot



def run_analysis(cond, fit = True, normalize = True, multi = False, single_trial = False, save = False):
    cropped = Process_1.Process_Raw(root = 'C:\\Users\\Shufan Wen\\Desktop\\Test', loc = 'Unprocessed', dest = '')
    steps = Plot_1.plotMulti(cropped, cond, multi, single_trial, normalize, fit, save)
    return steps

if __name__ == "__main__":
    run_analysis(cond = 'FI', multi = False, fit = True, normalize = True, single_trial = False, save = True)


