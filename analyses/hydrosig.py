# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 12:31:19 2020

@author: mhasan
"""

import numpy as np

class Signature:
    @staticmethod  
    def annual_mean(d): return np.mean(d, axis=1)
    
    @staticmethod
    def mean_annual_value(d): return np.mean(d, axis=1).mean()
    
    @staticmethod
    def mean_span_above_threshold(d, threshold=-9999):
        if threshold==-9999: threshold = np.mean(d)
        
        x = np.zeros(d.shape)
        
        ii = np.where(d > threshold)
        x[ii] = 1
        
        return np.sum(x, axis=1).mean()
    
    @staticmethod
    def slopes(d, threshold):
        peaks_at = np.argmax(d, axis=1)
        
        ii = np.argwhere(d > threshold)
        left_at, right_at = [], []
        
        jj = np.arange(len(d))
        for j in jj:
            kk = np.where(ii[:, 0]==j)
            left_at.append(ii[kk][:,1].min())
            right_at.append(ii[kk][:, 1].max())
        
        upslopes = (d[jj, peaks_at] - d[jj, left_at])/(peaks_at - left_at + 1)
        downslopes = (d[jj, right_at] - d[jj, peaks_at])/(right_at - peaks_at + 1)
        
        return upslopes, downslopes
    
    @staticmethod
    def mean_slopes(d, threshold):
        upslopes, downslopes = Signature.slopes(d, threshold)
        return upslopes.mean(), downslopes.mean()
    
    # detect peaks
    @staticmethod
    def annual_peaks(d): return np.max(d, axis=1)
    
    @staticmethod
    def mean_peak(d): return np.max(d, axis=1).mean()
    
    @staticmethod
    def peak_locations(d): return np.argmax(d, axis=1) + 1
    
    @staticmethod
    def peak_location_median(d): ii = np.argmax(d, axis=1) + 1; return np.median(ii)
    
    @staticmethod
    def peak_location_mean(d): ii = np.argmax(d, axis=1) + 1; return np.mean(ii)
    
    @staticmethod
    def spread_of_peak_locations(d): ii = np.argmax(d, axis=1); return max(ii) - min(ii) + 1
    
    @staticmethod
    def annual_bottoms(d): return np.min(d, axis=1)
    
    @staticmethod
    def mean_bottom(d): return np.min(d, axis=1).mean()
    
    @staticmethod
    def bottom_locations(d): return np.argmin(d, axis=1) + 1
    
    @staticmethod
    def bottom_location_median(d): ii = np.argmin(d, axis=1) + 1; return np.median(ii)
    
    @staticmethod
    def bottom_location_mean(d): ii = np.argmin(d, axis=1) + 1; return np.mean(ii)
    
    @staticmethod
    def spread_of_bottom_locations(d): ii = np.argmin(d, axis=1); return max(ii) - min(ii) + 1
    
    @staticmethod
    def annaul_amplitudes(d): return np.max(d, axis=1) - np.min(d, axis=1)
    
    @staticmethod
    def mean_annual_amplitude(d): return (np.max(d, axis=1) - np.min(d, axis=1)).mean()
    
    @staticmethod
    def monthly_means(d): return np.mean(d, axis=0)
    
    @staticmethod
    def cv(d): return np.std(d) / np.mean(d)