try: from enum import Enum
except:
    class Enum(): pass

class FileType(Enum):
    flat = 0
    binary = 1
    wghm_binary = 2

class FileEndian(Enum):
    little_endian = 0
    big_endian = 1

class PredictionType(Enum):
    daily = 0
    monthly = 1
    yearly = 2

class SortAlgorithm(Enum):
    bubble_sort = 0
    heap_sort = 1

class CompareResult(Enum):
    smaller = -1
    equal = 0
    larger = 1
    incompatible = -9999

class ObjectiveFunction(Enum):
    not_specified = -1
    mean_square_error = 0
    root_mean_square_error = 1
    coefficient_of_determination = 2
    mean_absolute_percentage_error = 3
    index_of_agreement = 4
    mean_absolute_error = 5
    percentage_bias = 6
    ratio_of_rmse_and_obs_stdv = 7
    nash_sutcliffe_efficiency = 8

    @staticmethod
    def find_function(func):
        func = func.lower().replace('_', ' ')
        while func.find(' ') >= 0: func = func.replace('  ', ' ')

        if func in ['mean square error', 'mse']: return ObjectiveFunction.mean_square_error
        elif func in ['root mean square error', 'rmse']: return ObjectiveFunction.root_mean_square_error
        elif func in ['coefficient of determination', 'r2']: return ObjectiveFunction.coefficient_of_determination
        elif func in ['mean absolute percentage error', 'mape']: return ObjectiveFunction.mean_absolute_percentage_error
        elif func in ['index of agreement', 'ioa']: return ObjectiveFunction.index_of_agreement
        elif func in ['mean absolute error', 'mae']: return ObjectiveFunction.mean_absolute_error
        elif func in ['percentage error', 'percentage bias', 'pb', 'pbias']: return ObjectiveFunction.percentage_bias
        elif func in ['rmse-obs. std. dev. ratio', 'rmse-observed std. dev. ratio', 'rsr']: return ObjectiveFunction.ratio_of_rmse_and_obs_stdv
        elif func in ['nash-sutcliffe efficiency', 'nash sutcliffe efficiency', 'nse']: return ObjectiveFunction.nash_sutcliffe_efficiency
        else: return ObjectiveFunction.not_specified

class DataNormalization(Enum):
    none = 0
    observed_max = 1
    observed_mean = 2

