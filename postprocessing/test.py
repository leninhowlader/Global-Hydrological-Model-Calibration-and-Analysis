import sys
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP

succeed = False
config_file = 'brahmaputra_bahadurbad_2646100_configuration.txt'
config = Configuration.read_configuration_file(config_file)
if config.is_okay() and WaterGAP.is_okay(): succeed = True

pval = [0.9578, 0.8616, 18.9246, 5, 0.9727, 0.0174, 3, 0.9242]
if len(pval) != len(config.parameters): succeed = False
else:
    for i in range(len(config.parameters)): config.parameters[i].set_parameter_value(pval[i])

if succeed:
    parameter_filename = 'parameters_calib_vi.json'
    succeed = WaterGAP.update_parameter_file(config.parameters, parameter_filename)

print(succeed)