"""
# -*- coding: utf-8 -*-

@author: Shufan Wen
"""

import Process
import Plot
import numpy as np
from scipy import stats

def run_analysis(cond, fit = True, normalize = True, multi = False, 
                 single_trial = False, save = False, run_statistics = False):
    """
    cond is the session type, PI or FI
    fit is whether the data should be fit to a guassian curve
    normalize is whether the data should be divided by the max value
    multi is whether 1 trial should be graphed or many
    single_trial indicates if the start and stop instances of high press volume should be identified
    save indicates whether the plot of the data should be saved or not
    run_statistics is whether you want to run a one way anova on the trials or not
    """
    
    cropped = Process.Process_Raw(root = 'C:\\Users\\Shufan Wen\\Desktop\\Test', loc = 'Unprocessed', dest = '')
    statistics = Plot.plotMulti(cropped, cond, multi, single_trial, normalize, fit, save)
    if run_statistics:
        p_value_s, p_value_l = one_way_anova(statistics)
        return p_value_s, p_value_l

def one_way_anova(statistics):
    df_between = len(statistics) - 1
    df_within_s = 0
    df_within_l = 0
    grand_m_s = 0
    grand_m_l = 0
    mean_s = []
    mean_l = []
    var_within_s = 0
    var_within_l = 0
    for k,v in statistics.items():
        for name_trial, num in v.items():
            if name_trial[-5:] == 'short':
                df_within_s += (num[0] - 1)
                grand_m_s +=  num[1]/(len(statistics))
                mean_s.append(num[1])
                var_within_s += (num[2])**2/(len(statistics))
            if name_trial[-4:] == 'long':
                df_within_l += (num[0] - 1)
                grand_m_l += num[1]/len(statistics)
                mean_l.append(num[1])
                var_within_l += (num[2])**2/len(statistics)
    var_m_s = sum((np.array(mean_s) - grand_m_s)**2)/df_between
    var_m_l = sum((np.array(mean_l) - grand_m_l)**2)/df_between
    var_between_s = var_m_s*(df_within_s + len(statistics))/len(statistics)
    var_between_l = var_m_l*(df_within_l + len(statistics))/len(statistics)
    f_value_s = var_between_s/var_within_s
    f_value_l = var_between_l/var_within_l
    p_value_s = stats.f.sf(f_value_s, df_between, df_within_s)
    p_value_l = stats.f.sf(f_value_l, df_between, df_within_l)
    return p_value_s, p_value_l        

if __name__ == "__main__":
    run_analysis(cond = 'FI', multi = True, fit = True, normalize = True, single_trial = False, save = True)


