import sys
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP
from utilities.fileio import *
from calibration.variable import DerivedVariable


filename = 'ganges_configuration.txt'
config = Configuration.read_configuration_file(filename)
if not (config.is_okay() and WaterGAP.is_okay()):
    print('not succeed')
    exit(1001)

simvars = config.sim_variables
succeed = WaterGAP.update_directory_info('OUTPUT', 'DATA.DIR')
succeed = WaterGAP.read_predictions(simvars)

# if succeed:
#     funs = ['mean', 'std', 'min', 'max', 'q1', 'median', 'q3']
#     pred_stat, month_stat, year_stat = WaterGAP.prediction_statistics(simvars, funs=funs)
#
#     # writing basic prediction statistics
#     separator = ','; iter_no = 1
#     lines = []
#     for key in pred_stat.keys():
#         for v in pred_stat[key]: lines.append(separator.join(map(str, [iter_no, key] + v)))
#     if lines: print_on_file(lines, config.prediction_summary_filename, '_STAT_OS.LOCK', sleep_time=0.3)
#
#     lines = []
#     for key in month_stat.keys():
#         var_stat = month_stat[key]
#         for vk in var_stat.keys(): lines.append(
#             separator.join(map(str, [iter_no, key, separator.join(map(str, vk))] + var_stat[vk])))
#     if lines: print_on_file(lines, config.monthly_prediction_summary_filename, '_STAT_MS.LOCK', sleep_time=0.5)
#
#     lines = []
#     for key in year_stat.keys():
#         var_stat = year_stat[key]
#         for vk in var_stat.keys(): lines.append(
#             separator.join(map(str, [iter_no, key, separator.join(map(str, vk))] + var_stat[vk])))
#     if lines: print_on_file(lines, config.yearly_prediction_summary_filename, '_STAT_YS.LOCK', sleep_time=0.5)

simvars = config.sim_variables
obsvars = config.obs_variables
for i in range(len(config.derived_variables)):
    v = config.derived_variables[i]
    v.derive_data(simvars=simvars, obsvars=obsvars)
    filename = 'output/'+ v.varname + '_00001.csv'
    config.derived_variables[i].data_cloud.print_data(filename)

for v in simvars:
    filename = 'output/' + v.varname + '_00001.csv'
    v.data_cloud.print_data(filename)

# filename = 'test_0001.csv'
# var = simvars[0]
# succeed = var.data_cloud.print_data(filename)
print(succeed)