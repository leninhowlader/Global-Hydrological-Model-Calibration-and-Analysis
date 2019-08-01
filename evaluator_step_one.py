#!/usr/local/Python-3.5.2/bin/python3
__author__ = 'mhasan'

import os, sys
# sys.path.append('..')
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP
from utilities.fileio import *
from collections import OrderedDict

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
    '''
    This function takes a sample of a given id as iter_no and sets the corresponding sample parameter values
    in the model input parameter file. Then it executes the model. When the model completes its run successfully
    the function reads the model output and computes necessary calculation using the model predictions.
    Finally, the summarized output is stored in a predefined file.

    :param config: (Configuration) configuration object. The config object contains all required information
                    about how to run the model, which parameters to modify, which output files to be read in
                    and what statistical calculation to be made etc
    :param iter_no: (int) iteration number. the iteration number serves as the sample number in effect
    :return: (bool) on successful operation it returns True,
                    False otherwise.
    '''
    arguments = OrderedDict()

    # step: collect parameter values from sample
    params = config.samples[iter_no]

    # step: update parameter values
    if len(params) == len(config.parameters):
        for i in range(len(params)): config.parameters[i].parameter_value = params[i]
    else: return False

    # step: write new parameter file with update parameter values
    pfix = str(iter_no).rjust(6, '0')
    filename = 'parameters_' + pfix + '.json'
    if not WaterGAP.update_parameter_file(config.parameters, filename): return False
    arguments['p'] = filename

    # step: create output output_directory and output_directory file
    output_dir = 'output_' + pfix
    dir_filename = 'data_' + pfix + '.dir'
    if not WaterGAP.update_directory_info(output_dir, dir_filename): return False
    arguments['d'] = dir_filename

    # step: execute model with new parameters
    log_file = '/dev/null' # os.path.join(WaterGAP.home_directory, 'log', 'run' + pfix + '.log')
    if not WaterGAP.execute_model(arguments, log_file=log_file):
        WaterGAP.remove_files(arguments)
        return False

    # step: read the model output and dump the prediction summary
    succeed = True
    dumping_directory = config.output_directory
    output_directory_name = os.path.join(WaterGAP.home_directory, WaterGAP.dir_info.output_directory)
    attribs = [iter_no]
    for var in config.sim_variables:
        succeed = var.dump_time_series_from_model_prediction(WaterGAP.start_year, WaterGAP.end_year, additional_attributes=attribs,
                                                             prediction_directory=output_directory_name, dumping_directory=dumping_directory)
        if not succeed: break

    # step: remove model output files
    WaterGAP.remove_files(arguments)

    return succeed

def main(argv):
    # step: read iteration number; the first iteration number will be considered as the processor node number
    node_id = -9999
    while True:
        node_id = read_iter_number()    # starts from zero
        if node_id >= 0: break

    # step: check program arguments. configuration file must be provided as system argument
    if len(argv) != 2:
        if node_id == 0: print_on_screen('Usages:\n%s <configuration config_filename>' %os.path.split(argv[0])[-1])
        exit(os.EX_NOINPUT)

    # step: read the configuration file and check if required information is provided into the file
    filename = argv[1]
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()):
        if node_id == 0: print_on_screen('Error!! Configuration file could not be read successfully. Check configuration file: %s.' % filename)
        exit(os.EX_DATAERR)

    # step: continue iteration until iter_no reaches iter_limit
    sample_no = node_id
    iter_limit = len(config.samples)
    while sample_no < iter_limit:
        # step: process the current sample
        print_on_screen('\tSample no. %d is being processed on Computer Node No. %d.' % (sample_no, node_id))
        succeed = process_parameter_sample(config, sample_no)

        # read current iteration number
        while True:
            sample_no = read_iter_number()    # starts from zero
            if sample_no >= 0: break

    if sample_no == (iter_limit):
        print_on_screen('Sample processing [end]')
        print_on_screen('The process has been successfully completed.')
    exit(os.EX_OK)

if __name__ == '__main__': main(sys.argv)
