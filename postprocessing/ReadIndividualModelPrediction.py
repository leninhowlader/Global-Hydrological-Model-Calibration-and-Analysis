import sys
sys.path.append('..')
from wgap.watergap import WaterGAP
from calibration.variable import SimVariable

model_settings = """
home_directory = ../wgap_home
parameter_file = parameters.json
start_year = 1989
end_year = 2014
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


var_definition = """
@
var_name = 1_LocalLake_km3
data_file = G_LOC_LAKE_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 2_GlobalLake_km3
data_file = G_GLO_LAKE_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 3_LocalWetland_km3
data_file = G_LOC_WETL_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 4_GlobalWetland_km3
data_file = G_GLO_WETL_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 5_ResourvorOut_km3
data_file = G_RES_OUT_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 6_ResourvorStorageMean_km3
data_file = G_RES_STORAGE_MEAN_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 7_RiverStorage_km3
data_file = G_RIVER_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 8_TotalStorage_km3
data_file = G_TOTAL_STORAGES_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 11_discharge_km3pm
data_file = G_RIVER_AVAIL_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = 42897
zone flag = False
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 24_CELL_AET_mm
data_file = G_CELL_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:brahmaputra_bahadurbad_2646100_upstream.txt
cell_weights = filename:brahmaputra_bahadurbad_2646100_area.txt
zone flag = True
zone stat = avg
compute anomalies = False
conversion factor = 1
@@
END
"""


lines = var_definition.split('\n')
for i in reversed(range(len(lines))):
    l = lines[i].strip()
    if not l: lines.pop(i)
    else: lines[i] = l
vars = SimVariable.read_variables(lines)

# var_definition = """
# @
# var_name = surface_water_storage_ganges_hardinge_bridge_2646200
# equation = LocalLake_km3_G4B3+GlobalLake_km3_G4B3+LocalWetland_km3_G4B3+GlobalWetland_km3_G4B3+Resourvor_km3_G4B3+River_km3_G4B3
# @@
# END
# """
# lines = var_definition.split('\n')
# for i in reversed(range(len(lines))):
#     l = lines[i].strip()
#     if not l: lines.pop(i)
#     else: lines[i] = l
# derived_vars = DerivedVariable.read_variables(lines)

print('reading model predictions ..', end='', flush=True)
succeed = WaterGAP.read_predictions(vars, output_directory_name='OUTPUT')
if succeed: print('[done]')
else: print('[failed]')


for var in vars:
    print('saving "%s" data ..'%var.varname, end='', flush=True)
    filename = var.varname + '.csv'
    var.data_cloud.sort()
    succeed = var.data_cloud.print_data(filename, append=True, separator=',')
    if succeed: print('[done]')
    else: print('[failed]')

print(WaterGAP.start_year, WaterGAP.end_year)