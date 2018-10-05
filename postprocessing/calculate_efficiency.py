#!/usr/local/Python-2.7.3/bin/python

__author__ = 'mhasan'

import os, sys
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.variable import SimVariable, ObsVariable, DerivedVariable
from calibration.predstat import SeasonalStatistics
from calibration.watergap import WaterGAP
from utilities.fileio import *
# from mpi4py import MPI
from copy import deepcopy

config_filename = 'input/Config_BRH_Efficiency.txt'
# output_directory = '/media/sf_private/FINAL_CALIBRATION/Predictions/B2C06'
output_directory = 'B2C04'

def main():
    global  config_filename, output_directory

    succeed = False; config = None; vars = None

    if config_filename:
        print('reading configuration file ..', end='', flush=True)
        config = Configuration.read_configuration_file(config_filename)
        if config.is_okay():
            succeed = True
            print('[done]')
        else: print('[failed]')

    #if 1: print(config.derived_variables[0].varname); exit()

    if succeed and config.sim_variables:
        # read predictions
        print('reading model predictions ..', end='', flush=True)
        succeed = WaterGAP.read_predictions(config.sim_variables, output_directory_name=output_directory)
        if succeed: print('[done]')
        else: print('[failed]')

        # compute anomalies
        for var in config.sim_variables: var.compute_anomalies()

    if succeed and config.derived_variables:
        # compute derived variables
        for var in config.derived_variables:
            var.derive_data(simvars=config.sim_variables, obsvars=config.obs_variables)

    # svars = config.sim_variables + config.derived_variables
    # ovars = config.obs_variables
    # results = WaterGAP.prediction_efficiency(sim_vars=svars, obs_vars=ovars)


    # output_filename = 'output/efficiencies.csv'
    # headers = ['cid', 'obs_var', 'sim_var', 'sse', 'mse', 'rmse', 'mae', 'mape', 'pbias', 'rsr', 'r', 'r2', 'ioa', 'nse', 'kge']
    # data = []
    #
    cal_identifier = output_directory.split('/')[-1]
    # for d in results:
    #     d[0] = cal_identifier
    #     data.append(d)
    # write_flat_file(output_filename, data, separator=',', append=True)

    # writing predictions
    filename = '/media/sf_private/FINAL_CALIBRATION/Predictions/' + cal_identifier + 'P/' + cal_identifier + '_'
    for var in config.sim_variables:
        print('saving "%s" data ..' % var.varname, end='', flush=True)
        fname = filename + var.varname + '.csv'
        var.data_cloud.sort()
        succeed = var.data_cloud.print_data(fname, append=True, separator=',')
        if succeed: print('[done]')
        else: print('[failed]')

    for var in config.derived_variables:
        print('saving "%s" data ..' % var.varname, end='', flush=True)
        var.derive_data(simvars=config.sim_variables)
        fname = filename + var.varname + '.csv'
        var.data_cloud.sort()
        succeed = var.data_cloud.print_data(fname, append=True, separator=',')
        if succeed: print('[done]')
        else: print('[failed]')

    if succeed: print('Mission Accomplished :)')
    else: print('Mission Failed!!')

if __name__ == '__main__': main()
