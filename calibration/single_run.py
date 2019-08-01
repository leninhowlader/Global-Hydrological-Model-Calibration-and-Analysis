
import sys
sys.path.append('..')
from wgap.watergap import WaterGAP
from calibration.parameter import Parameter




model_settings = """
home_directory = ../wgap_home
parameter_file = parameters.json
start_year = 1989
end_year = 2005
grid_cell_count = 66896
output_endian_type = 2
data_directory_file = DATA.DIR
END
"""

lines = model_settings.split('\n')
for i in reversed(range(len(lines))):
    l = lines[i].strip()
    if not l: lines.pop(i)
    else: lines[i] = l
WaterGAP.read_model_settings(lines)
WaterGAP.executable = '../wgap_home/watergap.sh'
ret = WaterGAP.is_okay()
model_settings = None

parameter_def = """
@
param_name = CFA_cellCorrFactor
lower_bound = 0
upper_bound = 2
@@
@
param_name = CFS_statCorrFactor
lower_bound = 0
upper_bound = 1
@@
END
"""

lines = parameter_def.split('\n')
for i in reversed(range(len(lines))):
    l = lines[i].strip()
    if not l: lines.pop(i)
    else: lines[i] = l
params = Parameter.read_parameters(lines)
parameter_def = None

values = [1, 1]
for i in range(len(params)): params[i].parameter_value = values[i]

filename = 'parameters_01.json'
ret = WaterGAP.update_parameter_file(params, filename)
print(ret)