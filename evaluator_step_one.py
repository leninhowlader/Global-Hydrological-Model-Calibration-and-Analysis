#!/usr/local/Python-3.5.2/bin/python3
__author__ = 'mhasan'

import os, sys
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP
from utilities.fileio import FileInputOutput as io
from analyses.sensitivity import SensitivityAnalysis

evaluate_sample = SensitivityAnalysis.SampleEval_ModelRun.evaluate_sample

def main(argv):
    # step: read iteration number; the first iteration number will be considered
    # as the processor node number
    iteration_lock = '_iteration'
    node_id = -9999
    while True:
        node_id = io.readwrite_unique_id(iteration_lock)    # starts from zero
        if node_id >= 0: break

    # step: check program arguments. configuration file must be provided as
    # system argument
    if len(argv) != 2:
        if node_id == 0:
            message = ('Usages:\n%s <configuration config_filename>'
                       % os.path.split(argv[0])[-1])
            io.print_on_screen(message)
        exit(os.EX_NOINPUT)

    # step: read the configuration file and check if required information is
    # provided into the file
    filename = argv[1]
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()):
        if node_id == 0:
            message = ('Error!! Configuration file could not be read ' +
                       'successfully. Check configuration file: %s.' % filename)
            io.print_on_screen(message)
        exit(os.EX_DATAERR)

    # step: continue iteration until iter_no reaches iter_limit
    sample_no = node_id
    iter_limit = len(config.samples)
    while sample_no < iter_limit:
        # step: process the current sample
        message = ('\tSample no. %d is being processed on Computer Node No. %d.'
                   % (sample_no, node_id))
        io.print_on_screen(message)
        succeed = evaluate_sample(config, sample_no, node_id)

        # read current iteration number
        while True:
            sample_no = io.readwrite_unique_id(iteration_lock)
            if sample_no >= 0: break

    if sample_no == (iter_limit):
        io.print_on_screen('Sample processing [end]')
        io.print_on_screen('The process has been successfully completed.')
    exit(os.EX_OK)

if __name__ == '__main__': main(sys.argv)
