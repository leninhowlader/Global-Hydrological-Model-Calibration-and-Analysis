import sys
sys.path.append('..')
from calibration.watergap import WaterGAP
from calibration.variable import SimVariable


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


var_definition = """
#@
var_name = Soil_ET_G4B3
data_file = G_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:upstreams_G4B3.txt
cell_weights = filename:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
#@@
#@
var_name = Land_ET_G4B3
data_file = G_LAND_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:upstreams_G4B3.txt
cell_weights = filename:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
#@@
#@
var_name = Total_AET_G4B3
data_file = G_CELL_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:upstreams_G4B3.txt
cell_weights = filename:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
#@@
#@
var_name = Precipitation_G4B3
data_file = G_PRECIPITATION_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:upstreams_G4B3.txt
cell_weights = filename:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
#@@
#@
var_name = Discharge_G4B3
data_file = G_RIVER_AVAIL_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = [40771, 41090, 41406, 42893, 42897, 42317, 41724, 43452]
zone flag = False
compute anomalies = False
#@@
#@
var_name = Total_Storage_G4B3
data_file = G_TOTAL_STORAGES_mm_[year].12.UNF0
value_type = monthly
target_grid_cells = filename:upstreams_G4B3.txt
cell_weights = filename:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
#@@
@
var_name = NetUse_GW_G4B3
data_file = G_NETUSE_GW_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@
@
var_name = NetUse_SW_G4B3
data_file = G_NETUSE_SW_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename:upstreams_G4B3.txt
zone flag = True
zone stat = sum
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

WaterGAP.read_predictions(vars, output_directory_name='OUTPUT')

for var in vars:
    filename = var.varname + '.csv'
    var.data_cloud.sort()
    var.data_cloud.print_data(filename, append=True, separator=',')
