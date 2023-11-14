#!/usr/local/Python-3.5.2/bin/python3
__author__ = 'mhasan'

import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'

import numpy as np
from core.configuration import Configuration
from wgap.watergap import WaterGAP
from wgap.wgapio import WaterGapIO
from utilities.fileio import FileInputOutput as io
from analyses.sensitivity import SensitivityAnalysis
from core.stats import stats

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
                                        world_rank, start_index, end_index)
        io.print_on_screen(message)
    else:
        message = 'Node %d will not process any sample.' % world_rank
        io.print_on_screen(message)
        exit(os.EX_OK)
    # end [step]


    # step: run reference-run when necessary
    reference_predictions = {}
    M = len(config.parameters)  # no. of parameters

    if config.experiment_type == 'sensitivity' and (
        config.sensitivity_as_change_in_simulation or
        len(config.obs_variables) == 0):

        if start_index%(M+1) != 0:
            ref_sample_no = (start_index//(M+1))*(M+1)

            succeed = run_model(
                config=config,
                sample_id=ref_sample_no,
                additional_filename_specifier='%s_ref_%d'%(
                                    config.experiment_name.lower(),world_rank)
            )

            if not succeed:
                message = 'Samples %d-%d of rank %d could not be run'%(
                    start_index, end_index, world_rank
                )
                io.print_on_screen(message)
                exit(os.EX_OSERR)

            for var in config.sim_variables:
                # compute spatial scale summary
                succeed = var.aggregate_prediction_at_spatial_scale()

                # compute anomaly
                succeed = var.do_anomaly_computation()

                reference_predictions[var.varname] = {
                    'data': var.data_cloud.data.copy(),
                    'indices': var.data_cloud.data_indices.copy()
                }
    # end [step]


    # step: run model using sample numbers within start index and end index
    # and compute fx
    sample_no = -1
    for sample_no in range(start_index, end_index+1):
        if sample_no % (M + 1) == 0: reference_predictions = {}

        message = ('\tSample no. %d is being processed on Computer Node No. %d.'
                   % (sample_no, world_rank))
        io.print_on_screen(message)

        succeed = run_model(
                    config=config,
                    sample_id=sample_no,
                    additional_filename_specifier=config.experiment_name.lower()
        )

        if not succeed:
            message = 'Samples %d-%d of rank %d could not be run' % (
                sample_no, end_index, world_rank
            )
            io.print_on_screen(message)
            exit(os.EX_OSERR)

        for var in config.sim_variables:
            # compute spatial scale summary
            succeed = var.aggregate_prediction_at_spatial_scale()

            # compute anomaly
            succeed = var.do_anomaly_computation()

            # dump predictions
            if config.dump_simulation_timeseries:
                # for both basin and cell scale variables the method of dumping 
                # simulation values is the same
                succeed = var.dump_data_into_binary_file(
                    directory_out=config.output_directory,
                    additional_filename_identifier=str(world_rank),
                    additional_attributes=[sample_no]
                )

            if config.experiment_type == 'sensitivity':
                # compute fx
                if config.sensitivity_as_change_in_simulation:
                    fun = config.function_to_measure_the_change
                    if not fun: fun = stats.root_mean_square_error

                    data_curr = var.data_cloud.data
                    indicies_curr = var.data_cloud.data_indices

                    ncol = data_curr.shape[1]
                    fx = [0] * ncol

                    if sample_no % (M + 1) == 0:
                        reference_predictions[var.varname] = {
                            'data': data_curr.copy(),
                            'indices': indicies_curr.copy()
                        }
                    else:
                        data_ref = reference_predictions[var.varname]['data']
                        indices_ref = reference_predictions[var.varname]['indices']

                        if (data_ref.shape == data_curr.shape and
                            indices_ref.shape == indicies_curr.shape and
                            np.abs(indices_ref-indicies_curr).sum() == 0):

                            for i in range(ncol):
                                fx[i] = fun(data_curr[:,i], data_ref[:,i])

                    # step: dump fx into binary file
                    fx = np.array([sample_no] + fx) # add sample number
                    f_out = 'fx_%s_%d.%d.unf0'%(
                        var.varname.lower(), world_rank, ncol + 1
                    )
                    f_out = os.path.join(config.output_directory, f_out)

                    succeed = WaterGapIO.write_unf(f_out, fx, append=True)
                    # end of step

                elif len(config.obs_variables) > 1: pass # sub-section to be added
                else: break
    # end [step]

    if world_rank == (world_size - 1) and sample_no == (sample_size - 1):
        io.print_on_screen('Sample processing [end]')
        io.print_on_screen('The process has been successfully completed.')
    exit(os.EX_OK)

if __name__ == '__main__': main(sys.argv)
