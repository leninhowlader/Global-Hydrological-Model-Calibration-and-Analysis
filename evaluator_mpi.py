#!/usr/local/Python-3.5.2/bin/python3
__author__ = 'mhasan'

import os, sys
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP
from utilities.fileio import FileInputOutput as io
from analyses.sensitivity import SensitivityAnalysis

evaluate_sample = SensitivityAnalysis.SampleEvaluation.evaluate_sample

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

    sample_size = len(config.samples)
    samples_per_node = sample_size//world_size
    start_index = world_rank * samples_per_node
    end_index = start_index + samples_per_node
    if world_rank == (world_size - 1): end_index = sample_size

    message = 'Node %d will process sample no. %d-%d' % (world_rank, start_index,
                                                         end_index - 1)
    io.print_on_screen(message)

    # step: continue iteration until iter_no reaches iter_limit
    sample_no = -1
    for sample_no in range(start_index, end_index):
    # while sample_no < end_index:
        # step: process the current sample
        message = ('\tSample no. %d is being processed on Computer Node No. %d.'
                   % (sample_no, world_rank))
        io.print_on_screen(message)
        succeed = evaluate_sample(config, sample_no, world_rank)

    if world_rank == (world_size - 1) and sample_no == (sample_size - 1):
        io.print_on_screen('Sample processing [end]')
        io.print_on_screen('The process has been successfully completed.')
    exit(os.EX_OK)

if __name__ == '__main__': main(sys.argv)
