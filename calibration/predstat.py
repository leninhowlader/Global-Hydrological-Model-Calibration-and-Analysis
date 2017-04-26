
import sys, numpy as np
sys.path.append('..')
from calibration.variable import DataCloud
from calibration.stats import stats

class PredictionStatistics(stats):
    @staticmethod
    def test():
        print('Hi from PredictionStatistics Class!!')