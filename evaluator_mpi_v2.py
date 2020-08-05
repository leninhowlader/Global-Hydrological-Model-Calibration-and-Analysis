#!/usr/local/Python-3.5.2/bin/python3
__author__ = 'mhasan'

import os, sys
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP
from utilities.fileio import FileInputOutput as io
from analyses.sensitivity import SensitivityAnalysis

evaluate_sample = SensitivityAnalysis.SampleEvaluation.evaluate_sample
run_model = SensitivityAnalysis.SampleEvaluation.run_model

def get_start_end_index(world_rank, world_size, sample_size):
    x1 = sample_size % world_size
    x2 = sample_size // world_size

    if x1 != 0:
        if world_rank < x1:
            start_index = world_rank * x2 + world_rank
        else:
            start_index = world_rank * x2 + x1
    else:
        start_index = world_rank * x2

    end_index = start_index + x2 - 1
    if world_rank < x1: end_index += 1

    return start_index, end_index

def main(argv):


    # read node id (rank) and number of nodes (world size) from system
    # arguments
    filename = ''
    world_rank, world_size = -1, -1
    if len(argv) >= 4:

        filename = argv[1]
        try:
            world_size = int(argv[2])
            world_rank = int(argv[3])
        except: pass

    if not os.path.exists(filename):
        message = 'Configuration file does not exist!'
        io.print_on_screen(message)
        exit(os.EX_NOINPUT)
    elif world_rank == -1 or world_size == -1:
        message = 'Rank and communicator size could not be retrieved!!'
        io.print_on_screen(message)
        exit(os.EX_NOINPUT)

    # step: read the configuration file and check if required information is
    # provided into the file
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()):
        if world_rank == 0:
            message = ('Error!! Configuration file could not be read ' +
                       'successfully. Check configuration file: %s.' % filename)
            io.print_on_screen(message)
        exit(os.EX_DATAERR)

    # step: compute start and end indices
    sample_size = len(config.samples)
    start_index, end_index = get_start_end_index(
        world_rank=world_rank, world_size=world_size, sample_size=sample_size
    )

    if start_index <= end_index:
        message = 'Node %d will process sample no. %d-%d' % (
                                        world_rank, start_index, end_index - 1)
        io.print_on_screen(message)
    else:
        message = 'Node %d will not process any sample.' % world_rank
        io.print_on_screen(message)
        exit(os.EX_OK)
    # end [step]


    # step: run reference-run when necessary
    reference_predictions = {}
    M = len(config.parameters)          # no. of parameters

    if start_index%(M+1) != 0:
        ref_sample_no = (start_index//(M+1))*(M+1)
        succeed = run_model(
            config=config,
            sample_id=ref_sample_no,
            additional_filename_specifier='ref' + str(world_rank)
        )

        for var in config.sim_variables:
            reference_predictions[var.varname] = var.prediction_time_series.copy()
    # end [step]


    # step: run model using sample numbers within start index and end index
    # and compute fx
    sample_no = -1
    for sample_no in range(start_index, end_index+1):
        message = ('\tSample no. %d is being processed on Computer Node No. %d.'
                   % (sample_no, world_rank))
        io.print_on_screen(message)
        succeed = run_model(
            config=config,
            sample_id=sample_no
        )

        if not succeed: break

        for var in config.sim_variables:
            # from cell time-series compute basin time-series
            # compute anomaly
            # dump predictions
            # compute fx

            if config.dump_model_prediction:
                # dump prediction in suitable manner
                pass


            if sample_no % (M + 1) == 0:
                reference_predictions[var.varname] = \
                var.prediction_time_series.copy()

                # append fx=0 into output file
            else:
                # compute fx
                # append fx into output file
                pass
    # end [step]

    if world_rank == (world_size - 1) and sample_no == (sample_size - 1):
        io.print_on_screen('Sample processing [end]')
        io.print_on_screen('The process has been successfully completed.')
    exit(os.EX_OK)

if __name__ == '__main__': main(sys.argv)
