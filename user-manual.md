1. Getting started
2. Parameter Calibration



**2.1 What is a configuration file?** 

Configuration file contains all neccessary information to define a calibration/optimization problem (e.g., how many decision variables to be optimize, what the objectives are, etc.) and important configuration information for the optimization algorithm.

The configuration file contains following sections; the name of the section is given in parenthses:
- Experiment configuration (namely SETTINGS)
- Simulation program configuration (MODEL-OPTIONS)
- Parameters (PARAMETER)
- Observation variables (OBS-VARIABLE)
- Simulation variables (SIM-VARIABLE)
- Derived variables (DERIVED-VARIABLE)

Each section starts and ends with the keywords BEGIN and END respectively followed by the  name of the section. 

An example of configuration file:
```
BEGIN SETTINGS
experiment_type = calibration
calibration_id = ganges_qtes_01
maximum_iteration = 20000
output_filename = output/replication_01/results.csv
runtime_dynamics_filename = output/replication_01/runtime_dynamics.txt
runtime_dynamics_write_frequency = 500
save_param_values = output/replication_01/parameters.csv
save_function_values = output/replication_01/objectives.csv
parallel_evaluation = true
#report_filename = output/replication_01/report.txt
END SETTINGS

BEGIN MODEL-OPTIONS
model_executable = watergap.sh
home_directory = watergap
wgap_config_filename = configuration_watergap.txt
temporary_output_directory = temporary_output
#log_directory = log
start_year = 1980
end_year = 2009
output_endian_type = 2
grid_cell_count = 67420
model_version = wghm2.2e
END MODEL-OPTIONS

BEGIN PARAMETER
@
param_name = gammaHBV_runoff_coeff
lower_bound = 0.3
upper_bound = 3.0
target_grid_cells = filename:input/upstream.txt
@@
@
param_name = root_depth_multiplier
lower_bound = 0.5
upper_bound = 3.0
target_grid_cells = filename:input/upstream.txt
@@
@
param_name = river_roughness_coeff_mult
lower_bound = 1.0
upper_bound = 5.0
target_grid_cells = filename:input/upstream.txt
@@
@
param_name = precip_mult
lower_bound = 0.5
upper_bound = 2.0
target_grid_cells = filename:input/upstream.txt
@@
END PARAMETER


BEGIN OBS-VARIABLE
@
var_name = obs_discharge_km3
data_file = ../observations/ganges_river_discharge_km3.csv
data_file_type = csv
separator = ,
header = true
data_column_name = discharge
index_column_names = year, month
counter_simvar = sim_discharge_mts_km3
function = nse
borg_epsilon = 0.005
@@
@
var_name = obs_swsa_km3
data_file = ../observations/ganges_sws_variation_km3.csv
data_file_type = text
separator = ,
header = true
data_column_name = sws_variation_km3
index_column_names = year, month
counter_simvar = sim_swsa_km3
function = nse
borg_epsilon = 0.005
@@
END OBS-VARIABLE

BEGIN SIM-VARIABLE
@
varname = sim_discharge_mts_km3
filename = G_RIVER_AVAIL_[YEAR].12.UNF0
temporal_resolution = monthly
target_grid_cells = 43913
basin_outlets_only = True
compute_anomaly = False
conversion_factor = 1
@@
@
varname = sim_swsa_km3
filename = G_SURFACE_WATER_STORAGE_MEAN_km3_[YEAR].12.UNF0
temporal_resolution = monthly
target_grid_cells = filename:input/upstream.txt
spatial_aggregation = True
zone stat = sum
compute_anomaly = True
conversion_factor = 0.5
@@
END SIM-VARIABLE

BEGIN DERIVED-VARIABLE
END DERIVED-VARIABLE

```

