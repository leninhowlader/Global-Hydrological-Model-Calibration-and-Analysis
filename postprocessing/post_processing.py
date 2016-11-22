
import sys
sys.path.append('..')
from postprocessing.borgoutput import BorgOutput
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP


import numpy as np
from datetime import datetime


config_filename = 'ganges_configuration.txt'
config = Configuration.read_configuration_file(config_filename)
tmp = config.is_okay()
tmp = WaterGAP.is_okay()

borg_output_filename = 'results.dat'

nobj = 2
results = BorgOutput.read_borg_output(borg_output_filename)
pset, ndx = BorgOutput.find_best_parameterset(results, nobj)

params = config.parameters
if pset and len(pset)==config.get_parameter_count():
    for i in range(config.get_parameter_count()):
        params[i].set_parameter_value(pset[i])

for i in range(config.get_parameter_count()):
    print(params[i].get_parameter_value())

for r in results: print(r)
print(pset)

tmp = WaterGAP.update_parameter_file(params, 'parameter_002.json')
if tmp: print('succeeded')
else: print('not succeeded')