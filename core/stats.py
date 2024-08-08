#modified on: 13-Nov-2014
import numpy as np
from utilities.enums import ObjectiveFunction, DataNormalization

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
    def sum_squared_error(sim, obs): return np.sum((obs-sim)**2)

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
    def nse_observation_uncertainty_II(sim, obs, lb, ub):
        err_var = 0
        ii, jj = (sim < lb), (sim > ub)
        err_var += np.sum((lb[ii]-sim[ii])**2)  
        err_var += np.sum((sim[jj]-ub[jj])**2)
        
        obs_var = np.sum((obs-obs.mean())**2)

        return 1 - err_var / obs_var
    
    @staticmethod
    def nse_observation_uncertainty(sim, obs, lb, ub):
        err = np.abs(obs-sim)
        
        # Initialize penalty,  p with ones
        p = np.ones_like(sim)

        ii = (lb < sim) & (sim <= obs)
        p[ii] = err[ii] / (obs[ii]-lb[ii])

        ii =  (obs <= sim) & (sim < ub)
        p[ii] = err[ii]/(ub[ii]-obs[ii])

        # Mean of observed values
        mu_obs = obs.mean()

        nse_ou = 1 - (np.sum((p * err)**2) / np.sum((obs-mu_obs)**2))

        return nse_ou

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
    def pearson_correlation_coefficient(sim, obs):
        sim_mean, obs_mean = np.mean(sim), np.mean(obs)
        cov = np.sum((sim-sim_mean)*(obs-obs_mean))
        ss_sim = np.sum((sim-sim_mean)**2)
        ss_obs = np.sum((obs-obs_mean)**2)

        return cov/(np.sqrt(ss_sim)*np.sqrt(ss_obs))

    @staticmethod
    def KGE_alpha(sim, obs): return np.std(sim)/np.std(obs)

    @staticmethod
    def KGE_dAlpha(sim, obs): return abs(np.std(sim) - np.std(obs))

    @staticmethod
    def KGE_beta(sim, obs):
        mu_sim = np.mean(sim)
        mu_obs = np.mean(obs)

        if round(mu_sim, 8) == 0:
            if round(mu_obs, 8) == 0: return 1
            else: return np.inf

        return np.mean(sim)/np.mean(obs)

    @staticmethod
    def KGE_dBeta(sim, obs): return abs(np.mean(sim)-np.mean(obs))

    @staticmethod
    def KGE_gamma(sim, obs):
        mu_sim = np.mean(sim)
        mu_obs = np.mean(obs)

        if round(mu_sim, 8) == 0 or round(mu_obs, 8) == 0: return np.inf

        cv_sim = np.std(sim) / mu_sim
        cv_obs = np.std(obs) / mu_obs

        return cv_sim/cv_obs

    @staticmethod
    def kling_gupta_efficiency_2009(sim, obs):
        # Reference: Gupta et al., 2009
        sim_mean, obs_mean = np.mean(sim), np.mean(obs)
        sim_stdv, obs_stdv = np.std(sim), np.std(obs)

        r = stats.pearson_correlation_coefficient(sim, obs)

        if round(obs_stdv, 8) > 0.0: alpha = sim_stdv/obs_stdv
        else: alpha = 1.0

        if round(obs_mean, 8) > 0.0: beta = sim_mean/obs_mean
        else: beta = 1.0

        return 1- np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2)

    @staticmethod
    def kling_gupta_efficiency(sim, obs):
        # Reference: Kling et al., 2012
        mean_sim, mean_obs = np.mean(sim), np.mean(obs)
        stdv_sim, stdv_obs = np.std(sim), np.std(obs)

        if round(stdv_obs, 8) == 0.0: return np.nan

        r = stats.pearson_correlation_coefficient(sim, obs)

        if round(mean_obs, 8) == 0.0:
            # with observed mean equals 0.0, the kling-gupta equation turns into
            # kge2009 (Gupta et al., 2009)

            alpha = stdv_sim / stdv_obs

            # beta is removed from the equation considering it would equal to 1.0
            # i.e.,
            # beta = 1.0
            # kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
            # which is equivalent to
            # kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2)

            return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2)
        else:
            cv_sim = stdv_sim/mean_sim
            cv_obs = stdv_obs/mean_obs

            beta = mean_sim / mean_obs
            gamma = cv_sim / cv_obs

            return 1- np.sqrt((r-1)**2 + (beta-1)**2 + (gamma-1)**2)

    @staticmethod
    def scaled_kling_gupta_efficiency(sim, obs, scale_r, scale_alpha, scale_beta):
        sim_mean, obs_mean = np.mean(sim), np.mean(obs)
        sim_stdv, obs_stdv = np.std(sim), np.std(obs)

        r = stats.pearson_correlation_coefficient(sim, obs)
        alpha = sim_stdv / obs_stdv
        beta = sim_mean / obs_mean

        return 1- np.sqrt((scale_r * (r - 1)) ** 2 + (scale_alpha * (alpha - 1)) ** 2 + (scale_beta * (beta - 1)) ** 2)

    @staticmethod
    def objective_function(
        fun, 
        sim, 
        obs, 
        normalize=DataNormalization.none, 
        scale_r=1, 
        scale_alpha=1, 
        scale_beta=1,
        lb=np.empty(0),
        ub=np.empty(0),
        rmna=True
    ):
        sim, obs = np.array(sim), np.array(obs)
        lb, ub = np.array(lb), np.array(ub)

        if rmna:
            ii = (np.isnan(sim) | np.isnan(obs))
            sim, obs = sim[~ii], obs[~ii]

            if lb.shape[0] > 0: lb = lb[~ii]
            if ub.shape[0] > 0: ub = ub[~ii]

        if (normalize != DataNormalization.none and fun in [
            ObjectiveFunction.root_mean_square_error,
            ObjectiveFunction.mean_absolute_error, 
            ObjectiveFunction.mean_square_error
        ]): sim, obs = stats.normalize(sim, obs, normalize)

        if fun == ObjectiveFunction.root_mean_square_error: 
            return stats.root_mean_square_error(sim, obs)
        elif fun == ObjectiveFunction.coefficient_of_determination: 
            return -stats.coefficient_of_determination(sim, obs)
        elif fun == ObjectiveFunction.mean_absolute_percentage_error: 
            return stats.mean_absolute_percentage_error(sim, obs)
        elif fun == ObjectiveFunction.index_of_agreement:
            return -stats.index_of_agreement(sim, obs)
        elif fun == ObjectiveFunction.mean_absolute_error: 
            return stats.mean_absolute_error(sim, obs)
        elif fun == ObjectiveFunction.mean_square_error: 
            return stats.mean_square_error(sim, obs)
        elif fun == ObjectiveFunction.percentage_bias: 
            return stats.percentage_bias(sim, obs)
        elif fun == ObjectiveFunction.ratio_of_rmse_and_obs_stdv: 
            return  stats.rmse_stdv_ratio(sim, obs)
        elif fun == ObjectiveFunction.nash_sutcliffe_efficiency: 
            return -stats.nash_sutcliffe_efficiency(sim, obs)
        elif fun == ObjectiveFunction.NSE_observation_uncertainty:
            return -stats.nse_observation_uncertainty(
                sim=sim, obs=obs, lb=lb, ub=ub
            )
        elif fun == ObjectiveFunction.NSE_observation_uncertainty_II:
            return -stats.nse_observation_uncertainty_II(
                sim=sim, obs=obs, lb=lb, ub=ub
            )
        elif fun == ObjectiveFunction.kling_gupta_efficiency: 
            return -stats.kling_gupta_efficiency(sim, obs)
        elif fun == ObjectiveFunction.KGE_2009: 
            return -stats.kling_gupta_efficiency_2009(sim, obs)
        elif fun == ObjectiveFunction.scaled_kling_gupta_efficiency: 
            return -stats.scaled_kling_gupta_efficiency(
                                sim, obs, scale_r, scale_alpha, scale_beta)
        elif fun == ObjectiveFunction.pearson_correlation_coefficient: 
            return -stats.pearson_correlation_coefficient(sim, obs)
        elif fun == ObjectiveFunction.KGE_alpha: 
            return -stats.KGE_alpha(sim, obs)
        elif fun == ObjectiveFunction.KGE_beta: 
            return -stats.KGE_beta(sim, obs)
        elif fun == ObjectiveFunction.KGE_dAlpha: 
            return -stats.KGE_dAlpha(sim, obs)
        elif fun == ObjectiveFunction.KGE_dBeta: 
            return -stats.KGE_dBeta(sim, obs)
        else: return np.nan

    @staticmethod
    def all_efficiencies(sim, obs):
        sse, mse, rmse, mae, mape, pbias, rsr, r, r2, ioa, nse, kge = (
            None, None, None, None, None, None, None, None, None, None, None, 
            None
        )

        statistic_names = [
            'sse', 'mse', 'rmse', 'mae', 'mape', 'pbias', 'rsr', 'r', 'r2', 
            'ioa', 'nse', 'kge'
        ]

        try:
            sim, obs = np.array(sim), np.array(obs)

            sse = stats.sum_squared_error(sim=sim, obs=obs)
            mse = stats.mean_square_error(sim=sim, obs=obs)
            rmse = stats.root_mean_square_error(sim=sim, obs=obs)
            mae = stats.mean_absolute_error(sim=sim, obs=obs)
            mape = stats.mean_absolute_percentage_error(sim=sim, obs=obs)
            pbias = stats.percentage_bias(sim=sim, obs=obs)
            rsr = stats.rmse_stdv_ratio(sim=sim, obs=obs)
            r = stats.pearson_correlation_coefficient(sim=sim, obs=obs)
            r2 = stats.coefficient_of_determination(sim=sim, obs=obs)
            ioa = stats.index_of_agreement(sim=sim, obs=obs)
            nse = stats.nash_sutcliffe_efficiency(sim=sim, obs=obs)
            kge = stats.kling_gupta_efficiency(sim=sim, obs=obs)
        except: pass

        return statistic_names, [sse, mse, rmse, mae, mape, pbias, rsr, r, r2, ioa, nse, kge]

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
        elif fun == 'sum': return np.sum(data)
        elif fun == 'range': return np.max(data)-np.min(data)
        else: return np.nan

    @staticmethod
    def multiple_statistics(data, functions):
        results = []
        for fun in functions: results.append(stats.statistics(data, fun))
        return results

    @staticmethod
    def row_statistics(data2dim, function='sum'):
        data2dim = np.array(data2dim)
        function = function.lower()

        results = []
        if function == 'sum': results = data2dim.sum(axis=1)
        elif function == 'mean': results = data2dim.mean(axis=1)
        elif function == 'min': results = data2dim.min(axis=1)
        elif function == 'max': results = data2dim.max(axis=1)
        else: return [np.nan] * data2dim.shape[0]

        return results.tolist()

    @staticmethod
    def column_statistics(data2dim, function='sum'):
        data2dim = np.array(data2dim)
        function = function.lower()

        results = []
        if function == 'sum': results = data2dim.sum(axis=0)
        elif function == 'mean': results = data2dim.mean(axis=0)
        elif function == 'min': results = data2dim.min(axis=0)
        elif function == 'max': results = data2dim.max(axis=0)
        else: return [np.nan] * data2dim.shape[0]

        return results.tolist()

    @staticmethod
    def ratio(d1, d2): # ratio of d1 to d2
        d1, d2 = np.array(d1), np.array(d2)
        return (d1/d2).tolist()

    @staticmethod
    def average_uncertainty_band_width(
        ensemble:np.ndarray,
        column_represents_timeseries:bool=True,
        reference_means:np.ndarray=np.empty(0)
    ):
        """
        Computes the average uncertainty band width (AUBW) for an ensemble of 
        time-series.
            AUBW = (1/n) * Σ((max_t - min_t)/mean_t)

        Parameters:
        @param ensemble: (2-d numpy array) ensemble of time-series
        @param column_represents_timeseries: (bool, optional, default=True) flag
                        showing the orientation of time-series in the ensemble 
                        dataset. if the flag is true, each column of ensemble 
                        will be considered as a member time-series. Otherwise,
                        the rows will be treated as ensemble member
        @param reference_mean: (1-d numpy array, optional) if provided, the
                        reference means will be used to scale the width of 
                        uncertainty for a single time step. if  not provided,
                        the ensemble mean will be used as reference mean.
        @return (1-d numpy array) Average uncertainty band width 

        Reference:
        (1) Jin, X., Xu, C.-Y., Zhang, Q., and Singh, V. P. (2010). Parameter 
        and modeling uncertainty simulated by GLUE and a formal Bayesian method 
        for a conceptual hydrological model. J. Hydrol., 383 (3-4), 147–155, 
        https://doi.org/10.1016/j.jhydrol.2009.12.028
        """
        ensemble = np.array(ensemble)
        reference_means = np.array(reference_means)

        if ensemble.shape[0] == 0 or ensemble.ndim != 2: return None
        if not column_represents_timeseries: ensemble = ensemble.T

        if reference_means.shape[0] != ensemble.shape[0]:
            reference_means = np.nanmean(ensemble, axis=0)[:,np.newaxis]
            
        
        mins = ensemble.min(axis=1)
        maxs = ensemble.max(axis=1)
        
        aubw = np.nanmean((maxs-mins)/reference_means)

        return aubw

    @staticmethod
    def ub_coverage(
        timeseries:np.ndarray,
        low_bound:np.ndarray,
        high_bound:np.ndarray
    ):
        """
        Computes uncertainty band (UB) coverage i.e., percentage of number of 
        monthly values of a timeseries that fall within defined uncertainty band 
        of a lower and higher bounds. the statistic describes quality of 
        prediction for a simulated timeseries for being within the uncertainty
        bound of observation data.

        Parameters:
        @param timeseries: (1-d numpy array) prediction time-series
        @param low_bound: (1-d numpy array) the lower bound of the uncertainty 
        @param high_bound: (1-d numpy array) the higher bound of uncertainty 
        @return (float, within 0 and 1) percentage of number of values bounded 
                        witinin uncertainty bounds

        """

        n = timeseries.shape[0]
        if n == 0 or low_bound.shape[0] != n or high_bound.shape[0] != n:
            return None
        
        return np.sum((timeseries>=low_bound)&(timeseries<=high_bound))/n