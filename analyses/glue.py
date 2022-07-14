
import os, numpy as np, pandas as pd
from tabnanny import verbose
from datetime import datetime, timedelta

from wgap.wgapio import WaterGapIO
from calibration.stats import stats

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
        verbose=False
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

        ## read observation dataset
        obs = pd.read_csv(filename_obs)
        obs = obs.iloc[:, -3:]  # keep last three columns
        obs.columns = ['year', 'month', 'obs']
        ##

        ## compute anomalies [if necessary]
        if compute_anomaly:
            ref_start_year, ref_end_year = period_ref_mean
            ref_mean = obs[(obs.year>=ref_start_year)&(
                            obs.year<=ref_end_year)].obs.mean()
            obs.iloc[:, -1] -= ref_mean
        ##

        ## filter data according to years
        if not (start_year == -1 and end_year == -1):
            obs = obs[(obs.year>=start_year)&(obs.year<=end_year)]
        ##

        ## apply conversion factor to observation dataset
        if conversion_factor_obs != 1:
            obs.loc[:,'obs'] *= conversion_factor_obs
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
            
            s, o = simobs.sim.values, simobs.obs.values
            fx.append([fun(s, o) for fun in funs])
            
            if verbose and (sid+1)%Glue.__verbose_frequency==0: 
                tm1 = datetime.now()
                print('%d samples have been proceed [%0.2f]'%(sid+1, (tm1-tm0).total_seconds()))
                tm0 = tm1
        fx = np.array(fx)
        
        df_out = pd.DataFrame(data=fx, columns=funnames)
        df_out.insert(0, 'sid', sids)
        
        return df_out
    
    @staticmethod
    def map_objective_functions(
        funnames
    ):
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