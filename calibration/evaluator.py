#!/usr/local/Python-3.5.2/bin/python3

__author__ = 'mhasan'

import os, sys
# sys.path.append('..')
from calibration.configuration import Configuration
# from calibration.variable import SimVariable, ObsVariable, DerivedVariable
from calibration.seasonalstats import SeasonalStatistics
from wgap.watergap import WaterGAP
from utilities.fileio import FileInputOutput as io
# from mpi4py import MPI
from copy import deepcopy
from collections import OrderedDict

def read_iter_number():
    iter_no = 0
    lockname = '_ITER.LOCK'
    fd = open(lockname, 'w')
    if io.acquire_lock(fd):

        f = None
        try:
            f = open('_ITER.VALUE', 'r')
            temp = f.readline().strip()
            iter_no = int(temp)
        except: pass
        finally:
            try: f.close()
            except: pass

        try:
            f = open('_ITER.VALUE', 'w')
            f.write(str(iter_no + 1))
        except: iter_no = -9999 # indicating not to proceed because new iter_no could not be saved
        finally:
            try: f.close()
            except: pass

        io.release_lock(fd)
    else: iter_no = -9999

    return iter_no

def process_parameter_sample(config, iter_no):
    arguments = OrderedDict()

    # collect parameter values from sample
    params = config.samples[iter_no]

    # update parameter values
    if len(params) == len(config.parameters):
        for i in range(len(params)): config.parameters[i].parameter_value = params[i]
    else: return False

    # write new parameter file
    pfix = str(iter_no).rjust(6, '0')
    filename = 'parameters_' + pfix + '.json'
    if not WaterGAP.update_parameter_file(config.parameters, filename): return False
    arguments['p'] = filename

    # create output output_directory and output_directory file
    output_dir = 'output_' + pfix
    dir_filename = 'data_' + pfix + '.dir'
    if not WaterGAP.update_directory_info(output_dir, dir_filename): return False
    arguments['d'] = dir_filename

    # execute model with new parameters
    log_file = '/dev/null' # os.path.join(WaterGAP.home_directory, 'log', 'run' + pfix + '.log')
    if not WaterGAP.execute_model(arguments, log_file=log_file):
        WaterGAP.remove_files(arguments)
        return False

    # read model output
    sim_vars, der_vars, obs_vars = deepcopy(config.sim_variables), deepcopy(config.derived_variables), config.obs_variables
    if not WaterGAP.read_predictions(sim_vars):
        WaterGAP.remove_files(arguments)
        return False

    for var in der_vars: var.derive_data(simvars=sim_vars, obsvars=obs_vars)

    # step-x.x: calculate prediction summaries
    # ------- begin of step-x.x -------
    # note: statistics will be generation with actual data (i.e. no anomalies will be included)
    lines, separator = [], ','
    if config.prediction_statistics:
        filename = config.summary_statistics_filename
        for var in sim_vars+der_vars:
            var_name = 'sim_%s'%var.varname.lower()
            data = [iter_no, var_name]
            try:
                snames, results = SeasonalStatistics.seasonal_summary(var.data_cloud)
                if results:
                    for key in results.keys(): data += list(results[key])
            except: data += [None] * 10 * 7     # 10 statistics of 7 seasonal behaviors

            try:
                snames, results = SeasonalStatistics.monthly_summary(var.data_cloud)
                if results:
                    for key in results.keys(): data += list(results[key])
            except: data += [None] * 6 * 12     # 6 statistics of 12 monthly
            
            lines.append(separator.join(str(x) for x in data))

        if lines: print_on_file(lines, filename, '_STAT_SUMMARY.LOCK', sleep_time=0.2)

        # --------------------- old code ------------------------
        # funs = ['mean', 'std', 'min', 'max', 'q1', 'median', 'q3']
        # pred_stat, month_stat, year_stat = WaterGAP.prediction_statistics(sim_vars, funs=funs)
        #
        # # writing basic prediction statistics
        # lines = []
        # for key in pred_stat.keys():
        #     for v in pred_stat[key]: lines.append(separator.join(map(str, [iter_no, key] + v)))
        # if lines: print_on_file(lines, config.prediction_summary_filename, '_STAT_OS.LOCK', sleep_time=0.3)
        #
        # lines = []
        # for key in month_stat.keys():
        #     var_stat = month_stat[key]
        #     for vk in var_stat.keys(): lines.append(separator.join(map(str, [iter_no, key, separator.join(map(str, vk))] + var_stat[vk])))
        # if lines: print_on_file(lines, config.monthly_prediction_summary_filename, '_STAT_MS.LOCK', sleep_time=0.5)
        #
        # lines = []
        # for key in year_stat.keys():
        #     var_stat = year_stat[key]
        #     for vk in var_stat.keys(): lines.append(separator.join(map(str, [iter_no, key, separator.join(map(str, vk))] + var_stat[vk])))
        # if lines: print_on_file(lines, config.yearly_prediction_summary_filename, '_STAT_YS.LOCK', sleep_time=0.5)
    # ------ end of step-x.x --------

    # step-x.x: calculate efficiencies
    # ----- begin of step-x.x -------
    for var in sim_vars: var.compute_anomalies()
    for var in der_vars: var.compute_anomalies()
    
    try: results = WaterGAP.prediction_efficiency(sim_vars=sim_vars+der_vars, obs_vars=obs_vars, iter_no=iter_no)
    except:
        results = []
        for var in obs_vars+der_vars: results += [iter_no, var.varname, var.counter_variable] + [None] * 12   # 12 statistics (i.e. error or efficiency)
        
    lines = []
    for d in results: lines.append(separator.join(map(str, d)))
    if lines: print_on_file(lines, config.prediction_efficiency_filename, '__PREDEFF.LOCK', sleep_time=0.1)
    # ------ end of step-x.x --------

    # remove files
    WaterGAP.remove_files(arguments)

    # return increment_done_count()
    return True

