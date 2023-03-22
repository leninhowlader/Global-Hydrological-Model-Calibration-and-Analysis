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
    kling_gupta_efficiency = 9
    scaled_kling_gupta_efficiency = 10
    pearson_correlation_coefficient = 11
    KGE_alpha = 12
    KGE_beta = 13
    KGE_dAlpha = 14
    KGE_dBeta = 15
    NSE_observation_uncertainty = 16

    @staticmethod
    def find_function(func):
        func = func.lower().replace('_', ' ')
        while func.find(' ') >= 0: func = func.replace('  ', ' ')

        if func in ['mean square error', 'mse']: 
            return ObjectiveFunction.mean_square_error
        elif func in ['root mean square error', 'rmse']: 
            return ObjectiveFunction.root_mean_square_error
        elif func in ['coefficient of determination', 'r2']: 
            return ObjectiveFunction.coefficient_of_determination
        elif func in ['mean absolute percentage error', 'mape']:
            return ObjectiveFunction.mean_absolute_percentage_error
        elif func in ['index of agreement', 'ioa']: 
            return ObjectiveFunction.index_of_agreement
        elif func in ['mean absolute error', 'mae']: 
            return ObjectiveFunction.mean_absolute_error
        elif func in ['percentage error', 'percentage bias', 'pb', 'pbias']: 
            return ObjectiveFunction.percentage_bias
        elif func in ['rmse-obs. std. dev. ratio', 'rmse-observed std. dev. ratio', 'rsr']: 
            return ObjectiveFunction.ratio_of_rmse_and_obs_stdv
        elif func in ['nash-sutcliffe efficiency', 'nash sutcliffe efficiency', 'nse']: 
            return ObjectiveFunction.nash_sutcliffe_efficiency
        elif func in ['nse-ou', 'nse_ou', 'nse_ou', 'nse observation uncertainty']:
            return ObjectiveFunction.NSE_observation_uncertainty
        elif func in ['kling-gupta efficiency', 'kling gupta efficiency', 'kling_gupta_efficiency', 'kge']: 
            return  ObjectiveFunction.kling_gupta_efficiency
        elif func in ['scaled kling-gupta efficiency', 'scaled kling gupta efficiency', 'scaled_kling_gupta_efficiency', 'skge', 'kges', 'kge-scaled', 'kge_scaled']:
            return ObjectiveFunction.scaled_kling_gupta_efficiency
        elif func in ['correlation coefficient', 'correlation_coefficient', 'pearson correlation coefficient', 'pearson_correlation_coefficient', 'r']:
            return ObjectiveFunction.pearson_correlation_coefficient
        elif func in ['kge-alpha', 'kge_alpha', 'kge alpha', 'alpha']: 
            return ObjectiveFunction.KGE_alpha
        elif func in ['kge-beta', 'kge_beta', 'kge beta', 'beta']: 
            return ObjectiveFunction.KGE_beta
        elif func in ['kge-dalpha', 'kge_dalpha', 'kge dalpha', 'dalpha']: 
            return ObjectiveFunction.KGE_dAlpha
        elif func in ['kge-dbeta', 'kge_dbeta', 'kge dbeta', 'dbeta']: 
            return ObjectiveFunction.KGE_dBeta
        else: return ObjectiveFunction.not_specified

    @staticmethod
    def get_function_name(func):
        if func == ObjectiveFunction.mean_square_error: return 'mse'
        elif func == ObjectiveFunction.root_mean_square_error: return 'rmse'
        elif func == ObjectiveFunction.coefficient_of_determination: return 'r2'
        elif func == ObjectiveFunction.mean_absolute_percentage_error: return 'mape'
        elif func == ObjectiveFunction.index_of_agreement: return 'ioa'
        elif func == ObjectiveFunction.mean_absolute_error: return 'mae'
        elif func == ObjectiveFunction.percentage_bias: return 'pbias'
        elif func == ObjectiveFunction.ratio_of_rmse_and_obs_stdv: return 'rsr'
        elif func == ObjectiveFunction.nash_sutcliffe_efficiency: return 'nse'
        elif func == ObjectiveFunction.kling_gupta_efficiency: return 'kge'
        elif func == ObjectiveFunction.scaled_kling_gupta_efficiency: return 'skge'
        elif func == ObjectiveFunction.pearson_correlation_coefficient: return 'r'
        elif func == ObjectiveFunction.KGE_alpha: return 'kge-alpha'
        elif func == ObjectiveFunction.KGE_beta: return 'kge-beta'
        elif func == ObjectiveFunction.KGE_dAlpha: return 'kge-dAlpha'
        elif func == ObjectiveFunction.KGE_dBeta: return 'kge-dBeta'
        elif func == ObjectiveFunction.NSE_observation_uncertainty: return 'nse-ou'
        else: return 'n/a'

class DataNormalization(Enum):
    none = 0
    observed_max = 1
    observed_mean = 2

