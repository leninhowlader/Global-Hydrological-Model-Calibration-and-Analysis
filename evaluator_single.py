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
    sample_no = -1

    if len(argv) >= 3:
        filename = argv[1]
        try: sample_no = int(argv[2])
        except: pass

    if sample_no == -1: exit(os.EX_DATAERR)

    # step: read the configuration file and check if required information is
    # provided into the file
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()): exit(os.EX_DATAERR)

    # step: continue iteration until iter_no reaches iter_limit
    succeed = evaluate_sample(config, sample_no, 1001)

    exit(os.EX_OK)

if __name__ == '__main__': main(sys.argv)
