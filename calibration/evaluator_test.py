#!/usr/bin/python3
__author__ = 'mhasan'

import os, sys
sys.path.append('..')
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP
from utilities.fileio import FileInputOutput as io
from copy import deepcopy
from datetime import datetime


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

def increment_done_count():
    succeed = True

    lockname = '_DONE.LOCK'
    fd = open(lockname, 'w')
    if io.acquire_lock(fd):
        done_count = 0
        f = None
        try:
            f = open('_DONE.COUNT', 'r')
            temp = f.readline().strip()
            done_count = int(temp)
        except: pass
        finally:
            try: f.close()
            except: pass

        if done_count >= 0:
            try:
                f = open('_DONE.COUNT', 'w')
                f.write(str(done_count + 1))
            except: succeed = False
            finally:
                try: f.close()
                except: pass
        io.release_lock(fd)
    else: succeed = False

    return succeed

def read_done_count():
    done_count = 0
    lockname = '_DONE.LOCK'
    fd = open(lockname, 'w')
    if io.acquire_lock(fd):
        f = None
        try:
            f = open('_DONE.COUNT', 'r')
            temp = f.readline().strip()
            done_count = int(temp)
        except: pass
        finally:
            try: f.close()
            except: pass
        io.release_lock(fd)
    else: done_count = -9999

    return done_count

def process_parameter_sample(config, iter_no=0, execute_model=False):
    arguments = {}

    if execute_model:
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
            WaterGAP.remove_files()
            return False

    # read model output
    sim_vars, obs_vars = deepcopy(config.sim_variables), config.obs_variables
    if not WaterGAP.read_predictions(sim_vars):
        WaterGAP.remove_files()
        return False

    # calculate prediction statistics
    # note: statistics will be generation with actual data (i.e. no anomalies will be included)
    lines, separator = [], '\t'
    if config.prediction_statistics:
        funs = ['mean', 'std', 'min', 'max', 'q1', 'median', 'q3']
        pred_stat, month_stat, year_stat = WaterGAP.prediction_statistics(sim_vars, funs=funs)

        # writing basic prediction statistics
        lines = []
        for key in pred_stat.keys():
            for v in pred_stat[key]: lines.append(separator.join(map(str, [iter_no, key] + v)))
        if lines: io.print_on_file(lines, config.prediction_summary_filename, '_STAT_OS.LOCK', sleep_time=0.3)

        lines = []
        for key in month_stat.keys():
            var_stat = month_stat[key]
            for vk in var_stat.keys(): lines.append(separator.join(map(str, [iter_no, key, separator.join(map(str, vk))] + var_stat[vk])))
        if lines: io.print_on_file(lines, config.monthly_prediction_summary_filename, '_STAT_MS.LOCK', sleep_time=0.5)

        lines = []
        for key in year_stat.keys():
            var_stat = year_stat[key]
            for vk in var_stat.keys(): lines.append(separator.join(map(str, [iter_no, key, separator.join(map(str, vk))] + var_stat[vk])))
        if lines: io.print_on_file(lines, config.yearly_prediction_summary_filename, '_STAT_YS.LOCK', sleep_time=0.5)

    # calculate efficiencies
    for var in sim_vars: var.compute_anomalies()

    der_vars = deepcopy(config.derived_variables)
    if der_vars:
        for var in der_vars:
            var.derive_data(simvars=sim_vars, obsvars=obs_vars)
            sim_vars.append(var)

    for var in sim_vars:
        if var.varname == 'discharge_km3pm':
            var.data_cloud.print_data('test_discharge_sim.txt')

    for var in obs_vars:
        if var.varname == 'discharge':
            var.data_cloud.print_data('test_discharge_obs.txt')

    efficiencies = WaterGAP.prediction_efficiency(sim_vars, obs_vars)

    lines = []
    for key in efficiencies.keys():
        lines.append(separator.join(map(str, [iter_no, key, efficiencies[key]])))
        print(separator.join(map(str, [iter_no, key, efficiencies[key]])))
    if lines:
        io.print_on_file(lines, config.prediction_efficiency_filename, '__PREDEFF.LOCK', sleep_time=0.1)


    # remove files
    if execute_model: WaterGAP.remove_files()

    # return increment_done_count()
    return True

def main(argv):
    a = datetime.now()
    print(a)
    if len(argv) != 2:
        io.print_on_screen('Usages:\n%s <configuration config_filename>' %os.path.split(argv[0])[-1])
        exit(os.EX_NOINPUT)

    # read configuration file
    filename = argv[1]
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()):
        io.print_on_screen('(Error) Configuration file could not be read successfully. Check %s.' % filename)
        exit(os.EX_DATAERR)

    # print(config.prediction_efficiency_filename)
    # i = 1
    # for var in config.obs_variables:
    #     # var = ObsVariable()
    #     if var.varname == 'discharge':
    #         var.data_cloud.print_data('test_discharge_obs.csv', append=False, separator=',')
    #         exit(0)
    #
    #     print(i, var.varname, var.counter_variable, end='', flush=True)
    #     for simvar in config.sim_variables+config.derived_variables:
    #         if simvar.varname == var.counter_variable:
    #             print(' exists')
    #             break
    #
    #     i += 1
    #
    # exit((os.EX_OK))
    succeed = process_parameter_sample(config, execute_model=False, iter_no=5)

    if succeed:
        io.print_on_screen('The process has been successfully completed.')
        b = datetime.now()
        print(b)
        print((b-a).seconds)
        exit(os.EX_OK)
    else: io.print_on_screen('The evaluation was not successful!!')
    exit(os.EX_CONFIG)

main(sys.argv)
