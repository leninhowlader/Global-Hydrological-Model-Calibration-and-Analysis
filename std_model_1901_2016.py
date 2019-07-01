#!/usr/local/Python-3.5.2/bin/python3
__author__ = 'mhasan'

import os, sys
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP


def main(argv):
    # step: check program arguments. configuration file must be provided as system argument
    if len(argv) != 2:
        print('Usages:\n%s <configuration config_filename>' %os.path.split(argv[0])[-1])
        return -1

    # step: read the configuration file and check if required information is provided into the file
    filename = argv[1]
    config = Configuration.read_configuration_file(filename)
    if not (config.is_okay() and WaterGAP.is_okay()):
        print('Error!! Configuration file could not be read successfully. Check configuration file: %s.' % filename)
        return -2

    # read standard model output
    dumping_directory = config.output_directory
    output_directory_name = os.path.join(WaterGAP.home_directory, 'OUTPUT')
    attribs = []
    for var in config.sim_variables:
        succeed = var.dump_time_series_from_model_prediction(WaterGAP.start_year, WaterGAP.end_year, additional_attributes=attribs,
                                                             prediction_directory=output_directory_name, dumping_directory=dumping_directory)
        if not succeed: return -3

    print('Standard Model Output was read and stored successfully.')
    return 0

if __name__ == '__main__': main(sys.argv)
