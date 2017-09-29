import sys
sys.path.append('..')
from calibration.watergap import WaterGAP
from calibration.variable import SimVariable, DerivedVariable
from calibration.configuration import Configuration

#
# model_settings = """
# home_directory = ../wgap_home
# parameter_file = parameters_noCorrFac.json
# start_year = 2006
# end_year = 2010
# grid_cell_count = 66896
# output_endian_type = 2
# data_directory_file = DATA.DIR
# END
# """
#
# lines = model_settings.split('\n')
# for i in reversed(range(len(lines))):
#     l = lines[i].strip()
#     if not l: lines.pop(i)
#     else: lines[i] = l
# WaterGAP.read_model_settings(lines)
#
#
# # var_definition = """
# # @
# # var_name = ET_mm_monthly_sum
# # data_file = G_CELL_AET_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # cell_weights = filename:input/brahmaputra_bahadurabad_areas.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = Discharge_km3
# # data_file = G_RIVER_AVAIL_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = 42897
# # zone flag = False
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = LocalLake_km3
# # data_file = G_LOC_LAKE_STORAGE_km3_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = GlobalLake_km3
# # data_file = G_GLO_LAKE_STORAGE_km3_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = LocalWetland_km3
# # data_file = G_LOC_WETL_STORAGE_km3_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = GlobalWetland_km3
# # data_file = G_GLO_WETL_STORAGE_km3_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = Resourvor_km3
# # data_file = G_RES_STORAGE_MEAN_km3_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = River_km3
# # data_file = G_RIVER_STORAGE_km3_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# #
# # @
# # var_name = TotalStorage_km3
# # data_file = G_TOTAL_STORAGES_km3_[YEAR].12.UNF0
# # value_type = monthly
# # target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# # zone flag = True
# # zone stat = sum
# # compute anomalies = False
# # conversion factor = 1
# # @@
# # END
# # """
#
# var_definition = """
# @
# var_name = Discharge_km3
# data_file = G_RIVER_AVAIL_[YEAR].12.UNF0
# value_type = monthly
# target_grid_cells = 42897
# zone flag = False
# zone stat = sum
# compute anomalies = False
# conversion factor = 1
# @@
#
# @
# var_name = TotalStorage_km3
# data_file = G_TOTAL_STORAGES_km3_[YEAR].12.UNF0
# value_type = monthly
# target_grid_cells = filename:input/brahmaputra_bahadurabad_upstreams.txt
# zone flag = True
# zone stat = sum
# compute anomalies = False
# conversion factor = 1
# @@
# END
# """
# lines = var_definition.split('\n')
# for i in reversed(range(len(lines))):
#     l = lines[i].strip()
#     if not l: lines.pop(i)
#     else: lines[i] = l
# vars = SimVariable.read_variables(lines)
#
# var_definition = """
#
# END
# """
# lines = var_definition.split('\n')
# for i in reversed(range(len(lines))):
#     l = lines[i].strip()
#     if not l: lines.pop(i)
#     else: lines[i] = l
# derived_vars = DerivedVariable.read_variables(lines)

filename = '/media/sf_private/SENSITIVITY_DATASET_GB/configuration/configuration_xa.txt'
config = Configuration.read_configuration_file(filename)
if not (config.is_okay() and WaterGAP.is_okay()): exit('failed')

vars, derived_vars = config.sim_variables, config.derived_variables

print('reading model predictions ..', end='', flush=True)
succeed = WaterGAP.read_predictions(vars, output_directory_name='OUTPUT')
for var in vars: var.compute_anomalies()

if succeed: print('[done]')
else: print('[failed]')

for var in vars:
    print('saving "%s" data ..'%var.varname, end='', flush=True)
    filename = 'output/' + var.varname + '.csv'
    var.data_cloud.sort()
    succeed = var.data_cloud.print_data(filename, append=True, separator=',')
    if succeed: print('[done]')
    else: print('[failed]')

for var in derived_vars:
    print('deriving data for %s ...'%var.varname, end='', flush=True)
    succeed = var.derive_data(simvars=vars)
    if succeed: print('[done]')
    else: print('[failed]')

for var in derived_vars:
    print('saving "%s" data ..'%var.varname, end='', flush=True)
    filename = 'output/' + var.varname + '.csv'
    var.data_cloud.sort()
    succeed = var.data_cloud.print_data(filename, append=True, separator=',')
    if succeed: print('[done]')
    else: print('[failed]')

print('Program ends!')