def main(argv):
    # __________________________________________________________________________________________________________________
    # step-01: initialize MPI
    # comm = MPI.COMM_WORLD
    # rank = comm.Get_rank()
    iter_no = -9999
    while True:
        iter_no = read_iter_number()    # starts from zero
        if iter_no >= 0: break

    # check program arguments
    # this program needs one argument as the address of configuration file
    if len(argv) != 2:
        if iter_no == 0: print_on_screen('Usages:\n%s <configuration config_filename>' %os.path.split(argv[0])[-1])
        exit(os.EX_NOINPUT)

    # read the configuration file and check if required information is provided into the file
    filename = argv[1]
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()):
        if iter_no == 0: print_on_screen('Error!! Configuration file could not be read successfully. Check configuration file: %s.' % filename)
        exit(os.EX_DATAERR)

    # step-x.x: calculate (seasonal) summary statistics from the observables
    if iter_no == 0:
        filename = config.summary_statistics_filename
        headers = ['iter_num', 'variable',
                   'avg_yr_mean', '10p_yr_mean', 'qr1_yr_mean', 'mdn_yr_mean', 'qr3_yr_mean', '90p_yr_mean', 'std_yr_mean', 'min_yr_mean', 'max_yr_mean', 'rng_yr_mean',
                   'avg_yr_stdv', '10p_yr_stdv', 'qr1_yr_stdv', 'mdn_yr_stdv', 'qr3_yr_stdv', '90p_yr_stdv', 'std_yr_stdv', 'min_yr_stdv', 'max_yr_stdv', 'rng_yr_stdv',
                   'avg_yr_peak', '10p_yr_peak', 'qr1_yr_peak', 'mdn_yr_peak', 'qr3_yr_peak', '90p_yr_peak', 'std_yr_peak', 'min_yr_peak', 'max_yr_peak', 'rng_yr_peak',
                   'avg_yr_pmon', '10p_yr_pmon', 'qr1_yr_pmon', 'mdn_yr_pmon', 'qr3_yr_pmon', '90p_yr_pmon', 'std_yr_pmon', 'min_yr_pmon', 'max_yr_pmon', 'rng_yr_pmon',
                   'avg_yr_btom', '10p_yr_btom', 'qr1_yr_btom', 'mdn_yr_btom', 'qr3_yr_btom', '90p_yr_btom', 'std_yr_btom', 'min_yr_btom', 'max_yr_btom', 'rng_yr_btom',
                   'avg_yr_bmon', '10p_yr_bmon', 'qr1_yr_bmon', 'mdn_yr_bmon', 'qr3_yr_bmon', '90p_yr_bmon', 'std_yr_bmon', 'min_yr_bmon', 'max_yr_bmon', 'rng_yr_bmon',
                   'avg_yr_ampt', '10p_yr_ampt', 'qr1_yr_ampt', 'mdn_yr_ampt', 'qr3_yr_ampt', '90p_yr_ampt', 'std_yr_ampt', 'min_yr_ampt', 'max_yr_ampt', 'rng_yr_ampt',
                   'jan_mean', 'jan_median', 'jan_std', 'jan_min', 'jan_max', 'jan_range', 'feb_mean', 'feb_median', 'feb_std', 'feb_min', 'feb_max', 'feb_range',
                   'mar_mean', 'mar_median', 'mar_std', 'mar_min', 'mar_max', 'mar_range', 'apr_mean', 'apr_median', 'apr_std', 'apr_min', 'apr_max', 'apr_range',
                   'may_mean', 'may_median', 'may_std', 'may_min', 'may_max', 'may_range', 'jun_mean', 'jun_median', 'jun_std', 'jun_min', 'jun_max', 'jun_range',
                   'jul_mean', 'jul_median', 'jul_std', 'jul_min', 'jul_max', 'jul_range', 'aug_mean', 'aug_median', 'aug_std', 'aug_min', 'aug_max', 'aug_range',
                   'sep_mean', 'sep_median', 'sep_std', 'sep_min', 'sep_max', 'sep_range', 'oct_mean', 'oct_median', 'oct_std', 'oct_min', 'oct_max', 'oct_range',
                   'nov_mean', 'nov_median', 'nov_std', 'nov_min', 'nov_max', 'nov_range', 'dec_mean', 'dec_median', 'dec_std', 'dec_min', 'dec_max', 'dec_range']

        lines = [','.join(headers)]
        print_on_file(lines, filename, '_STAT_SUMMARY.LOCK', sleep_time=0.2)

        lines = []
        for var in config.obs_variables:
            var_name = var.varname
            data = [-1, var_name]
            snames, result = SeasonalStatistics.seasonal_summary(var.data_cloud)
            if result:
                for key in result.keys(): data += list(result[key])

            snames, result = SeasonalStatistics.monthly_summary(var.data_cloud)
            if result:
                for key in result.keys(): data += list(result[key])
            lines.append(','.join(str(x) for x in data))

        if lines: print_on_file(lines, filename, '_STAT_SUMMARY.LOCK', sleep_time=0.2)
    # end of step-x.x


    # continue iterating following steps until the last sample is being processed
    if iter_no == 0: print_on_screen('Sample processing [begin]')

    iter_limit = len(config.samples)
    
    while iter_no < iter_limit:
        # process current sample
        print_on_screen('\tProcessing of sample no. %d has been started.' % iter_no)
        temp_bool = process_parameter_sample(config, iter_no)

        # break the sample processing if iter no is more than the sample size
        # if iter_no >= iter_limit: break

        # read current iteration number
        while True:
            iter_no = read_iter_number()    # starts from zero
            if iter_no >= 0: break

    if iter_no == (iter_limit):
        print_on_screen('Sample processing [end]')
        print_on_screen('The process has been successfully completed.')
    exit(os.EX_OK)

if __name__ == '__main__': main(sys.argv)
