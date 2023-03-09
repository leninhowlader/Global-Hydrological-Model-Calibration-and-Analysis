import os, numpy as np, pandas as pd
from datetime import datetime, timedelta

from wgap.wgapio import WaterGapIO
from core.stats import stats

class Glue:
    __verbose_frequency = 200
    
    @staticmethod
    def set_verbose_frequency(value):
        try: Glue.__verbose_frequency = int(value)
        except: pass

    @staticmethod
    def compute_objective(
        filename_obs,
        filename_simunf,
        funs,
        funnames:tuple=(),
        start_year=-1, 
        end_year=-1,
        compute_anomaly=False,
        period_ref_mean=(),
        basinid=0,
        sample_id_start=0,
        sample_id_end=20000,
        conversion_factor_sim=1,
        conversion_factor_obs=1,
        verbose=False,
        observation_series_count=1
    ):
        '''
        notes:
        (1) If we work with a subset of the data, the computation would be 
            faster. This would also allow us to split the workload on multiple
            machines or processors later on.
        '''
        if compute_anomaly:
            if not period_ref_mean: 
                if (start_year > 1900 < end_year and
                    end_year >= start_year): 
                    period_ref_mean = (start_year, end_year)
                else: compute_anomaly = False
        
        if not (start_year > 1900 < end_year and end_year >= start_year):
            start_year = end_year = -1

        while len(funnames) < len(funs): funnames += ('fx_%02d'%len(funnames),)
        if observation_series_count < 1: observation_series_count = 1

        ## read observation dataset
        nseries = observation_series_count
        columns = ['year', 'month'] + ['obs_%02d'%(i+1) for i in range(nseries)]
        obs = pd.read_csv(filename_obs)
        obs = obs.iloc[:, -(nseries + 2):]  # keep last three columns
        obs.columns = columns
        ##

        ## compute anomalies [if necessary]
        if compute_anomaly:
            ref_start_year, ref_end_year = period_ref_mean
            ref_mean = obs[(obs.year>=ref_start_year)&(obs.year<=ref_end_year)
                          ].iloc[:,2:].mean(axis=0).values
            obs.iloc[:, 2:] -= ref_mean
        ##

        ## filter data according to years
        if not (start_year == -1 and end_year == -1):
            obs = obs[(obs.year>=start_year)&(obs.year<=end_year)]
        ##

        ## apply conversion factor to observation dataset
        if conversion_factor_obs != 1:
            obs.iloc[:,2:] *= conversion_factor_obs
        ##
        
        ## read simulation data (unf files) and crop dataset for a basin
        d = WaterGapIO.read_unf(filename_simunf)
        
        ii = np.where((d[:,0]>=sample_id_start)&(d[:,0]<=sample_id_end)) # see note (1)
        d = d[ii][:, [0, 1, 2, (basinid+3)]].byteswap().newbyteorder()
        ##

        ## create a dataframe object 
        sim_df = pd.DataFrame(data=d[:,:-1].astype(int), columns=['sid', 'year', 'month'])
        sim_df['sim'] = d[:,-1]
        ##
        
        ## apply conversion factor to simulated values
        if conversion_factor_sim != 1: 
            sim_df.loc[:, 'sim'] *= conversion_factor_sim
        ##
        
        if nseries == 1:
            sids = np.unique(d[:,0]).astype(int)
            fx = []
            if verbose: tm0 = datetime.now()
            for sid in sids:
                sim = sim_df[sim_df.sid==sid].iloc[:,1:]
                
                if compute_anomaly:
                    ref_start_year, ref_end_year = period_ref_mean
                    ref_mean = sim[(sim.year>=ref_start_year)&
                                (sim.year<=ref_end_year)].sim.mean()
                    sim.iloc[:, -1] -= ref_mean
                
                simobs = sim.merge(obs, how='inner', on=['year', 'month'])
                simobs = simobs.dropna()

                s, o = simobs.iloc[:,-2].values, simobs.iloc[:,-1].values
                fx.append([fun(s, o) for fun in funs])
                
                if verbose and (sid+1)%Glue.__verbose_frequency==0: 
                    tm1 = datetime.now()
                    print('%d samples have been proceed [%0.2f]'%(sid+1, (tm1-tm0).total_seconds()))
                    tm0 = tm1
            
            fx = np.array(fx)
            fx = np.insert(fx, 0, sids[np.newaxis, :], axis=1)

        else:
            sids = np.unique(d[:,0]).astype(int)
            
            fx = []
            if verbose: tm0 = datetime.now()
            for sid in sids:
                sim = sim_df[sim_df.sid==sid].iloc[:,1:]
                
                if compute_anomaly:
                    ref_start_year, ref_end_year = period_ref_mean
                    ref_mean = sim[(sim.year>=ref_start_year)&
                                (sim.year<=ref_end_year)].sim.mean()
                    sim.iloc[:, -1] -= ref_mean
                
                fx_sid = []
                for i in range(nseries):
                    simobs = sim.merge(obs.iloc[:, [0, 1, 2+i]], how='inner', on=['year', 'month'])
                    simobs = simobs.dropna()

                    s, o = simobs.iloc[:,-2].values, simobs.iloc[:,-1].values
                    fx_sid.append([fun(s, o) for fun in funs])
                fx.append(fx_sid)

                if verbose and (sid+1)%Glue.__verbose_frequency==0: 
                    tm1 = datetime.now()
                    print('%d samples have been proceed [%0.2f]'%(sid+1, (tm1-tm0).total_seconds()))
                    tm0 = tm1
            
            fx = np.array(fx)
            fx = np.insert(fx, 0, sids[np.newaxis,:, np.newaxis], axis=1)

        return fx
    
    @staticmethod
    def map_objective_functions(
        funnames
    ):
        """
        The function maps objective functions and returns the signatures of 
        given function names

        Parameters:
        :param funnames: (list of string) list of function names
        :return (list) list of function signatures
        """
        sse = stats.sum_squared_error
        mse = stats.mean_square_error
        rmse = stats.root_mean_square_error
        mae = stats.mean_absolute_error
        mape = stats.mean_absolute_percentage_error
        pbias = stats.percentage_bias
        rsr = stats.rmse_stdv_ratio
        r = stats.pearson_correlation_coefficient
        r2 = stats.coefficient_of_determination
        ioa = stats.index_of_agreement
        nse = stats.nash_sutcliffe_efficiency
        kge = stats.kling_gupta_efficiency2012
        kge09 = stats.kling_gupta_efficiency
        alpha = stats.KGE_alpha
        beta = stats.KGE_beta
        gamma = stats.KGE_gamma
        def dummy(sim, obs): return np.nan

        funs = []
        for fun in funnames:
            if fun in ['nse']: funs.append(nse)
            elif fun in ['rmse']: funs.append(rmse)
            elif fun in ['kge', 'kge12']: funs.append(kge)
            elif fun in ['r']: funs.append(r)
            elif fun in ['r2', 'R2']: funs.append(r2)
            elif fun in ['sse']: funs.append(sse)
            elif fun in ['mse']: funs.append(mse)
            elif fun in ['mae']: funs.append(mae)
            elif fun in ['mape']: funs.append(mape)
            elif fun in ['pbias']: funs.append(pbias)
            elif fun in ['rsr']: funs.append(rsr)
            elif fun in ['ioa']: funs.append(ioa)
            elif fun in ['kge09', 'kge2009']: funs.append(kge09)
            elif fun in ['alpha']: funs.append(alpha)
            elif fun in ['beta']: funs.append(beta)
            elif fun in ['gamma']: funs.append(gamma)
            else: funs.append(dummy)
        return tuple(funs)

    @staticmethod
    def compute_posterior(
        prior:np.ndarray,
        likelihood:np.ndarray,
        scale:float=1
    ):
        """
        The function computes posterior probabilities given prior, data 
        likelihood and optionally the merginalizing constant

        Posterior probabilities,
            P (A | B) = P (B | A) x P(A) / P(B)

        Parameters:
        :param prior: (1-d array of floats) prior probalibities i.e., P(theta)
        :param likelihood: (1-d array of floats) likelihood given data i.e. P(data|theta)
        :param scale: (float) merginalizing constant P(data)
        :return (1-d array) posterior probabilities i.e, P (theta | data)
        """

        return prior * likelihood / scale

    @staticmethod
    def rescale_probabilities(
        probabilities
    ): 
        """
        The function rescale probabilities to make the sum of all probabilities 
        to unity.

        Parameters:
        :param probabilities: (1-d array) probability quantities
        :return (1-d array) scaled probabilities
        """
        
        return probabilities / probabilities.sum()

    @staticmethod
    def apply_glue(
        fx,
        thresholds,
        method_multivar='combined',
        multivar_combfunc_name='weighted sum',
        multivar_combfunc=None,
        weights=(),
        allstep_probs=False
    ):
        """
        The function estimated posterior parameter probability based on GLUE 
        method

        Parameters:
        :param fx: (n-d numpy array) objective function values for each sample
        :param thresholds: (float or tuple of floats) behevioral model selection
                           threshold(s). all models below the threshold will be
                           assigned zero probabilities
        :param metho_multivar: (string) method of glue for multivariable case
        :param multivar_combfunc_name: (string) name of the function to combine
                            function values for multivariable case
        :param multivar_combfunc: (function) signature of function to combine
                            objectives
        :param weights: (tuple of floats) weights for each variable
        :param allstep_probs: (bool) if true, all priors and posteriors in all 
                            steps will be returned
        :return (n-d numpy array) posterior probabilities
        """

        def weighted_sum(fx, weights): return (fx * weights).sum(axis=1)
        def products(fx): return fx.prod(axis=1)

        if fx.ndim == 1: fx = fx[:, np.newaxis]
        nsample, nvar = fx.shape

        if type(thresholds) is float: thresholds = [thresholds] * nvar
        if len(thresholds) == 0: return np.empty(0)
        if len(thresholds) != nvar: thresholds = (list(thresholds) * nvar)[:nvar]

        if len(weights) != nvar: 
            weights = (list(weights) + [1] * nvar)[:nvar]
        weights = np.array(weights)[np.newaxis, :]

        prior = np.ones(nsample)
        if allstep_probs: 
            probs_out = Glue.rescale_probabilities(prior).reshape(-1, 1)

        if method_multivar == 'combined':
            if multivar_combfunc: fx_comb = multivar_combfunc(fx)
            else:
                combfunc = multivar_combfunc_name.lower()
                if combfunc in ['weighted sum', 'weighted_sum']:
                    fx_comb = weighted_sum(fx=fx, weights=weights)
                elif combfunc in ['product', 'multiplication', 'prod']:
                    fx_comb = products(fx=fx)
                else: fx_comb = fx.sum(axis=1)
            
            jj = np.ones(nsample, dtype=bool)
            for i in range(nvar):
                jj &= (fx[:,i]>=thresholds[i])
            
            fx_comb[~jj] = 0
            likelihood = fx_comb.copy()
            posterior = Glue.compute_posterior(
                    prior=prior,
                    likelihood=likelihood,
                    scale=likelihood.sum()
                )

            if posterior.sum() != 1.0: 
                posterior = Glue.rescale_probabilities(posterior)
            
            if allstep_probs: 
                probs_out = np.concatenate((probs_out, posterior.reshape(-1,1)),
                                            axis=1)
        else: # sequential
            for i in range(nvar):
                curr_fx = fx[:,i]
                jj = (curr_fx>=thresholds[i])

                curr_fx[~jj] = 0
                likelihood = curr_fx
                
                posterior = Glue.compute_posterior(
                    prior=prior,
                    likelihood=likelihood,
                    scale=likelihood.sum()
                )

                if posterior.sum() != 1.0: 
                    posterior = Glue.rescale_probabilities(posterior)
                
                if allstep_probs: 
                    probs_out = np.concatenate((probs_out, 
                                                posterior.reshape(-1,1)),
                                                axis=1)
                prior = posterior.copy()

        if allstep_probs: return probs_out
        return posterior

    @staticmethod
    def empirical_cdf(
        x:np.ndarray, 
        probs:np.ndarray
    ):
        """
        The function computes the empirical cummulative distribution function

        Parameters:
        :param x: (1-d numpy array) quantities for whose cdf to be computed
        :param probs: (1-d numpy array) probabilities of quantities in x
        :return (1d-array, 1-d array) 
                (1) sorted x values (2) cummulative probabilities
        """

        ii = np.argsort(x)
        cdf = np.cumsum(probs[ii])

        return x[ii], cdf

    @staticmethod
    def estimated_empirical_pdf(
        x:np.ndarray,
        probs:np.ndarray,
        step:float=0,
        nintervals:int=1000,
        bounds:tuple=(),
        window=50
    ):
        """
        The function estimate propability density function for a given variate

        Parameters:
        :param x: (1-d numpy array) quantities for whose cdf to be computed
        :param probs: (1-d numpy array) probabilities of quantities in x
        :param step: (float) step or interval size
        :param nintervals: (int) (optional) No. of interval; used only when step 
                                 is not provided
        :param bounds: (tuple of float) (optional) lower and upper bound pair
        :param window: (int) window size for computing moving average. moving
                             average will only be computed when window > 1
        :return (1d-array, 1-d array) 
                (1) class intervals of x (2) (smoothed) probabilities
        
        """


        ## inner function for computing moving averages
        def moving_average(x, window=window):
            return np.array([np.mean(x[i:i+window]) 
                            for i in range(x.shape[0] - window)])
        ## end of inner function

        if not bounds: lb, ub = np.min(x), np.max(x)
        else: lb, ub = bounds

        if step == 0: step = (ub-lb) / nintervals
        
        intervals, densities = [], []
        for b in np.arange(lb, ub, step):
            ii = np.where((x>b)&(x<=b+step))

            densities.append(probs[ii].sum()/step)
            #intervals.append((probs[ii]*x[ii]).sum())
            intervals.append(b+step/2)
        
        intervals = np.array(intervals)
        densities = np.array(densities)

        if window > 1: 
            densities = moving_average(x=densities, window=window)
            intervals = moving_average(x=intervals, window=window)
        
        return intervals, densities

    @staticmethod
    def prediction_interval(
        preds:np.ndarray,
        probs:np.ndarray=np.empty(0),
        alpha:float=0.05,
        columns_represent_timeseries:bool=True
    ):
        """
        The function computes prediction interval empirically.

        Parameters:
        :param preds: (2-d numpy array) prediction time series
        :param probs: (1-d numpy array; optional) probabilities associate with 
                            each prediction. if not given, all prediction series
                            will be treated as equally probable
        :param alpha: (float) error level
        :param columns_represent_timeseries: (bool) a flag describs the orientation
                            of the prediction time series. if the flag is true,
                            each column will be considered as a prediction series
        :return (1-d numpy array, 1-d numpy array) lower and upper limits
        """
        lows, highs = np.empty(0), np.empty(0)
        
        if not (0<alpha<=1): return lows, highs
        if not columns_represent_timeseries: preds = preds.T
        if preds.ndim != 2: return lows, highs
        
        ntimestep, nprediction = preds.shape
        if ntimestep == 0 or nprediction == 0: return lows, highs

        if probs.shape[0] != nprediction: 
            probs = np.ones(nprediction) / nprediction
        
        half_alpha = alpha/2

        lows, highs = [], []
        for i in range(ntimestep):
            jj = np.argsort(preds[i, :])

            csum = probs[jj].cumsum()
            kk = jj[(csum>=half_alpha) & (csum <=(1-half_alpha))]
            lows.append(preds[i,kk].min())
            highs.append(preds[i,kk].max())
        lows, highs = np.array(lows), np.array(highs)

        return lows,  highs

        
