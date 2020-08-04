# -*- coding: utf-8 -*-


# import required modules and classes
import os, sys, numpy as np
from datetime import datetime
from collections import OrderedDict
from copy import deepcopy
from matplotlib import pyplot as plt


sys.path.append('..')
from wgap.wgapio import WaterGapIO
from wgap.watergap import WaterGAP
from calibration.configuration import Configuration
from calibration.seasonalstats import SeasonalStatistics
from utilities.fileio import FileInputOutput as io

class SensitivityAnalysis:
    # methods and variables of SensitivityAnalysis class
    # [to be added]
    #
    
    
    class SampleEvaluation:
        @staticmethod
        def evaluate_sample(
                config:Configuration,
                iter_no:int,
                node_id:int):
            '''
            This function evaluates a (parameter) sample. The method runs the
            model with sample parameter value and then computes prediction
            summaries

            :param config: (Configuration) configuration object. The config
                            object contains all required information about how
                            to run the model, which parameters to modify, which
                            output files to be read in and what statistical
                            calculation to be made etc
            :param iter_no: (int) iteration number. the iteration number serves
                            as the sample identifier from the sample file
            :param node_id: (int) serial number for processing node
            :return: (bool) on successful operation it returns True,
                            False otherwise.
            '''
            arguments = OrderedDict()

            # step: collect parameter values from sample
            params = config.samples[iter_no]

            # step: update parameter values
            if len(params) == len(config.parameters):
                for i in range(len(params)):
                    config.parameters[i].parameter_value = params[i]
            else: return False

            # step: write new parameter file with update parameter values
            pfix = str(iter_no).rjust(6, '0')
            filename = WaterGAP.json_parameter_file[:-5] + '_' + pfix + '.json'
            if not WaterGAP.update_parameter_file(config.parameters, filename):
                return False
            arguments['p'] = filename

            # step: create output output_directory and output_directory file
            output_dir = 'output_' + pfix
            dir_filename = 'data_' + pfix + '.dir'
            if not WaterGAP.update_directory_info(output_dir, dir_filename):
                return False
            arguments['d'] = dir_filename

            # step: execute model with new parameters
            log_file = '/dev/null'  # os.path.join(WaterGAP.home_directory,
                                    #              'log', 'run' + pfix + '.log')
            if not WaterGAP.execute_model(arguments, log_file=log_file):
                WaterGAP.remove_files(arguments)
                return False

            # step: read the model output and dump predictions
            succeed = True
            dumping_directory = config.output_directory
            output_directory_name = os.path.join(
                                            WaterGAP.home_directory,
                                            WaterGAP.dir_info.output_directory)
            if config.dump_model_prediction:
                attribs = [iter_no]
                for var in config.sim_variables:
                    succeed = var.dump_time_series_from_model_prediction(
                                    WaterGAP.start_year,
                                    WaterGAP.end_year,
                                    additional_attributes=attribs,
                                    prediction_directory=output_directory_name,
                                    dumping_directory=dumping_directory,
                                    prefix_filename=str(node_id))

                    if not succeed: break

            if (config.compute_prediction_efficiency or
                config.compute_prediction_statistics or
                config.compute_seasonal_statistics):

                sim_vars = deepcopy(config.sim_variables)
                der_vars = deepcopy(config.derived_variables)
                obs_vars = config.obs_variables

                # read model output
                if not WaterGAP.read_predictions(sim_vars):
                    WaterGAP.remove_files(arguments)
                    return False

                # derive data for derived variables
                for var in der_vars: var.derive_data(simvars=sim_vars,
                                                     obsvars=obs_vars)

                separator = ','
                if config.compute_prediction_statistics:
                    funs = ['mean', 'std', 'min', 'max', 'q1', 'median', 'q3']
                    pred_stat, month_stat, year_stat \
                    = WaterGAP.prediction_statistics(sim_vars, funs=funs)

                    # writing basic prediction statistics
                    filename = config.prediction_summary_output_filename
                    if filename:
                        lines = []
                        for key in pred_stat.keys():
                            for v in pred_stat[key]:
                                lines.append(separator.join(
                                                map(str, [iter_no, key] + v)))

                        if lines:
                            io.print_on_file(lines, filename, '_STAT_OS.LOCK',
                                          sleep_time=0.3)

                    filename = config.prediction_summary_monthly_output_filename
                    if filename:
                        lines = []
                        for key in month_stat.keys():
                            var_stat = month_stat[key]

                            for vk in var_stat.keys():
                                lines.append(separator.join(
                                    map(str, [iter_no, key,
                                              separator.join(map(str, vk))] +
                                        var_stat[vk])))

                        if lines:
                            io.print_on_file(lines, filename, '_STAT_MS.LOCK',
                                             sleep_time=0.5)
                    filename = config.prediction_summary_annual_output_filename
                    if filename:
                        lines = []
                        for key in year_stat.keys():
                            var_stat = year_stat[key]
                            for vk in var_stat.keys():
                                lines.append(separator.join(
                                            map(str, [iter_no, key,
                                                separator.join(map(str, vk))] +
                                                var_stat[vk])))

                        if lines:
                            io.print_on_file(lines, filename, '_STAT_YS.LOCK',
                                             sleep_time=0.5)

                if config.compute_seasonal_statistics:
                    filename = config.seasonal_statistics_output_filename
                    if not filename: succeed = False
                    else:
                        lines = []

                        for var in sim_vars+der_vars:
                            var_name = 'sim_%s'%var.varname.lower()
                            data = [iter_no, var_name]
                            try:
                                snames, results \
                                = SeasonalStatistics.seasonal_summary(
                                                                var.data_cloud)

                                if results:
                                    for key in results.keys():
                                        data += list(results[key])
                            except: data += [None] * 10 * 7

                            try:
                                snames, results \
                                = SeasonalStatistics.monthly_summary(
                                                                var.data_cloud)

                                if results:
                                    for key in results.keys():
                                        data += list(results[key])
                            except: data += [None] * 6 * 12
                            lines.append(separator.join(str(x) for x in data))

                        if lines:
                            io.print_on_file(lines,
                                             filename,
                                             '_STAT_SUMMARY.LOCK',
                                             sleep_time=0.2)

                if config.compute_prediction_efficiency:
                    filename = config.prediction_efficiency_output_filename
                    if not filename: succeed = False
                    else:
                        for var in sim_vars: var.compute_anomalies()
                        for var in der_vars: var.compute_anomalies()

                        try:
                            results = WaterGAP.prediction_efficiency(
                                            sim_vars=sim_vars+der_vars,
                                            obs_vars=obs_vars,
                                            iter_no=iter_no)
                        except:
                            results = []
                            for var in obs_vars+der_vars:
                                results += [iter_no, var.varname,
                                            var.counter_variable] + [None] * 12
                        lines = []
                        for d in results:
                            lines.append(separator.join(map(str, d)))

                        if lines:
                            io.print_on_file(lines, filename, '__PREDEFF.LOCK',
                                             sleep_time=0.1)

            # step: remove model output files
            WaterGAP.remove_files(arguments)

            return succeed

    # end of SampleEval_ModelRun class

    class SampleEval_ComputeFx:
        '''
        Sample evaluation (step-two): Compute f(x)

        This class calculates root mean squared deviation of each prediction
        variable, predicted by the model using a sample parameter set, from the
        predictions with a reference parameter sample. The predictions are
        generated by the model in the first step of the sample evaluation and
        stored in binary file as basin scale summary monthly time series. The
        samples are taken using the SAFE1.8 Toolbox in MatLab using Morris
        (1991) sampling strategy for EET SA method. Two sampling parameters are
        important for this module to identify the reference sample from the
        sample set which are: (i) Number of EE to be used (r) in EET analysis
        and (ii) Number of parameters to be considered (M) was 24. Other
        sampling parameters are not relevant to this module. Every ((M+1) * i;
        where i ε {0, 1, 2, ... r-1})th  sample is considered as the reference
        sample for the next r samples.

        Algorithm:
            Step-1: assign r and M
            Step-2: gather information regarding the prediction variables and
                    the address of summary time-series at model runs with samples
                    (output of step-one of sample evaluation). This information
                    can be readily available in the configuration file used in
                    the step-one of sample evaluation.
            Step-3: read binary time-series file for each variable, reconstruct
                    the timeseries
            Step-4: find the reference sample and reference time-series
            Step-5: compute the root mean squared deviation (rmsd), set rmsd of
                    the reference sample to zero
            Step-6: sort the result according to the sample appearance in the
                    sample file and save the result
            Notes : In addition to root mean squared deviation, other useful
                    statistics can be calculated following the same algorithm;
                    however, in case of other statistics, it is not necessary to
                     assign zero to the reference sample.

        Definition of Root Mean Squared Deviation (rmsd):
                rmsd = sqrt ( mean ( (pred_ref - pred_sam) ** 2) );
                where pred_ref is the prediction time series with reference
                sample and pred_sam is the prediction time series with the
                current sample

        Inputs:
            __r                 : (int) Number of EEs (r)
            __m                 : (int) Number of model parameters (M)
            __fx                : (function) function definition; default is
                                  rmsd i.e., root mean squared difference
        '''
        # private variables
        __r = 0                 # No. of trajectories   
        __m = 0                 # No. of parameters
        __fx = None             # function to compute f(x)
        
        __anomaly_flag = False  # flag to determine if anomalies would be 
                                # computed before applying f(x)
        
        @staticmethod
        def get_no_of_trajectories(): 
            return SensitivityAnalysis.SampleEval_ComputeFx.__r
        
        @staticmethod
        def set_no_of_trajectories(r):
            SensitivityAnalysis.SampleEval_ComputeFx.__r = r
        
        @staticmethod
        def get_no_of_parameters(): 
            return SensitivityAnalysis.SampleEval_ComputeFx.__m
        
        @staticmethod
        def set_no_of_parameters(m):
            SensitivityAnalysis.SampleEval_ComputeFx.__m = m
            
        @staticmethod
        def get_anomaly_flag():
            return SensitivityAnalysis.SampleEval_ComputeFx.__anomaly_flag
        
        @staticmethod
        def set_anomaly_flag(flag):
            SensitivityAnalysis.SampleEval_ComputeFx.__anomaly_flag = flag
        
        @staticmethod
        def set_fun(fun):
            SensitivityAnalysis.SampleEval_ComputeFx.__fx = fun
            
        @staticmethod
        def set_static_parameters(no_of_trajectories,
                               no_of_parameters,
                               compute_anomaly_flag):
            
            SensitivityAnalysis.SampleEval_ComputeFx.__r = no_of_trajectories
            SensitivityAnalysis.SampleEval_ComputeFx.__m = no_of_parameters
            SensitivityAnalysis.SampleEval_ComputeFx.__anomaly_flag = \
                            compute_anomaly_flag
        
        @staticmethod
        def compute_rmsd(ts1:np.ndarray, ts2:np.ndarray)->np.ndarray:
            '''
            The method computes the root mean squared deviation (rmsd) between 
            two time series of same length.
            
            :param ts1: (1d numpy array) First time-series
            :param ts2: (1d numpy array) Second time-series
            :return: (float) root of mean squared deviation
            '''
            return np.sqrt(np.mean((ts1-ts2)**2))

        @staticmethod
        def construct_time_series(basin_data, sample_id):
            """
            This method constructs 1d time-series from basin data. First it find 
            data  for specified sample and then sort data according to years. 
            Finally, it constructs the time-series with monthly data of all 
            years.
            
            :param data: (ndarray) input 2d data having 15 columns containing 
                                   sample id, basin id, year, and 12 monthly 
                                   values
            :param sample_id: (int) sample id
            :return: (1d numpy array) time series for the current sample for 
                                      specified basin
            """
            
            # step: filter data using basin id and sample id. crop data from 
            # 3rd column till the end column [expected shape is (nyear, 13)]
            ndx = np.where(basin_data[:, 0] == sample_id)
            d = basin_data[ndx][:, 2:]
            
            # step: sort the data according to the year column. crop data from
            # 2nd column till the end column
            ndx = np.argsort(d[:, 0])
            d = d[ndx][:, 1:]
            
            return d.flatten()
        
        @staticmethod
        def compute_fx(data_filename, 
                       output_filename, 
                       no_of_trajectories:int=0,
                       no_of_parameters:int=0):
            
            __self = SensitivityAnalysis.SampleEval_ComputeFx
            
            # step: check inputs
            if no_of_trajectories > 0: __self.__r = no_of_trajectories
            if no_of_parameters > 0: __self.__m = no_of_parameters
                        
            flag_compute_anomaly = __self.__anomaly_flag
            construct_timeseries = __self.construct_time_series
                        
            fx = __self.__fx
            if not fx: fx = __self.compute_rmsd
            
            r = __self.__r
            m = __self.__m
            
            if r <= 0 or m <= 0: return np.empty(0)
            if not os.path.exists(data_filename): return np.empty(0)
            # end of step
            
            # step: compute sample size
            
            nsample = r * (m + 1)
            # end of step
            
            # step: read binary data from the data-file
            data = WaterGapIO.read_unf(data_filename)
            if not type(data) is np.ndarray: return np.empty(0)
            
            
            # step: for each basin/cell, compute rmsd with each sample and store 
            # the results
            basins = np.unique(data[:,1])
            
            results_rmsd = []
            for bid in basins:
                print('\tcurrent basin no.: %d' %bid, end='', flush=True)
                t = datetime.now()
                
                time_series_ref = None          # reference time series
                
                # step: crop basin specific predictions from data
                ndx = np.where(data[:, 1] == bid)
                basin_data = data[ndx]
                # ... end [of data cropping]
                
                # step: for each sample, construct time-series and compute rmsd 
                # with the current time-series and reference time-series. if the
                # current sample is a reference sample, reference time-series 
                # must be updated  with the current time-series and 'rmsd'  
                # should be assign to zero
                for sid in range(nsample):
                    time_series_curr = construct_timeseries(basin_data, sid)
                    if flag_compute_anomaly: 
                        time_series_curr = time_series_curr - time_series_curr.mean()
                    
                    if sid % (m + 1) == 0:
                        # if the current sample should be considered as a 
                        # reference, set rmsd to zero and update the reference 
                        # time-series with current time-series
                        rmsd = 0
                        time_series_ref = time_series_curr
                    else: rmsd = fx(time_series_curr, time_series_ref)
                
                    results_rmsd.append([bid, sid, rmsd])
                
                # display how much time required for each basin
                tdif = datetime.now() - t
                total_t = tdif.seconds + tdif.microseconds / 10**6
                print(' [total time: %f seconds]' % total_t)
            
            if output_filename:
                np.savetxt(output_filename, results_rmsd, delimiter=',', 
                           fmt='%d,%d,%.15f')
            
            return np.array(results_rmsd)
        # end of function
    
    # end of SampleEval_ComputeFx class


    class ParameterSelection:
        __method = 'major contributors' # methosds: Equal Top Rank, 
                                        #           Major Contributors
        __contribution_threshold = 0.5
        
        @staticmethod
        def set_selection_method(method):
            SensitivityAnalysis.ParameterSelection.__method = method
        
        @staticmethod
        def get_selection_method():
            return SensitivityAnalysis.ParameterSelection.__method
        
        @staticmethod
        def set_contribution_threshold(threshold):
            __self__ = SensitivityAnalysis.ParameterSelection
            if threshold > 0:
                __self__.__contribution_threshold = threshold
        
        @staticmethod
        def get_contribution_threshold():
            __self__ = SensitivityAnalysis.ParameterSelection
            return __self__.__contribution_threshold
        
        @staticmethod
        def major_contributors(si:np.ndarray, threshold=0.5):
            # step: check inputs
            e = np.empty(0)
            if type(si) is not np.ndarray or si.shape[0] == 0: 
                return e, []
            
            if threshold <= 0:
                __self__ = SensitivityAnalysis.ParameterSelection
                threshold = __self__.__contribution_threshold
            # end of step
            
            # step: attach parameter id
            nparam = si.shape[0]
            
            d_out = np.arange(1, nparam + 1).reshape(nparam, 1)
            d_out = np.concatenate((d_out, si.reshape(nparam, 1)), axis=1)
            
            colnames = ['paramid', 'si']
            # end of step
            
            # step: compute ranks [1 to no. of parameters] and sort
            ranks = (np.argsort(np.argsort(-si)) + 1).reshape(-1, 1)
            d_out = np.concatenate((d_out, ranks), axis=1)
            colnames.append('rank')
            
            ii = np.argsort(d_out[:, 2])
            d_out = d_out[ii]
            # end of step
            
            # step: compute cumulative contribution of (ranked) parameters
            # [NB: d_out column index 2 is the rank column]
            tee = np.sum(d_out[:, 1])   # total elementary effects
            contrib = d_out[:, 1]/tee   # contribution of each parameters
            cum_contrib = np.cumsum(contrib).reshape(-1, 1)
            
            d_out = np.concatenate((d_out, contrib.reshape(-1,1)), axis=1)
            colnames.append('contrib')
            # end of step
            
            # step: select parameters based on (least) contribution threshold
            
            # find index of first element where cumulative contribution is
            # higher or equal to the (least) contribution threshold
            i = np.where(cum_contrib >= threshold)[0][0]
            sel = np.zeros((nparam, 1))
            sel[:i+1,:] = 1
            
            d_out = np.concatenate((d_out, sel), axis=1)
            colnames.append('selection')
            # end of step
            
            # step: sort parameters according to parameter id
            ii = np.argsort(d_out[:, 0])
            d_out = d_out[ii]
            # end of step
            
            return d_out, colnames

        @staticmethod
        def compute_ranks(
            si:np.ndarray,
            filename_out:str = ''
        ):
            ndim = si.ndim
            if ndim == 1: si = si.reshape(-1, 1)

            nparam, nvar = si.shape

            ranks_out = np.empty(0)
            for i in range(nvar):
                ranks = (np.argsort(np.argsort(-si[:,i])) + 1).reshape(-1, 1)

                try: ranks_out = np.concatenate((ranks_out, ranks), axis=1)
                except: ranks_out = ranks

            if filename_out:
                fmt = ','.join(['%d'] * nvar)
                np.savetxt(filename_out, ranks_out, delimiter=',', fmt=fmt)
            else:
                if ndim == 1: ranks_out = ranks_out.flatten()
                return ranks_out

    # end of ParameterSelection class
    
    class Plot:
        @staticmethod
        def plot_parameter_ranks(
            ranks:np.ndarray,
            parameter_names:list,
            xvar_names:list,
            filename_out:str='',
            ax=None,
            figsize=(5, 7),
            title='',
            colormap='YlOrRd_r',
            show_cmap=False,
            show_yticks=True,
            fig_adjust_params={'left': 0.15, 'bottom': 0.20, 'right': 0.95,
                               'top': 0.95, 'wspace': None, 'hspace': None},
            tight_layout=False
        ):
            # colormaps:
            # Accent, Accent_r, Blues, Blues_r, BrBG, BrBG_r, BuGn, BuGn_r, 
            # BuPu, BuPu_r, CMRmap, CMRmap_r, Dark2, Dark2_r, GnBu, GnBu_r, 
            # Greens, Greens_r, Greys, Greys_r, OrRd, OrRd_r, Oranges, 
            # Oranges_r, PRGn, PRGn_r, Paired, Paired_r, Pastel1, Pastel1_r, 
            # Pastel2, Pastel2_r, PiYG, PiYG_r, PuBu, PuBuGn, PuBuGn_r, PuBu_r, 
            # PuOr, PuOr_r, PuRd, PuRd_r, Purples, Purples_r, RdBu, RdBu_r, 
            # RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu, RdYlBu_r, RdYlGn, RdYlGn_r, 
            # Reds, Reds_r, Set1, Set1_r, Set2, Set2_r, Set3, Set3_r, Spectral,
            # Spectral_r, Wistia, Wistia_r, YlGn, YlGnBu, YlGnBu_r, YlGn_r, 
            # YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r, afmhot, afmhot_r, autumn, 
            # autumn_r, binary, binary_r, bone, bone_r, brg, brg_r, bwr, bwr_r, 
            # cividis, cividis_r, cool, cool_r, coolwarm, coolwarm_r, copper, 
            # copper_r, cubehelix, cubehelix_r, flag, flag_r, gist_earth, 
            # gist_earth_r, gist_gray, gist_gray_r, gist_heat, gist_heat_r, 
            # gist_ncar, gist_ncar_r, gist_rainbow, gist_rainbow_r, gist_stern, 
            # gist_stern_r, gist_yarg, gist_yarg_r, gnuplot, gnuplot2, 
            # gnuplot2_r, gnuplot_r, gray, gray_r, hot, hot_r, hsv, hsv_r, 
            # inferno, inferno_r, jet, jet_r, magma, magma_r, nipy_spectral, 
            # nipy_spectral_r, ocean, ocean_r, pink, pink_r, plasma, plasma_r, 
            # prism, prism_r, rainbow, rainbow_r, seismic, seismic_r, spring, 
            # spring_r, summer, summer_r, tab10, tab10_r, tab20, tab20_r, 
            # tab20b, tab20b_r, tab20c, tab20c_r, terrain, terrain_r, twilight, 
            # twilight_r, twilight_shifted, twilight_shifted_r, viridis, 
            # viridis_r, winter, winter_r
            
            
            nrow, ncol = ranks.shape
            if len(parameter_names) != nrow: return False
            if len(xvar_names) != ncol: return False
            
            if ax: 
                fig = ax.figure
                
                filename_out = ''
                tight_layout = False
                fig_adjust_params = {}
            else:
                fig = plt.figure(figsize=figsize)
                ax = fig.add_subplot(111)
                
            im = ax.imshow(ranks, cmap=colormap)
            
            if show_yticks:
                yticks = np.arange(nrow)
                ax.set_yticks(yticks)
                ax.set_yticklabels(parameter_names)
            else: ax.set_yticks([])
            
            ax.set_xticks(np.arange(ncol))
            ax.set_xticklabels(xvar_names, rotation=90)
            
            if show_cmap:
                ticks = np.arange(1, nrow + 1)
                cbar = fig.colorbar(im)
                cbar.set_ticks(ticks)
                cbar.set_ticklabels(ticks)
                
                if colormap[-2:] == '_r': cbar.ax.invert_yaxis()
                cbar.set_label('Parameter ranks')
                
                
            
            if title: ax.set_title(title)
            
            if tight_layout: fig.tight_layout()
            elif fig_adjust_params: fig.subplots_adjust(**fig_adjust_params)
              
            if filename_out: fig.savefig(filename_out, dpi=600)

            return fig
    
        @staticmethod
        def multiplot_parameter_ranks(
            list_of_ranks:list,
            parameter_names:list,
            xvar_names:list,
            filename_out:str='',
            figsize=(5, 7),
            titles='',
            colormap='YlOrRd_r',
            show_cmap=True,
            fig_adjust_params={'left': 0.15, 'bottom': 0.20, 'right': 0.95,
                               'top': 0.95, 'wspace': None, 'hspace': None},
            tight_layout=False
        ):
            nplots = len(list_of_ranks)
            
            if nplots == 0: return False
            if titles and len(titles) != nplots: return False
            
            nrow, ncol = list_of_ranks[0].shape
            if len(parameter_names) != nrow: return False
            if len(xvar_names) != ncol: return False
            
            fig = plt.figure(figsize=figsize)
            
            ax, show_yticks, show_cmap_i, title = None, True, False, ''
            
            for i in range(nplots):
                ranks = list_of_ranks[i]
                
                if titles: title = titles[i]
                
                if show_cmap and i == (nplots-1): show_cmap_i = True
                
                ax = fig.add_subplot(1, nplots, i+1)
                
                f = SensitivityAnalysis.Plot.plot_parameter_ranks(
                        ranks=ranks,
                        parameter_names=parameter_names,
                        xvar_names=xvar_names,
                        title=title,
                        show_yticks=show_yticks,
                        show_cmap=show_cmap_i,
                        ax=ax,
                        colormap=colormap
                )
                
                show_yticks = False
            
            if tight_layout: fig.tight_layout()
            else: fig.subplots_adjust(**fig_adjust_params)
            
            if filename_out: fig.savefig(filename_out, dpi=600)
            
            return fig
        
