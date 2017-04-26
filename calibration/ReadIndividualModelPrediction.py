import sys
sys.path.append('..')
from calibration.watergap import WaterGAP
from calibration.variable import SimVariable, DerivedVariable


model_settings = """
home_directory = ../wgap_home
parameter_file = parameters.json
start_year = 1993
end_year = 2007
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

'''
var_definition = """
@
var_name = 1_CanopyWaterStorage_km3_G4B3
data_file = G_CANOPY_WATER_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 2_SnowWaterStorage_km3_G4B3
data_file = G_SNOW_WATER_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 3_SoilWaterStorage_km3_G4B3
data_file = G_SOIL_WATER_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 4_GroundWaterStorage_km3_G4B3
data_file = G_GROUND_WATER_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 5_LocalLakeStorage_km3_G4B3
data_file = G_LOC_LAKE_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 6_GlobalLakeStorage_km3_G4B3
data_file = G_GLO_LAKE_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 7_LocalWetlandStorage_km3_G4B3
data_file = G_LOC_WETL_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 8_GlobalWetlandStorage_km3_G4B3
data_file = G_GLO_WETL_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 9_ResourvorOut_km3_G4B3
data_file = G_RES_OUT_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 10_ResourvorStorageMean_km3_G4B3
data_file = G_RES_STORAGE_MEAN_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 11_RiverStorage_km3_G4B3
data_file = G_RIVER_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 12_TotalStorage_km3_G4B3
data_file = G_TOTAL_STORAGES_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 13_CanopyWaterStorage_mm_G4B3
data_file = G_CANOPY_WATER_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@


@
var_name = 14_SnowWaterStorage_mm_G4B3
data_file = G_SNOW_WATER_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 15_SoilWaterStorage_mm_G4B3
data_file = G_SOIL_WATER_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 16_GroundWaterStorage_mm_G4B3
data_file = G_GROUND_WATER_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 17_LocalLakeStorage_mm_G4B3
data_file = G_LOC_LAKE_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 18_GlobalLakeStorage_mm_G4B3
data_file = G_GLO_LAKE_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 19_LocalWetlandStorage_mm_G4B3
data_file = G_LOC_WETL_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 20_GlobalWetlandStorage_mm_G4B3
data_file = G_GLO_WETL_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 21_ResourvorStorageMean_mm_G4B3
data_file = G_RES_STORAGE_MEAN_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 22_RiverStorage_mm_G4B3
data_file = G_RIVER_STORAGE_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 23_TotalStorage_mm_G4B3
data_file = G_TOTAL_STORAGES_mm_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 24_CELL_AET_VOL_G4B3
data_file = G_CELL_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 25_Soil_ET_VOL_G4B3
data_file = G_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 26_Land_AET_VOL_G4B3
data_file = G_LAND_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 27_Land_AET_Uncorr_VOL_G4B3
data_file = G_LAND_AET_UNCORR_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 28_Soil_ET_mm_G4B3
data_file = G_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 29_Land_AET_mm_G4B3
data_file = G_LAND_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 30_Land_AET_Uncorr_mm_G4B3
data_file = G_LAND_AET_UNCORR_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 31_CELL_AET_mm_G4B3
data_file = G_CELL_AET_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 32_ConsistentPrecipitation_km3_G4B3
data_file = G_CONSISTENT_PRECIPITATION_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 33_Precipitation_VOL_G4B3
data_file = G_PRECIPITATION_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 34_Precipitation_mm_G4B3
data_file = G_PRECIPITATION_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 35_RiverDischarge_km3_G4B3
data_file = G_RIVER_AVAIL_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = [40771, 41090, 41406, 42893, 42897, 42317, 41724]
zone flag = False
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 36_UnsatisfiedWaterUse_mm_G4B3
data_file = G_UNSAT_USE_[YEAR].UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 37_PreviousUnsatifiedWaterUse_mm_G4B3
data_file = G_UNSAT_USE_PREV_[YEAR].UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
cell_weights = filename_data:areas_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 38_UnsatisfiedWaterUse_VOL_G4B3
data_file = G_UNSAT_USE_[YEAR].UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 39_PreviousUnsatifiedWaterUse_VOL_G4B3
data_file = G_UNSAT_USE_PREV_[YEAR].UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 40_NetUse_GW_m3_G4B3
data_file = G_NETUSE_GW_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 41_NetUse_SW_m3_G4B3
data_file = G_NETUSE_SW_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 42_TotalConsumptiveUse_m3_G4B3
data_file = G_TOTAL_CONS_USE_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 43_TotalConsumptiveUse_GW_m3_G4B3
data_file = G_TOTAL_CONS_USE_GW_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 44_TotalWithdrawal_GW_m3_G4B3
data_file = G_TOTAL_WITHDRAWAL_USE_GW_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = 45_TotalWithdrawal_m3_G4B3
data_file = G_TOTAL_WITHDRAWAL_USE_HISTAREA_m3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:upstreams_G4B3.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@
END
"""
'''

'''
var_definition = """
@
var_name = RiverDischarge_1950_2014_km3_G4B3
data_file = G_RIVER_AVAIL_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = [42897]
zone flag = False
zone stat = sum
compute anomalies = False
conversion factor = 1
@@
END
"""
'''

var_definition = """
@
var_name = LocalLake_km3_G4B3
data_file = G_LOC_LAKE_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:ganges_hardinge_bridge_2646200_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = GlobalLake_km3_G4B3
data_file = G_GLO_LAKE_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:ganges_hardinge_bridge_2646200_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = LocalWetland_km3_G4B3
data_file = G_LOC_WETL_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:ganges_hardinge_bridge_2646200_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = GlobalWetland_km3_G4B3
data_file = G_GLO_WETL_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:ganges_hardinge_bridge_2646200_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = Resourvor_km3_G4B3
data_file = G_RES_STORAGE_MEAN_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:ganges_hardinge_bridge_2646200_upstream.txt
zone flag = True
zone stat = sum
compute anomalies = False
conversion factor = 1
@@

@
var_name = River_km3_G4B3
data_file = G_RIVER_STORAGE_km3_[YEAR].12.UNF0
value_type = monthly
target_grid_cells = filename_data:ganges_hardinge_bridge_2646200_upstream.txt
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

var_definition = """
@
var_name = surface_water_storage_ganges_hardinge_bridge_2646200
equation = LocalLake_km3_G4B3+GlobalLake_km3_G4B3+LocalWetland_km3_G4B3+GlobalWetland_km3_G4B3+Resourvor_km3_G4B3+River_km3_G4B3
@@
END
"""
lines = var_definition.split('\n')
for i in reversed(range(len(lines))):
    l = lines[i].strip()
    if not l: lines.pop(i)
    else: lines[i] = l
derived_vars = DerivedVariable.read_variables(lines)

print('reading model predictions ..', end='', flush=True)
succeed = WaterGAP.read_predictions(vars, output_directory_name='OUTPUT')
if succeed: print('[done]')
else: print('[failed]')

for var in derived_vars:
    print('deriving data for %s ...'%var.varname, end='', flush=True)
    succeed = var.derive_data(simvars=vars)
    if succeed: print('[done]')
    else: print('[failed]')

for var in derived_vars:
    print('saving "%s" data ..'%var.varname, end='', flush=True)
    filename = var.varname + '.csv'
    var.data_cloud.sort()
    succeed = var.data_cloud.print_data(filename, append=True, separator=',')
    if succeed: print('[done]')
    else: print('[failed]')

print(WaterGAP.start_year, WaterGAP.end_year)