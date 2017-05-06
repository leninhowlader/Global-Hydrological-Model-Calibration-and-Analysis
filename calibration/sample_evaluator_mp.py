#!/usr/bin/python3

__author__ = 'mhasan'

import os, sys
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.variable import SimVariable, ObsVariable
from calibration.predstat import SeasonalStatistics
from calibration.watergap import WaterGAP
from utilities.fileio import *
from mpi4py import MPI
from copy import deepcopy

def read_iter_number():
    iter_no = 0
    lockname = '_ITER.LOCK'
    fd = open(lockname, 'w')
    if acquire_lock(fd):

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

        release_lock(fd)
    else: iter_no = -9999

    return iter_no

def process_parameter_sample(config, iter_no):
    arguments = {}

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
    log_file = os.path.join(WaterGAP.home_directory, 'log', 'run' + pfix + '.log')
    if not WaterGAP.execute_model(arguments, log_file=log_file):
        WaterGAP.remove_files(arguments)
        return False

    # read model output
    sim_vars, obs_vars = deepcopy(config.sim_variables), config.obs_variables
    if not WaterGAP.read_predictions(sim_vars):
        WaterGAP.remove_files()
        return False

    # step-x.x: calculate prediction summaries
    # ------- begin of step-x.x -------
    # note: statistics will be generation with actual data (i.e. no anomalies will be included)
    lines, separator = [], ','
    if config.prediction_statistics:
        filename = config.summary_statistics_filename
        for var in config.sim_variables:
            var_name = 'sim_%s'%var.varname.lower()
            data = [iter_no, var_name]
            snames, results = SeasonalStatistics.seasonal_summary(var.data_cloud)
            if results:
                for key in results.keys(): data += list(results[key])

            snames, results = SeasonalStatistics.monthly_summary(var.data_cloud)
            if results:
                for key in results.keys(): data += list(results[key])

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
    efficiencies = WaterGAP.prediction_efficiency(sim_vars, obs_vars)

    lines = []
    for key in efficiencies.keys():
        lines.append(separator.join(map(str, [iter_no, key, efficiencies[key]])))
    if lines: print_on_file(lines, config.prediction_efficiency_filename, '__PREDEFF.LOCK', sleep_time=0.1)
    # ------ end of step-x.x --------

    # remove files
    WaterGAP.remove_files()

    # return increment_done_count()
    return True

def main(argv):
    # ------------------------------------------------------------------------------------------------------------------
    # step-01: initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # check program arguments
    # this program needs one argument as the address of configuration file
    if len(argv) != 2:
        if rank == 0: print_on_screen('Usages:\n%s <configuration config_filename>' %os.path.split(argv[0])[-1])
        exit(os.EX_NOINPUT)

    # read the configuration file and check if required information is provided into the file
    filename = argv[1]
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()):
        if rank == 0: print_on_screen('(Error) Configuration file could not be read successfully. Check %s.' % filename)
        exit(os.EX_DATAERR)

    # step-x.x: calculate (seasonal) summary statistics from the observables
    if rank == 0:
        filename = config.summary_statistics_filename
        headers = ['iter_num', 'variable', 'average_seasonal_mean', '50pr_seasonal_mean', '75pr_seasonal_mean', '80pr_seasonal_mean', '90pr_seasonal_mean',
                   'stddev_seasonal_mean', 'min_seasonal_mean', 'max_seasonal_mean', 'range_seasonal_mean',
                   'average_seasonal_deviation', '50pr_seasonal_deviation', '75pr_seasonal_deviation', '80pr_seasonal_deviation', '90pr_seasonal_deviation',
                   'stddev_seasonal_deviation', 'min_seasonal_deviation', 'max_seasonal_deviation', 'range_seasonal_deviation',
                   'average_seasonal_peak', '50pr_seasonal_peak', '75pr_seasonal_peak', '80pr_seasonal_peak', '90pr_seasonal_peak',
                   'stddev_seasonal_peak', 'min_seasonal_peak', 'max_seasonal_peak', 'range_seasonal_peak',
                   'average_peak_period', '50pr_peak_period', '75pr_peak_period', '80pr_peak_period', '90pr_peak_period',
                   'stddev_peak_period', 'min_peak_period', 'max_peak_period', 'range_peak_period',
                   'average_seasonal_bottom', '50pr_seasonal_bottom', '75pr_seasonal_bottom', '80pr_seasonal_bottom', '90pr_seasonal_bottom',
                   'stddev_seasonal_bottom', 'min_seasonal_bottom', 'max_seasonal_bottom', 'range_seasonal_bottom',
                   'average_bottom_period', '50pr_bottom_period', '75pr_bottom_period', '80pr_bottom_period', '90pr_bottom_period',
                   'stddev_bottom_period', 'min_bottom_period', 'max_bottom_period', 'range_bottom_period',
                   'average_seasonal_amplitude', '50pr_seasonal_amplitude', '75pr_seasonal_amplitude', '80pr_seasonal_amplitude', '90pr_seasonal_amplitude',
                   'stddev_seasonal_amplitude', 'min_seasonal_amplitude', 'max_seasonal_amplitude', 'range_seasonal_amplitude',
                   'jan_mean', 'jan_stddev', 'jan_min', 'jan_max', 'jan_range', 'feb_mean', 'feb_stddev', 'feb_min', 'feb_max', 'feb_range',
                   'mar_mean', 'mar_stddev', 'mar_min', 'mar_max', 'mar_range', 'apr_mean', 'apr_stddev', 'apr_min', 'apr_max', 'apr_range',
                   'may_mean', 'may_stddev', 'may_min', 'may_max', 'may_range', 'jun_mean', 'jun_stddev', 'jun_min', 'jun_max', 'jun_range',
                   'jul_mean', 'jul_stddev', 'jul_min', 'jul_max', 'jul_range', 'aug_mean', 'aug_stddev', 'aug_min', 'aug_max', 'aug_range',
                   'sep_mean', 'sep_stddev', 'sep_min', 'sep_max', 'sep_range', 'oct_mean', 'oct_stddev', 'oct_min', 'oct_max', 'oct_range',
                   'nov_mean', 'nov_stddev', 'nov_min', 'nov_max', 'nov_range', 'dec_mean', 'dec_stddev', 'dec_min', 'dec_max', 'dec_range']
        lines = [','.join(headers)]
        print_on_file(lines, filename, '_STAT_SUMMARY.LOCK', sleep_time=0.2)

        lines = []
        for var in config.obs_variables:
            var_name = 'obs_%s' % var.varname.lower()
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
    if rank == 0: print_on_screen('Sample processing [begin]')
    while True:
        # read current iteration number
        iter_no = -9999
        while True:
            iter_no = read_iter_number()    # starts from zero
            if iter_no >= 0: break

        # break the sample processing if iter no is more than the sample size
        if iter_no >= len(config.samples): break

        # process current sample
        print_on_screen('\tProcessing of sample no. %d has been started.' %iter_no)
        # temp_bool = process_parameter_sample(config, iter_no)

    if rank == 0:
        if rank == 0: print_on_screen('Sample processing [end]')
        print_on_screen('The process has been successfully completed.')
        exit(os.EX_OK)

main(sys.argv)
