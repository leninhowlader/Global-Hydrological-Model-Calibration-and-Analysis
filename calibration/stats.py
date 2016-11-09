#modified on: 13-Nov-2014
import sys
sys.path.append('..')
import numpy as np
from calibration.enums import ObjectiveFunction, DataNormalization

np.seterr(divide='ignore', invalid='ignore')

class stats:
    @staticmethod
    def compute_anomalies(data):
        try:
            data = np.array(data)
            data = data - np.mean(data)
        except: return [np.nan] * len(data)
        return list(data)

    @staticmethod
    def mean(data):

        return np.mean(data)

    @staticmethod
    def weighted_mean(data, weights):
        try:
            data, weights = np.array(data), np.array(weights)
            wsum = np.sum(weights)
            return np.sum(np.array(data) * np.array(weights))/wsum
        except: return np.nan

    @staticmethod
    def root_mean_square_error(sim, obs):
        try: return np.sqrt(np.mean((obs - sim) ** 2))
        except: return np.nan


    @staticmethod
    def coefficient_of_determination(sim, obs):
        obs_mean = np.mean(obs)
        sim_mean = np.mean(sim)

        r2 = (np.sum((obs - obs_mean)*(sim-sim_mean)))**2/(np.sum((obs-obs_mean)**2)*(np.sum((sim-sim_mean)**2)))

        return r2

    @staticmethod
    def mean_square_error(sim, obs):
        return np.mean((sim - obs) ** 2)

    @staticmethod
    def mean_absolute_percentage_error(sim, obs):
        return np.mean(abs(sim-obs)/obs)*100

    @staticmethod
    def index_of_agreement(sim, obs):
        pe = stats.potential_error(sim, obs)

        if pe != 0: return 1-(np.sum((sim-obs)**2)/pe)
        else: return None

    @staticmethod
    def nash_sutcliffe_efficiency(sim, obs):
        obs_mean = np.mean(obs)
        return 1 - (np.sum((obs-sim)**2)/np.sum((obs-obs_mean)**2))

    @staticmethod
    def mean_absolute_error(sim, obs):
        return np.mean(abs(sim-obs))

    @staticmethod
    def potential_error(sim, obs):
        obs_mean = np.mean(obs)
        return np.sum((abs(sim-obs_mean)+abs(obs-obs_mean))**2)

    @staticmethod
    def percentage_bias(sim, obs):
        return abs(np.sum(obs-sim)*100/np.sum(obs))

    @staticmethod
    def rmse_stdv_ratio(sim, obs):
        rmse = stats.root_mean_square_error(sim, obs)
        return rmse/np.std(obs)

    @staticmethod
    def objective_function(fun, sim, obs, normalize=DataNormalization.none):
        sim, obs = np.array(sim), np.array(obs)
        if normalize != DataNormalization.none and fun in [ObjectiveFunction.root_mean_square_error,
                   ObjectiveFunction.mean_absolute_error, ObjectiveFunction.mean_square_error]:
            sim, obs = stats.normalize(sim, obs, normalize)

        if fun == ObjectiveFunction.root_mean_square_error: return stats.root_mean_square_error(sim, obs)
        elif fun == ObjectiveFunction.coefficient_of_determination: return stats.coefficient_of_determination(sim, obs)
        elif fun == ObjectiveFunction.mean_absolute_percentage_error: return stats.mean_absolute_percentage_error(sim, obs)
        elif fun == ObjectiveFunction.index_of_agreement:return stats.index_of_agreement(sim, obs)
        elif fun == ObjectiveFunction.mean_absolute_error: return stats.mean_absolute_error(sim, obs)
        elif fun == ObjectiveFunction.mean_square_error: return stats.mean_square_error(sim, obs)
        elif fun == ObjectiveFunction.percentage_bias: return stats.percentage_bias(sim, obs)
        elif fun == ObjectiveFunction.ratio_of_rmse_and_obs_stdv: return  stats.rmse_stdv_ratio(sim, obs)
        elif fun == ObjectiveFunction.nash_sutcliffe_efficiency: return stats.nash_sutcliffe_efficiency(sim, obs)
        else: return np.nan

    @staticmethod
    def normalize(sim, obs, normalize=DataNormalization.none):
        if normalize != DataNormalization.none:
            nval = 0
            if normalize == DataNormalization.observed_max: nval = np.max(obs)
            else: nval = np.mean(obs)
            return sim/nval, obs/nval
        else: return sim, obs

    @staticmethod
    def year_month(year, month):
        yr_mn = []
        if len(year) == len(month):
            for i in range(len(year)):
                yr_mn.append(str(year[i]) + '-' + str(month[i]).rjust(2,'0'))
        return yr_mn

    @staticmethod
    def statistics(data, fun):
        fun = fun.lower()
        if fun == 'mean': return np.mean(data)
        elif fun == 'median': return np.median(data)
        elif fun == 'std': return np.std(data)
        elif fun == 'var': return np.var(data)
        elif fun == 'min': return np.min(data)
        elif fun == 'max': return np.max(data)
        elif fun == 'q1': return np.percentile(data, 25)
        elif fun == 'q3': return  np.percentile(data, 75)
        else: return np.nan

    @staticmethod
    def multiple_statistics(data, functions):
        results = []
        for fun in functions: results.append(stats.statistics(data, fun))
        return results