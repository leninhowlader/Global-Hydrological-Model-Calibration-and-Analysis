__author__ = 'mhasan'

import sys, os
sys.path.append('..')
from calibration.variable import ObsVariable, SimVariable, DerivedVariable
from wgap.watergap import WaterGAP
from calibration.parameter import Parameter
from utilities.fileio import read_flat_file
from utilities.station import Station
from utilities.upstream import Upstream
from utilities.globalgrid import GlobalGrid as gg

class Configuration:
    def __init__(self, mode='sensitivity'):
        self.__mode = mode
        self.__target_cells_from_station_file = True
        self.__disjoint_basin_extent = True

        # variables for sensitivity-mode
        self.input_file_for_parameters = ''
        self.sample_file = ''
        self.prediction_statistics = False

        self.monthly_prediction_summary_filename = 'prediction_summary_monthly.dat'
        self.yearly_prediction_summary_filename = 'prediction_summary_yearly.dat'
        self.prediction_summary_filename = 'prediction_summary.dat'
        self.prediction_efficiency_filename = 'prediction_efficiency.dat'
        self.summary_statistics_filename = 'summary_statistics.csv'
        self.output_directory = 'output'

        # variables for calibration-mode
        self.__executable_name = ''
        self.__system_arguments = []
        self.__max_iterations = 0
        self.__prediction_output_filename = ''
        self.__iteration_paramvalue_filename = ''
        self.__model_efficiency_filename = ''
        self.__calibration_output_filename = ''
        self.__parallel_evaluation_flag = False

        # common variables
        self.obs_variables = []
        self.sim_variables = []
        self.derived_variables = []
        self.parameters = []
        self.samples = []

    @property
    def target_cells_from_station_file(self): return self.__target_cells_from_station_file
    @target_cells_from_station_file.setter
    def target_cells_from_station_file(self, flag:bool): self.__target_cells_from_station_file = flag

    @property
    def disjoint_basin_extent(self): return self.__disjoint_basin_extent
    @disjoint_basin_extent.setter
    def disjoint_basin_extent(self, flag): self.__disjoint_basin_extent = flag

    def set_executable_name(self, executable_name): self.__executable_name = executable_name
    def set_system_arguments(self, args): self.__system_arguments = args
    def set_max_iterations(self, max_iter): self.__max_iterations = max_iter
    def set_prediction_output_filename(self, filename): self.__prediction_output_filename = filename
    def set_paramvalue_filename(self, filename): self.__iteration_paramvalue_filename = filename
    def set_model_efficiency_filename(self, filename): self.__model_efficiency_filename = filename
    def set_calibration_output_filename(self, filename): self.__calibration_output_filename = filename
    def set_parallel_evaluation_flag(self, flag): self.__parallel_evaluation_flag = flag
    def set_mode(self, mode): self.__mode = mode
    def get_executable_name(self): return self.__executable_name
    def get_system_arguments(self): return self.__system_arguments
    def get_max_iterations(self): return self.__max_iterations
    def get_prediction_output_filename(self): return self.__prediction_output_filename
    def get_paramvalue_filename(self): return self.__iteration_paramvalue_filename
    def get_model_efficiency_filename(self): return self.__model_efficiency_filename
    def get_calibraiton_output_filename(self): return self.__calibration_output_filename
    def get_parallel_evaluation_flag(self): return self.__parallel_evaluation_flag
    def get_mode(self): return self.__mode

    def obs_var_count(self): return len(self.obs_variables)
    def sim_var_count(self): return len(self.sim_variables)
    def get_parameter_count(self): return len(self.parameters)

    def get_objective_count(self):
        count = 0

        sim_varnames, derived_vars = [], []
        for v in self.sim_variables: sim_varnames.append(v.varname)
        for v in self.derived_variables: derived_vars.append(v.varname)

        for v in self.obs_variables:
            if v.counter_variable in sim_varnames: count += 1
            if v.counter_variable in derived_vars: count += 1

        return count

    @staticmethod
    def read_configuration_file(filename):
        config = Configuration()

        try:
            fs = open(filename, 'r')
            lines = fs.readlines()
            try: fs.close()
            except: pass

            while lines:
                line = lines.pop(0).strip()
                if line:
                    temp = line.strip().split()
                    for i in range(len(temp)): temp[i] = temp[i].strip().lower()
                    if len(temp) == 2:
                        key, value = temp[0], temp[1]
                        if key == 'begin':
                            if value == 'sa-settings': Configuration.read_sensitivity_settings(lines, config)
                            elif value == 'settings': Configuration.read_calibration_settings(lines, config)
                            elif value == 'parameter' and len(config.parameters) == 0: # config.get_mode() == 'calibration':
                                param_list = Parameter.read_parameters(lines)
                                if param_list: config.parameters = param_list
                            elif value == 'obs-variable': config.obs_variables = ObsVariable.read_variables(lines)
                            elif value == 'sim-variable': config.sim_variables = SimVariable.read_variables(lines)
                            elif value == 'model-options': WaterGAP.read_model_settings(lines)
                            elif value == 'derived-variable': config.derived_variables = DerivedVariable.read_variables(lines)
        except: config = None

        return config

    @staticmethod
    def read_sensitivity_settings(lines, config):
        config.set_mode('sensitivity')
        while lines:
            line = lines.pop(0).strip()
            if line:
                temp = line.strip().split()
                temp[0] = temp[0].strip().lower()
                if temp[0] == 'end': return True
                else:
                    temp = line.split('=')
                    for i in range(len(temp)): temp[i] = temp[i].strip()
                    if len(temp) == 2:
                        key, value = temp[0], temp[1]
                        if key in ['summary_statistics_filename', 'summary_statistics', 'stat_summary', 'summary statistics filename',
                                     'summary statistics', 'stat summary']:
                            config.summary_statistics_filename = value
                        elif key in ['output_directory', 'output directory']: config.output_directory = value
                        elif key in ['output_model_efficiency', 'output model efficiency', 'output_efficiency',
                                     'output efficiency', 'prediction_efficiency_filename']: config.prediction_efficiency_filename = value
                        elif key in ['input_parameter_list_filename', 'input_parameter_list', 'parameter_list',
                                     'input parameter list config_filename', 'input parameter list', 'parameter list']:
                            config.input_file_for_parameters = value
                        elif key in ['sample_list_file', 'sample list file', 'sample file', 'sample_file']:
                            config.sample_file = value
                        elif key in ['prediction_statistics', 'predictionstatistics']:
                            value = value.lower()
                            if value in ['true', 't', '1', 'yes', 'y']: config.prediction_statistics = True
                            else: config.prediction_statistics = False
                        elif key in ['target_cells_from_station_file', 'target_cell_from_station_file',
                                     'target cells from station file', 'target cell from station file']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.target_cells_from_station_file = True
                            else: config.target_cells_from_station_file = False
                        elif key in ['disjoint_basin_extent', 'disjoint basin extent']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.disjoint_basin_extent = True
                            else: config.disjoint_basin_extent = False
        return False

    @staticmethod
    def read_calibration_settings(lines, config):
        config.set_mode('calibration')

        while lines:
            line = lines.pop(0).strip()
            if line:
                temp = line.strip().split()
                temp[0] = temp[0].strip().lower()
                if temp[0] == 'end':
                    return True
                else:
                    temp = line.split('=')
                    for i in range(len(temp)): temp[i] = temp[i].strip()
                    if len(temp) == 2:
                        key, value = temp[0], temp[1]
                        if key in ['executable_name', 'executable name', 'executable']:
                            config.set_executable_name(value)
                        elif key in ['monthly_summary_filename', 'monthly summary config_filename', 'month_summary',
                                     'monthly_summary', 'month summary', 'monthly summary']:
                            config.monthly_prediction_summary_filename = value
                        elif key in ['system_arguments', 'system arguments', 'arguments']:
                            value = value.split(',')
                            for i in range(len(value)): value[i] = value[i].strip()
                            config.set_system_arguments(value)
                        elif key in ['maximum_iteration', 'maximum iteration', 'max iter', 'max_iter']:
                            config.set_max_iterations(value)
                        elif key in ['save_simulation_output', 'save simulation output', 'prediction_dumpfile', 'prediction dumpfile']:
                            config.set_prediction_output_filename(value)
                        elif key in ['save_param_values', 'save param values', 'save_param_value', 'save param value', 'parameter_dumpfile', 'parameter dumpfile']:
                            config.set_paramvalue_filename(value)
                        elif key in ['save_function_values', 'save function values', 'save_function_value', 'save function value', 'funvalue_dumpfile', 'dunvalue dumpfile']:
                            config.set_model_efficiency_filename(value)
                        elif key in ['output_filename']:
                            config.set_calibration_output_filename(value)
                        elif key in ['parallel_evaluations', 'parallel_evaluation', 'parallel evaluations', 'parallel evaluation', 'parallel', 'parallelization']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.set_parallel_evaluation_flag(True)
                            else: config.set_parallel_evaluation_flag(False)
                        elif key in ['target_cells_from_station_file', 'target_cell_from_station_file',
                                     'target cells from station file', 'target cell from station file']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.target_cells_from_station_file = True
                            else: config.target_cells_from_station_file = False
                        elif key in ['disjoint_basin_extent', 'disjoint basin extent']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.disjoint_basin_extent = True
                            else: config.disjoint_basin_extent = False
        return False

    def is_okay(self, skip_observation=False):
        '''
        This function checks the completeness of the configuration object. During the check, all variables'
        completeness is also being checked. If the configuration object has observation variable(s), observation
        data will be read hear. In case of sensitivity analysis, samples will be loaded during this check.
        The parameters' completeness will be checked as well.
        Finally, model executable name and address is tested.

        :return: (bool) True : if all checks succeed
                        False : otherwise
        '''

        # step: check whether or not the station file is available when 'target cell from station file' flag is set ON
        if not (WaterGAP.station_filename and
                os.path.exists(os.path.join(WaterGAP.home_directory, WaterGAP.station_filename))):
            self.target_cells_from_station_file = False
            self.disjoint_basin_extent = False

        # step: read the target cells from station file, if applicable
        if self.target_cells_from_station_file:
            succeed = self.generate_target_cells_from_station_file()
            if not succeed: return False

        # step: check completeness of simulation variables. there must at least be one simulation variable
        if not self.sim_variables: return False
        else:
            for var in self.sim_variables:
                var.data_source.file_endian = WaterGAP.output_endian_type
                if not var.is_okay(): return False

        # step: check completeness of observation variables (if any). Try to load the observation data
        if not skip_observation:
            if len(self.obs_variables) > 0:
                if not ObsVariable.data_collection(self.obs_variables): return False

                for var in self.obs_variables:
                    if not var.is_okay(): return False

        # step: check completeness of derived variables (if any)
        if len(self.derived_variables) > 0:
            for var in self.derived_variables:
                if not var.is_okay(): return False
                if not var.evaluate_equation(simvars=self.sim_variables, obsvars=self.obs_variables):
                    return False

        # step: check if the samples can be gathered in case of sensitivity analysis mode. load the samples.
        # if parameter file is specified instead of defining individual parameters, create the parameter
        # object with provided information in the parameter info file.
        if self.__mode == 'sensitivity':

            # check the sample file and load samples
            if not self.sample_file: return False
            elif not self.samples:
                header, dt = read_flat_file(self.sample_file, separator=',')
                if dt:
                    for d in dt:
                        if len(d) != len(self.parameters): return False
                    self.samples = dt
                else: return False
            if not self.samples: return False

            # create parameter objects from parameter info file (if given)
            if self.input_file_for_parameters: self.parameters = Parameter.read_parameter_list(self.input_file_for_parameters, header=True)

        # step: check completeness of parameters
        if not self.parameters: return False
        else:
            for param in self.parameters:
                if not param.is_okey(): return False

        # step: check model executable name and address. [this check could be omitted]
        if not WaterGAP.executable:
            executable_name = self.get_executable_name()
            if WaterGAP.home_directory:
                if executable_name.find(WaterGAP.home_directory) == -1: executable_name = os.path.join(WaterGAP.home_directory, executable_name)
            WaterGAP.executable = executable_name
        if not WaterGAP.executable: return False

        return True

    def generate_target_cells_from_station_file(self):
        '''
        This method generate basin cell list from given station file and then assign them to variables and parameter.
        However, if target cell list (either of a variable or of a parameter) is provided by another mean (i.e., usign
        old method), the cell list will not be overwritten. This will ensure explicit assignment of target cell if it
        is needed.

        :return: (bool) True on success, False otherwise
        '''
        succeed = True

        # setp: get basin outlet cells
        filename = os.path.join(WaterGAP.home_directory, WaterGAP.station_filename)
        outlets = Station.get_stations(filename, rowcol_only=True)
        if len(outlets) == 0: return False

        # step: compute entire upstream basin extents
        succeed = Upstream.read_flow_data(unf_input=True, model_version=WaterGAP.model_version)
        if not succeed: return False
        basins = Upstream.compute_basin_extent(outlets)
        if len(basins) != len(outlets): return False

        discharge_outlets = []
        # step: compute disjoint basins (if applicable) and discharge outlet cells for all basins
        if self.disjoint_basin_extent:
            supbasins = Upstream.find_super_basin(outlets)

            discharge_outlets = Upstream.find_basin_discharge_cell(basins, supbasins)
            basins = Upstream.compute_disjoint_basin_extent(basins, supbasins)
        else:
            for cell in outlets: discharge_outlets.append([cell])

        # step: find wghm cell num and area for all basin cells
        basin_cellnum, basin_cellareas = [], []
        for key, value in basins.items():

            cnums, careas = [], []
            for cell in value:
                cnums.append(gg.get_wghm_cell_number(cell[0], cell[1]))
                careas.append(gg.find_wghm_cellarea(cell[0]))

            basin_cellnum.append(cnums)
            basin_cellareas.append(careas)

        # step: find wghm cell num of discharge outlets
        cellnum_discharge = []
        for basin_outlets in discharge_outlets:
            cnums = []
            for cell in basin_outlets: cnums.append(gg.get_wghm_cell_number(cell[0], cell[1]))
            cellnum_discharge.append(cnums)

        # step: assign target cells in simulation variables
        for var in self.sim_variables:
            if not var.basin_cell_list:
                if var.basin_outlets_only: var.basin_cell_list = cellnum_discharge
                else: var.basin_cell_list = basin_cellnum

            if not var.cell_weights and var.cell_area_as_weight: var.cell_weights = basin_cellareas

        # step: assign target cells in parameters
        unique_target_cells = []
        for basin in basin_cellnum: unique_target_cells += basin
        unique_target_cells = list(set(unique_target_cells))

        for param in self.parameters:
            if not param.cell_list: param.cell_list = unique_target_cells

        return succeed
