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

**Section Name: SETTINGS**
| Option Name | Description | Value type | Default value| Alternative names |
|:---|:---------------|:---|:---|:---|
|experiment_type|In sensitivity analysis (EET method), during the sample evaluation, the sim. difference between the reference run and the run with perturbed parameter will be computed. This is why a distinction of the process from GLUE analysis is necessary. In case of calibration, very different functions would be used. |String|sensitivity|experiment_type, experiment type, mode|
|experiment_name|Name of the experiment. The experiment name is used to create new file and directory names. Thus, when multiple experiments are running simulteneously, this option becomes a necessity |String|''|experiment_name, experiment name, experiment_id, experiment_id, calibration_id, calibration_name calibration id, calibration name|
|parallel_computation|The flag indicate whether or not the experiment run on multiple CPUs or on a stand-alone computer|Bool|True|do_parallel_evaluation, parallel_evaluations, parallel_evaluation, parallel evaluations, parallel evaluation, parallel, parallelization|
|seasonal_statistics_output_filename|||||
|as_change_in_prediction|||||
|function|||||
|report_outfile|||||
|**Options for Glue Analysis**|||||
|save_simulation_output|A flag indicating if the simulation output should be stored. The output format is usually UNF0*. If the flag is set True, the output files will be stored in the output directory|Bool|False|save_simulation_output, save simulation output, dump_model_prediction, save_model_prediction|
|output_directory|Name of the directory where the simulation output will be stored|String|''||
|sample_filename| The sample file contains parameter sets/samples which need to be evaluated. The file will be read in if the experiment type is either 'sensitivity' or 'Glue'|String|''|input_sample_filename, sample_filename|
|compute_prediction_efficiency|(will be removed)|Bool||compute_model_efficiency|
|model_efficiency_output_filename||||prediction_efficiency_output_filename|
|compute_prediction_statistics||||prediction_statistics|
|prediction_summary_statistics_filename||||summary_statistics_output_filename|
|annual_statistics_output_filename||||annual_statistics_filename|
|monthly_statistics_output_filename||||monthly_statistics_filename|
|compute_seasonal_statistics| Seasonal statistics refer to the seasonal parameters like peak and bottom values, amplitude, time of peak and bottom values |||seasonal_statistics|
|**Options for Sensitivity Analysis**|||||
|change_from_refsimulation|||||
|function_to_compute_change|||||
|**Options for Calibration Analysis (One-Calibration Mode)**|||||
|maximum_iteration| Maximum number of iteration|Integer|20,000| maximum_iteration, maximum iteration, max iter, max_iter|
|save_parameter_values|(will be deleted) A flag indicate whether or not the parameter values will be stored|String|''||
|parameter_outfile|(optional) Name of the filename where the parameter values for the sample/proposed model run will be stored|String|''||
|objective_outfile|Filename where objectives during model evaluation will be stored|String|''||
|result_outfile||String|||
|runtime_dynamics_outfile|filename where the information about Runtime dynamics related to the optimization algorithm to be stored|String|''||
|runtime_dynamics_frequency|After how many model runs the runtime dynamics will be stored|Int|500||
|sleep_time|||||
|**Options for Many-Calibration Mode**|||||
|many_calibration|(not implemented yet)|Bool|False||
|parameter_indexfile| (not implemented yet) Name of file where parameter numbers (or index) are listed for each of the many calibration problems|String|''||
|objective_indexfile| (not implemented yet) Name of the file where the objective numbers (or index) for each of the many calibratin problemns are listed|String|''||
|**Utility Options**|||||
|compute_upstream|The flag indicate whether or not the cell list of upstream area would be computed from the station file given that the the station filename is provided in model configuration section.|Bool|False|compute_upstream_from_station_file, upstream_from_station_file, target_cells_from_station_file, target_cell_from_station_file, target cells from station file, target cell from station file|
|disjoint_basins|When the upstream cell list will be computed directly from the station file, non-overlapping area will be identified if the flag is set true|Bool|True|disjoint_basin_extent, disjoint basin extent|
|parameter_description_filename| Name of the file where parameters are described. If the value of this parameter is provided, the parameter list will be created using the parameter description; parameter section can be left empty |String|''|parameter_info, parameter_info_input_filename, parameter_info_filename|
||||||
||||||

*File format of simulation output: Simulation output is stored in a native WGHM file format (UNF0) which is binary array of floating point values. Number of column is provided in the filename before file extension and a dot preceed the number.


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

