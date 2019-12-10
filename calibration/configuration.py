__author__ = 'mhasan'

import sys, os
sys.path.append('..')
from calibration.variable import ObsVariable, SimVariable, DerivedVariable
from wgap.watergap import WaterGAP
from calibration.parameter import Parameter
from utilities.fileio import FileInputOutput as io
from utilities.station import Station
from utilities.upstream import Upstream
from utilities.globalgrid import GlobalGrid as gg

class Configuration:
    def __init__(self, mode='sensitivity'):
        self.__mode = mode
        self.__target_cells_from_station_file = True
        self.__disjoint_basin_extent = True

        self.__dump_model_prediction = True
        self.__compute_prediction_efficiency = False
        self.__compute_prediction_statistics = False
        self.__compute_seasonal_statistics = False
        # NB: Prediction statistics and seasonal statistics will be merged
        # together in the future

        # input parameter info file
        self.__parameter_info_input_filename = ''
        # [mode: sensitivity] input sample filename
        self.__input_sample_filename = ''

        # output filename(s) of prediction statistics
        # [used only when compute_prediction_statistics flag is true]
        self.__prediction_summary_monthly_output_filename = ''
        self.__prediction_summary_annual_output_filename = ''
        self.__prediction_summary_output_filename = ''

        # output filename of seasonal statistics
        # [used only when compute_seasonal_statistics flag is set true]
        self.__seasonal_statistics_output_filename = 'seasonal_statistics.csv'
        # NB: Prediction statistics and seasonal statistics will be merged
        # together in the future


        # output directory
        self.__output_directory = 'output'

        # variables for calibration-mode
        self.__executable_name = ''
        self.__system_arguments = []
        self.__max_iterations = 0
        #self.__prediction_output_filename = ''
        #self.__iteration_paramvalue_filename = ''

        # output filename of prediction efficiency
        # [used only when compute_prediction_efficiency flag is set true]
        self.__prediction_efficiency_output_filename = 'prediction_efficiency.dat'

        # [mode-calibration] output filename of parameter values
        self.__parameter_value_output_filename = ''

        # [mode-calibration] output filename of calibration results
        self.__calibration_result_output_filename = ''


        self.__do_parallel_evaluation = False

        # common variables
        self.obs_variables = []
        self.sim_variables = []
        self.derived_variables = []
        self.parameters = []
        self.samples = []

    @property
    def mode(self): return self.__mode
    @mode.setter
    def mode(self, config_mode): self.__mode = config_mode

    @property
    def parallel_evaluation(self):
        return self.__do_parallel_evaluation
    @parallel_evaluation.setter
    def parallel_evaluation(self, flag):
        self.__do_parallel_evaluation = flag

    @property
    def parameter_info_filename(self):
        return self.__parameter_info_input_filename
    @parameter_info_filename.setter
    def parameter_info_filename(self, filename):
        self.__parameter_info_input_filename = filename

    @property
    def input_sample_filename(self):
        return self.__input_sample_filename
    @input_sample_filename.setter
    def input_sample_filename(self, filename):
        self.__input_sample_filename = filename

    @property
    def dump_model_prediction(self):
        return self.__dump_model_prediction
    @dump_model_prediction.setter
    def dump_model_prediction(self, flag):
        self.__dump_model_prediction = flag

    @property
    def compute_prediction_efficiency(self):
        return self.__compute_prediction_efficiency
    @compute_prediction_efficiency.setter
    def compute_prediction_efficiency(self, flag):
        self.__compute_prediction_efficiency = flag

    @property
    def compute_prediction_statistics(self):
        return self.__compute_prediction_statistics
    @compute_prediction_statistics.setter
    def compute_prediction_statistics(self, flag):
        self.__compute_prediction_statistics = flag

    @property
    def compute_seasonal_statistics(self):
        return self.__compute_seasonal_statistics
    @compute_seasonal_statistics.setter
    def compute_seasonal_statistics(self, flag):
        self.__compute_seasonal_statistics = flag

    @property
    def output_directory(self):
        return self.__output_directory
    @output_directory.setter
    def output_directory(self, directory):
        self.__output_directory = directory

    @property
    def prediction_efficiency_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__prediction_efficiency_output_filename)
    @prediction_efficiency_output_filename.setter
    def prediction_efficiency_output_filename(self, filename):
        self.__prediction_efficiency_output_filename = filename

    @property
    def parameter_value_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__parameter_value_output_filename)
    @parameter_value_output_filename.setter
    def parameter_value_output_filename(self, filename):
        self.__parameter_value_output_filename = filename

    @property
    def calibration_result_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__calibration_result_output_filename)
    @calibration_result_output_filename.setter
    def calibration_result_output_filename(self, filename):
        self.__calibration_result_output_filename = filename

    @property
    def seasonal_statistics_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__seasonal_statistics_output_filename)
    @seasonal_statistics_output_filename.setter
    def seasonal_statistics_output_filename(self, filename):
        self.__seasonal_statistics_output_filename = filename

    @property
    def prediction_summary_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__prediction_summary_output_filename)
    @prediction_summary_output_filename.setter
    def prediction_summary_output_filename(self, filename):
        self.__prediction_summary_output_filename = filename

    @property
    def prediction_summary_annual_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__prediction_summary_annual_output_filename)
    @prediction_summary_annual_output_filename.setter
    def prediction_summary_annual_output_filename(self, filename):
        self.__prediction_summary_annual_output_filename = filename

    @property
    def prediction_summary_monthly_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__prediction_summary_monthly_output_filename)
    @prediction_summary_monthly_output_filename.setter
    def prediction_summary_monthly_output_filename(self, filename):
        self.__prediction_summary_monthly_output_filename = filename

    @property
    def target_cells_from_station_file(self):
        return self.__target_cells_from_station_file
    @target_cells_from_station_file.setter
    def target_cells_from_station_file(self, flag:bool):
        self.__target_cells_from_station_file = flag

    @property
    def disjoint_basin_extent(self):
        return self.__disjoint_basin_extent
    @disjoint_basin_extent.setter
    def disjoint_basin_extent(self, flag):
        self.__disjoint_basin_extent = flag

    def set_executable_name(self, executable_name): self.__executable_name = executable_name
    def set_system_arguments(self, args): self.__system_arguments = args
    def set_max_iterations(self, max_iter): self.__max_iterations = max_iter
    #def set_prediction_output_filename(self, filename): self.__prediction_output_filename = filename
    #def set_paramvalue_filename(self, filename): self.__iteration_paramvalue_filename = filename
    # def set_model_efficiency_filename(self, filename): self.__prediction_efficiency_output_filename = filename
    #def set_calibration_output_filename(self, filename): self.__calibration_result_output_filename = filename
    #def set_parallel_evaluation_flag(self, flag): self.__do_parallel_evaluation = flag
    def set_mode(self, mode): self.__mode = mode
    def get_executable_name(self): return self.__executable_name
    def get_system_arguments(self): return self.__system_arguments
    def get_max_iterations(self): return self.__max_iterations
    #def get_prediction_output_filename(self): return self.__prediction_output_filename
    #def get_paramvalue_filename(self): return self.__iteration_paramvalue_filename
    #def get_model_efficiency_filename(self): return self.__prediction_efficiency_output_filename
    #def get_calibraiton_output_filename(self): return self.__calibration_result_output_filename
    #def get_parallel_evaluation_flag(self): return self.__do_parallel_evaluation
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
                        if not (key and value): continue


                        if key in ['parallel_evaluation',
                                     'parallel evaluation']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.parallel_evaluation = True
                            else: config.parallel_evaluation = False

                        elif key in ['parameter_info_filename',
                                     'parameter info filename',
                                     'parameter_info_input_filename',
                                     'parameter info input filename']:
                            config.parameter_info_filename = value

                        elif key in ['summary_statistics_filename', 'summary_statistics', 'stat_summary', 'summary statistics filename',
                                     'summary statistics', 'stat summary']:
                            config.summary_statistics_filename = value

                        elif key in ['output_directory', 'output directory']:
                            config.output_directory = value

                        elif key in ['dump_model_prediction',
                                     'dump model prediction',
                                     'save_model_prediction',
                                     'save model prediction']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.dump_model_prediction = True
                            else: config.dump_model_prediction = False

                        elif key in ['compute_prediction_efficiency',
                                     'compute prediction efficiency',
                                     'compute_model_efficiency',
                                     'compute model efficiency']:
                            value = value.lower()
                            if value in ['true', 't', '1', 'yes', 'y']:
                                config.compute_prediction_efficiency = True
                            else: config.compute_prediction_efficiency = False

                        elif key in ['model_efficiency_filename',
                                     'model efficiency filename',
                                     'prediction_efficiency_filename',
                                     'prediction efficiency filename']:
                            config.prediction_efficiency_output_filename = value
                            config.compute_prediction_efficiency = True

                        elif key in ['input_sample_filename',
                                     'input sample filename',
                                     'sample_filename',
                                     'sample filename']:
                            config.input_sample_filename = value

                        elif key in ['compute_prediction_statistics',
                                     'compute prediction statistics',
                                     'prediction_statistics',
                                     'predictionstatistics']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.compute_prediction_statistics = True
                            else: config.compute_prediction_statistics = False

                        elif key in ['prediction_summary_statistics_filename',
                                     'summary_statistics_output_filename',
                                     'prediction summary statistics filename',
                                     'summary statistics output filename']:
                            config.prediction_summary_output_filename = value
                            config.compute_prediction_statistics = True

                        elif key in ['annual_summary_statistics_output_filename',
                                     'annual_summary_statistics_filename',
                                     'annual summary statistics output filename',
                                     'annual summary statistics filename']:
                            config.prediction_summary_annual_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['monthly_summary_statistics_output_filename',
                                     'monthly_summary_statistics_filename',
                                     'monthly summary statistics output filename',
                                     'monthly summary statistics filename']:
                            config.prediction_summary_monthly_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['compute_seasonal_statistics',
                                     'seasonal_statistics',
                                     'compute seasonal statistics',
                                     'seasonal statistics']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.compute_seasonal_statistics = True
                            else: config.compute_seasonal_statistics = False

                        elif key in ['seasonal_statistics_output_filename',
                                     'seasonal_statistics_filename',
                                     'seasonal statistics output filename',
                                     'seasonal statistics filename']:
                            config.seasonal_statistics_output_filename = value
                            config.compute_seasonal_statistics = True

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

        # set default values
        config.compute_prediction_efficiency = True
        config.dump_model_prediction = False
        config.compute_seasonal_statistics = False
        config.compute_prediction_statistics = False

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
                        if not (key and value): continue

                        if key in ['executable_name',
                                   'executable name',
                                   'executable']:
                            config.set_executable_name(value)

                        elif key in ['system_arguments',
                                     'system arguments',
                                     'arguments']:
                            value = value.split(',')
                            for i in range(len(value)): value[i] = value[i].strip()
                            config.set_system_arguments(value)

                        elif key in ['maximum_iteration',
                                     'maximum iteration',
                                     'max iter',
                                     'max_iter']:
                            config.set_max_iterations(value)

                        elif key in ['parallel_evaluation',
                                     'parallel evaluation']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.parallel_evaluation = True
                            else: config.parallel_evaluation = False

                        elif key in ['parameter_info_filename',
                                     'parameter info filename',
                                     'parameter_info_input_filename',
                                     'parameter info input filename']:
                            config.parameter_info_filename = value

                        elif key in ['output_directory', 'output directory']:
                            config.output_directory = value

                        elif key in ['model_efficiency_filename',
                                     'model efficiency filename',
                                     'prediction_efficiency_filename',
                                     'prediction efficiency filename']:
                            config.prediction_efficiency_output_filename = value
                            config.compute_prediction_efficiency = True

                        elif key in ['parameter_value_output_filename',
                                     'parameter value output filename']:
                            config.parameter_value_output_filename = value

                        elif key in ['dump_model_prediction',
                                     'dump model prediction',
                                     'save_model_prediction',
                                     'save model prediction']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.dump_model_prediction = True
                            else: config.dump_model_prediction = False

                        elif key in ['calibration_result_output_filename',
                                     'calibration_result_filename',
                                     'calibration result output filename',
                                     'calibration result filename']:
                            config.calibration_result_output_filename = value


                        elif key in ['target_cells_from_station_file', 'target_cell_from_station_file',
                                     'target cells from station file', 'target cell from station file']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.target_cells_from_station_file = True
                            else: config.target_cells_from_station_file = False
                        elif key in ['disjoint_basin_extent', 'disjoint basin extent']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.disjoint_basin_extent = True
                            else: config.disjoint_basin_extent = False

                        elif key in ['compute_prediction_statistics',
                                     'compute prediction statistics',
                                     'prediction_statistics',
                                     'predictionstatistics']:
                            value = value.lower()
                            if value in ['true', 't', '1', 'yes', 'y']:
                                config.compute_prediction_statistics = True
                            else: config.compute_prediction_statistics = False

                        elif key in ['prediction_summary_statistics_filename',
                                     'summary_statistics_output_filename',
                                     'prediction summary statistics filename',
                                     'summary statistics output filename']:
                            config.prediction_summary_output_filename = value
                            config.compute_prediction_statistics = True

                        elif key in ['annual_summary_statistics_output_filename',
                                     'annual_summary_statistics_filename',
                                     'annual summary statistics output filename',
                                     'annual summary statistics filename']:
                            config.prediction_summary_annual_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['monthly_summary_statistics_output_filename',
                                     'monthly_summary_statistics_filename',
                                     'monthly summary statistics output filename',
                                     'monthly summary statistics filename']:
                            config.prediction_summary_monthly_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['compute_seasonal_statistics',
                                     'seasonal_statistics',
                                     'compute seasonal statistics',
                                     'seasonal statistics']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.compute_seasonal_statistics = True
                            else: config.compute_seasonal_statistics = False

                        elif key in ['seasonal_statistics_output_filename',
                                     'seasonal_statistics_filename',
                                     'seasonal statistics output filename',
                                     'seasonal statistics filename']:
                            config.seasonal_statistics_output_filename = value
                            config.compute_seasonal_statistics = True

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
            if not self.__input_sample_filename: return False
            elif not self.samples:
                header, dt = io.read_flat_file(self.__input_sample_filename, separator=',')
                if dt:
                    for d in dt:
                        if len(d) != len(self.parameters): return False
                    self.samples = dt
                else: return False
            if not self.samples: return False

            # create parameter objects from parameter info file (if given)
            if self.__parameter_info_input_filename: self.parameters = Parameter.read_parameter_list(self.__parameter_info_input_filename, header=True)

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

        discharge_outlets, discharge_outlets_without_supbasin = [], []
        # step: compute disjoint basins (if applicable) and discharge outlet cells for all basins
        if self.disjoint_basin_extent:
            supbasins = Upstream.find_super_basin(outlets)

            discharge_outlets = Upstream.find_basin_discharge_cell(basins, supbasins)
            discharge_outlets_without_supbasin = Upstream.find_basin_discharge_cell(basins, {})
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
        cellnum_discharge, cellnum_discharge_without_supbasin = [], []
        for basin_outlets in discharge_outlets:
            cnums = []
            for cell in basin_outlets: cnums.append(gg.get_wghm_cell_number(cell[0], cell[1]))
            cellnum_discharge.append(cnums)

        for basin_outlets in discharge_outlets_without_supbasin:
            cnums = []
            for cell in basin_outlets: cnums.append(gg.get_wghm_cell_number(cell[0], cell[1]))
            cellnum_discharge_without_supbasin.append(cnums)

        # step: assign target cells in simulation variables
        for var in self.sim_variables:
            if not var.basin_cell_list:
                if var.basin_outlets_only:
                    if not var.boo_consider_super_basins:
                        var.basin_cell_list = cellnum_discharge_without_supbasin
                    else: var.basin_cell_list = cellnum_discharge
                else: var.basin_cell_list = basin_cellnum

            if not var.cell_weights and var.cell_area_as_weight: var.cell_weights = basin_cellareas

        # step: assign target cells in parameters
        unique_target_cells = []
        for basin in basin_cellnum: unique_target_cells += basin
        unique_target_cells = list(set(unique_target_cells))

        for param in self.parameters:
            if not param.cell_list: param.cell_list = unique_target_cells

        return succeed
