# -*- coding: utf-8 -*-
"""
@author: Shufan Wen
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os.path
from scipy.optimize import curve_fit, brute
from collections import defaultdict

def hist_rast(data, bin_n):
    
    #creates histogram
    data.columns = range(len(data.columns))
    flatten = data.unstack().dropna()
    sort = flatten.sort_values()
    sort = np.array(flatten) / 100
    bin_data = np.digitize(sort, bins = range(bin_n))
    
    #creates raster
    raster = np.zeros((data.shape[1], bin_n * 100))
    
    for i in range(data.shape[1]):
        trial = data.iloc[:, i]
        presses = trial.values[~np.isnan(trial.values)]
        raster[i, :].put(np.int64(presses), 1)
    
    return [np.bincount(bin_data, minlength = bin_n + 1)], [np.where(raster)]

def single_trial_analysis(data):
   
    def func(x_var, x, y0):
        
        a, b = x_var
        
        if a < b:
            y = np.piecewise(x.astype(float), [(x < a) | (x >= b), (a <= x) & (x < b)], [0, 1])
            val = sum((y-y0)**2)
        else:
            val = 100
        return val 
    
    data = data[0]
    tpts = np.zeros((max(data[0] + 1), 2))
    rrange = (slice(0, 91, 1), slice(0, 91, 1))
    for i in range(max(data[0] + 1)):
        presses = data[1][data[0] == i]
        if presses.size:
            bins = np.digitize(presses/ 100, bins = range(90)) # puts press data into 200ms bins
            Y = np.bincount(bins, minlength = 91).astype(float)
            X = np.array(range(91)).astype(float)
            res = brute(func, rrange, args = (X, Y))
            
            #on low press trials there may be no high state. The 5 sec is arbitrary but seems to work
            if res[1] - res[0] > 5:
                tpts[i, :] = res
            else:
                tpts[i, :] = np.array([np.nan, np.nan])
                
        else:
            tpts[i, :] = np.array([np.nan, np.nan])
        
    return tpts
    
def plot(data, subject, cond = '', date = '', path = '', fit = True, normalize = True, save = False):
    
    #equation taken from Buhusi et al., 2009   
    def gauss_ramp(x, a, b, c, d):
        return a * np.exp(-(x - b)**2 / (2 * c)**2) + d * (x - b)
    
    colors = ['b', 'm']
  
    gs = plt.GridSpec(2, 2, width_ratios = [1,2])
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    ax3 = plt.subplot(gs[1, :])
    sns.despine()
    
    statistics = defaultdict(list)
    key_name = subject
        
    for i, vals in enumerate(data):
        rast, Y, x, trial = data[i]
        X = range(x + 1)
        
        if normalize:
            Y = Y / float(max(Y))
            if 'Normalized' not in subject:
                subject = subject + ' Normalized'
        
        if i == 0:
            axn = ax1
        else:
            axn = ax2
        plt.suptitle(subject)
        sns.regplot(rast[1] / 100.00, rast[0], scatter = True, marker = '|', color = colors[i], 
                    scatter_kws = {'s': 12, 'linewidth': 0.5}, fit_reg = False, ax = axn)
        ax1.set_ylabel('Trial Number')
        n = rast[0].max()
        
        if len(trial) != 0:
            y_range = np.array(range(max(rast[0] + 1)))
            sns.regplot(trial[:, 0], y_range, scatter = True, marker = 's', color = 'g', 
                        scatter_kws = {'s': 12}, fit_reg = False, ax = axn)
            sns.regplot(trial[:, 1], y_range, scatter = True, marker = 's', color = 'r', 
                        scatter_kws = {'s': 12}, fit_reg = False, ax = axn)
        
        ax3.plot(X, Y, color = colors[i], linewidth = 2)
        ax3.set_xlabel('Time (sec)')
        ax3.set_ylabel('Cumulative Presses')
        ax3.set_xlim([0, 100])
            
        if fit:
            if i == 0:
                initial = [1, 12, 12, 0]
            else:
                initial = [1, 36, 36, 0]
            popt, pcov = curve_fit(gauss_ramp, X, Y, p0 = initial)
            ax3.plot(X, gauss_ramp(X, *popt), 'k', linewidth = 0.5, 
                     label = 'fit: rate=%5.3f\n      μ=%5.3f\n      σ=%5.3f\n      tail=%5.3f' % tuple(popt))
            ax3.legend(fontsize = 9, loc = 1)
            ax3.set_xlabel('Time (sec)')
            ax3.set_ylabel('Presses (Normalized)')
            μ = popt[1]
            σ = popt[2]
        else:
            μ = 0
            σ = 0
        
        if i == 0:
            statistics[key_name + '_short'] = [n, μ, σ]
        else:
            statistics[key_name + '_long'] = [n, μ, σ]
    
    if save: 
        if not os.path.exists(os.path.join(path, 'Subjects', subject[:4], 'Graphs')):
            os.makedirs(os.path.join(path, 'Subjects', subject[:4], 'Graphs'))
        plt.savefig(os.path.join(path, 'Subjects', subject[:4], 'Graphs', date + cond + '.png')) 
    plt.show()

    return statistics 

def plotMulti(Process, cond, multi_session = True, single_trial = False, normalize = True, fit = True, save = True):
    
    Med_data = Process.MedPC_format()
    statistics = {}
    
    for k, v in Med_data.items():
        
        if multi_session:
            loops = 1
        else:
            loops = len(v)
            
        press_data = []
        plot_data = []
        
        for i in range(loops):
            
            if multi_session:
                data = pd.concat(v, axis = 1)
            else:
                data = v[i]
                
            if cond.lower() == 'fi' and k[-1] == "1":
                press_data.append(pd.concat([data[888, "Right"], data[555,"Right"]], axis = 1))
                press_data.append(data[555, "Left"])
                bins = 150
            elif cond.lower() == 'fi' and k[-1] == "2":
                press_data.append(pd.concat([data[888, "Left"], data[555,"Left"]], axis = 1))
                press_data.append(data[555, "Right"])
                bins = 150
            elif cond.lower() == 'pi' and k[-1] == "1":
                press_data.append(pd.concat([data[666, "Right"], data [333, "Right"]], axis = 1))
                press_data.append(data[333, "Left"])
                bins = 149
            elif cond.lower() == 'pi' and k[-1] == "2" :
                press_data.append(pd.concat([data[666, "Left"], data [333, "Left"]], axis = 1))
                press_data.append(data[333, "Right"])
                bins = 149
            
        
        press_names = ["Short", "Long"]
        path = Process.root
        if multi_session:
            date = Process.identifier[k][0] + '_to_' + Process.identifier[k][-2]
        else:
            date = Process.identifier[k][0]
        if not os.path.exists(os.path.join(path, 'Subjects', k, 'Bins')):
            os.makedirs(os.path.join(path, 'Subjects', k, 'Bins'))
            
        saved = pd.DataFrame()
        
        for i, val in enumerate(press_data):
            no_omit = val.dropna(axis = 'columns', thresh = 1)  # This removes omitted trials
            hist, rast = hist_rast(no_omit, bins)
            binned_data = pd.DataFrame(hist, index = [press_names[i]])
            saved = pd.concat([saved, binned_data], sort=True,)
            
            if single_trial:
                trials = single_trial_analysis(rast)
            else:
                trials = []
            plot_data.append([rast[0], hist[0], bins, trials])
            
        file_name = '_'.join([k, cond, date])
        saved.to_excel(os.path.join(path, 'Subjects', k, 'Bins', file_name + '.xlsx'))
            
        statistics[k] = plot(plot_data, k, cond, date, path, fit, normalize, save)
        
    return statistics

def plotExperiment(Experiment, cond, multi_session = True, single_trial = False, normalize = True, fit = True, save = True):
    
    Med_data = Experiment.MedPC_format()
    statistics = {}
    
    for k, v in Med_data.items():
        
        press_data = []
        plot_data = []
        
        long_trials = pd.DataFrame()
        short_trials = pd.DataFrame()
        
        for i, j in v:
            
            if cond.lower() == 'fi':
                bins = 150
                if j[-1] == '1':
                    short_trials = pd.concat([short_trials, i[888, "Right"], i[555,"Right"]], axis = 1)
                    long_trials = pd.concat([long_trials, i[555, "Left"]], axis = 1)
                if j[-1] == '2':
                    short_trials = pd.concat([short_trials, i[888, "Left"], i[555,"Left"]], axis = 1)
                    long_trials = pd.concat([long_trials, i[555, "Right"]], axis = 1)
                
            if cond.lower() == 'pi':
                bins = 149
                if j[-1] == '1':
                    short_trials = pd.concat([short_trials, i[666, "Right"], i[333, "Right"]], axis = 1)
                    long_trials = pd.concat([long_trials, i[333, "Left"]], axis = 1)
                if j[-1] == '2':
                    short_trials = pd.concat([short_trials, i[666, "Left"], i[333, "Left"]], axis = 1)
                    long_trials = pd.concat([long_trials, i[333, "Right"]], axis = 1)
                    
        press_data.extend([short_trials, long_trials])
        
        saved = pd.DataFrame()
        press_names = ["Short", "Long"]
        path = Experiment.root
        date = 'N/A'
        
        if not os.path.exists(os.path.join(path, 'Experiments', k, 'Bins')):
            os.makedirs(os.path.join(path, 'Experiments', k, 'Bins'))
            
        for i, val in enumerate(press_data):
            no_omit = val.dropna(axis = 'columns', thresh = 1)  # This removes omitted trials
            hist, rast = hist_rast(no_omit, bins)
            binned_data = pd.DataFrame(hist, index = [press_names[i]])
            saved = pd.concat([saved, binned_data], sort=True,)
            
            if single_trial:
                trials = single_trial_analysis(rast)
            else:
                trials = []
            plot_data.append([rast[0], hist[0], bins, trials])
            
        file_name = '_'.join([k, cond, date])
#        saved.to_excel(os.path.join(path, 'Experiments', k, 'Bins', file_name + '.xlsx'))
        statistics[k] = plot(plot_data, k, cond, date, path, fit, normalize, save)
        
    return statistics
                
                
            
            
            
            
            
            
            
            
            
            
            
            
            