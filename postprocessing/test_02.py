__author__ = 'mhasan'

import sys,os
import numpy as np
print( os.path.abspath(os.curdir))
sys.path.append('..')
from utilities.grid import grid
from utilities.upstream import Upstream
from utilities.station import Station
from calibration.variable import SimVariable
from calibration.wgapoutput import WGapOutput
from calibration.enums import FileEndian
print( os.path.abspath(os.curdir))
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP

filename_config = 'ganges_configuration_km3_test.txt'
print( os.path.abspath(os.curdir))
config = Configuration.read_configuration_file(filename_config)

succeed = False
if config and config.is_okay() and WaterGAP and WaterGAP.is_okay(): succeed = True

if succeed: succeed = WaterGAP.read_predictions(config.sim_variables)

if succeed:
    for var in config.sim_variables:
        if var.data_cloud:
            config_filename = 'output/test_' + var.varname + '.csv'
            succeed = var.data_cloud.print_data(config_filename)
        if not succeed: break

print(succeed)

#
# print(len(config.sim_variables[1].cell_groups))
#
#
# config_filename = '../wgap_home/OUTPUT/G_TOTAL_STORAGES_km3_2002.12.UNF0'
# d = WGapOutput.read_unf(config_filename, file_endian=FileEndian.big_endian)
# d = WGapOutput.summarize(d, basin=config.sim_variables[1].cell_groups[0])
# # for i in range(len(d)): print(d[i]/len(config.sim_variables[1].cell_groups[0]))
# print(d)