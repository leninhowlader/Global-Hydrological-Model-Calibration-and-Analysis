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
    '''
    [B] mode [calibration or sensitivity]
    [B] parameter_info_filename/parameter_info_input_filename

    [S] input_sample_filename/sample_filename

    [B] parallel_evaluation/do_parallel_evaluation
    [C] maximum_iteration

    [B] compute_upstream_from_station_file/upstream_from_station_file
    [B] disjoint_basin_extent

    [B] output_directory
    [C] calibration_output_filename/output_filename

    [C] save_parameter_values
    [C] parameter_value_output_filename


    [B] dump_model_prediction/save_model_prediction

    [B] compute_prediction_efficiency/compute_model_efficiency
    [B] model_efficiency_output_filename/prediction_efficiency_output_filename

    [B] compute_prediction_statistics/prediction_statistics
    [B] prediction_summary_statistics_filename/summary_statistics_output_filename
    [B] annual_statistics_output_filename/annual_statistics_filename
    [B] monthly_statistics_output_filename/monthly_statistics_filename

    [B] compute_seasonal_statistics/seasonal_statistics
    [B] seasonal_statistics_output_filename
    '''

    def __init__(self, mode='sensitivity'):
        self.__mode = mode
        self.__parameter_info_input_filename = ''
        self.__input_sample_filename = ''

        self.__do_parallel_evaluation = False
        self.__max_iterations = 0

        self.__compute_upstream_from_station_file = True
        self.__disjoint_basin_extent = True

        self.__output_directory = 'output'
        self.__calibration_result_output_filename = ''

        self.__save_parameter_values = False
        self.__parameter_value_output_filename = ''

        self.__dump_model_prediction = True

        self.__compute_prediction_efficiency = False
        self.__prediction_efficiency_output_filename = 'efficiency.dat'

        self.__compute_prediction_statistics = False
        self.__prediction_summary_monthly_output_filename = ''
        self.__prediction_summary_annual_output_filename = ''
        self.__prediction_summary_output_filename = ''

        self.__compute_seasonal_statistics = False
        self.__seasonal_statistics_output_filename = 'seasonal_statistics.csv'

        # NB: Prediction statistics and seasonal statistics will be merged
        # together in the future

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
    def save_parameter_values(self):
        return self.__save_parameter_values
    @save_parameter_values.setter
    def save_parameter_values(self, flag):
        self.__save_parameter_values = flag

    @property
    def parameter_value_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__parameter_value_output_filename)
    @parameter_value_output_filename.setter
    def parameter_value_output_filename(self, filename):
        self.__parameter_value_output_filename = filename


    @property
    def dump_model_prediction(self):
        return self.__dump_model_prediction
    @dump_model_prediction.setter
    def dump_model_prediction(self, flag):
        self.__dump_model_prediction = flag

    @property
    def maximum_iteration(self): return self.__max_iterations
    @maximum_iteration.setter
    def maximum_iteration(self, max_itarations):
        self.__max_iterations = max_itarations

    @property
    def compute_upstream_from_station_file(self):
        return self.__compute_upstream_from_station_file
    @compute_upstream_from_station_file.setter
    def compute_upstream_from_station_file(self, flag:bool):
        self.__compute_upstream_from_station_file = flag

    @property
    def disjoint_basin_extent(self):
        return self.__disjoint_basin_extent
    @disjoint_basin_extent.setter
    def disjoint_basin_extent(self, flag):
        self.__disjoint_basin_extent = flag

    @property
    def output_directory(self):
        return self.__output_directory
    @output_directory.setter
    def output_directory(self, directory):
        self.__output_directory = directory

    @property
    def calibration_result_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__calibration_result_output_filename)
    @calibration_result_output_filename.setter
    def calibration_result_output_filename(self, filename):
        self.__calibration_result_output_filename = filename

    @property
    def compute_prediction_efficiency(self):
        return self.__compute_prediction_efficiency
    @compute_prediction_efficiency.setter
    def compute_prediction_efficiency(self, flag):
        self.__compute_prediction_efficiency = flag

    @property
    def prediction_efficiency_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__prediction_efficiency_output_filename)
    @prediction_efficiency_output_filename.setter
    def prediction_efficiency_output_filename(self, filename):
        self.__prediction_efficiency_output_filename = filename

    @property
    def compute_seasonal_statistics(self):
        return self.__compute_seasonal_statistics
    @compute_seasonal_statistics.setter
    def compute_seasonal_statistics(self, flag):
        self.__compute_seasonal_statistics = flag

    @property
    def seasonal_statistics_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__seasonal_statistics_output_filename)
    @seasonal_statistics_output_filename.setter
    def seasonal_statistics_output_filename(self, filename):
        self.__seasonal_statistics_output_filename = filename

    @property
    def compute_prediction_statistics(self):
        return self.__compute_prediction_statistics
    @compute_prediction_statistics.setter
    def compute_prediction_statistics(self, flag):
        self.__compute_prediction_statistics = flag

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
                            if value == 'settings':
                                Configuration.read_settings(lines, config)

                            elif value == 'model-options':
                                WaterGAP.read_model_settings(lines)

                            elif (value == 'parameter' and
                                  len(config.parameters) == 0):
                                param_list = Parameter.read_parameters(lines)
                                if param_list: config.parameters = param_list

                            elif value == 'obs-variable':
                                config.obs_variables \
                                = ObsVariable.read_variables(lines)

                            elif value == 'sim-variable':
                                config.sim_variables \
                                = SimVariable.read_variables(lines)

                            elif value == 'derived-variable':
                                config.derived_variables \
                                    = DerivedVariable.read_variables(lines)
        except: config = None

        return config

    @staticmethod
    def read_settings(lines, config):
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

                        while key.find('  ') != -1: key = key.replace('  ', ' ')
                        while key.find(' ') != -1: key = key.replace(' ', '_')

                        if not (key and value): continue

                        if key in ['mode']: config.mode = value

                        elif key in ['parameter_info_input_filename',
                                     'parameter_info_filename']:
                            config.parameter_info_filename = value

                        elif key in ['input_sample_filename',
                                     'sample_filename']:
                            config.input_sample_filename = value

                        elif key in ['parallel_evaluation',
                                     'do_parallel_evaluation']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.parallel_evaluation = True
                            else: config.parallel_evaluation = False

                        elif key in ['maximum_iteration']:
                            try: max_iter = int(value)
                            except: max_iter = 0

                            config.maximum_iteration(max_iter)

                        elif key in ['compute_upstream_from_station_file',
                                     'upstream_from_station_file']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.compute_upstream_from_station_file = True
                            else:
                                config.compute_upstream_from_station_file \
                                = False

                        elif key in ['disjoint_basin_extent']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.disjoint_basin_extent = True
                            else: config.disjoint_basin_extent = False

                        elif key in ['output_directory']:
                            config.output_directory = value

                        elif key in ['calibration_output_filename',
                                     'output_filename']:
                            config.calibration_result_output_filename = value

                        elif key in ['save_parameter_values']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.save_parameter_values = True
                            else: config.save_parameter_values = False

                        elif key in ['parameter_value_output_filename']:
                            config.parameter_value_output_filename = value

                        elif key in ['dump_model_prediction',
                                     'save_model_prediction']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.dump_model_prediction = True
                            else: config.dump_model_prediction = False

                        elif key in ['compute_prediction_efficiency'
                                     'compute_model_efficiency']:
                            value = value.lower()
                            if value in ['true', 't', '1', 'yes', 'y']:
                                config.compute_prediction_efficiency = True
                            else: config.compute_prediction_efficiency = False

                        elif key in ['model_efficiency_output_filename'
                                     'prediction_efficiency_output_filename']:
                            config.prediction_efficiency_output_filename = value
                            config.compute_prediction_efficiency = True

                        elif key in ['compute_prediction_statistics'
                                     'prediction_statistics']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.compute_prediction_statistics = True
                            else: config.compute_prediction_statistics = False

                        elif key in ['prediction_summary_statistics_filename',
                                     'summary_statistics_output_filename']:
                            config.prediction_summary_output_filename = value
                            config.compute_prediction_statistics = True

                        elif key in ['annual_statistics_output_filename',
                                     'annual_statistics_filename']:
                            config.prediction_summary_annual_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['monthly_statistics_output_filename',
                                     'monthly_statistics_filename']:
                            config.prediction_summary_monthly_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['compute_seasonal_statistics',
                                     'seasonal_statistics']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.compute_seasonal_statistics = True
                            else: config.compute_seasonal_statistics = False

                        elif key in ['seasonal_statistics_output_filename']:
                            config.seasonal_statistics_output_filename = value
                            config.compute_seasonal_statistics = True

        return False

    def is_okay(self, skip_observation=False):
        '''
        This function checks the completeness of the configuration object. If
        the configuration object has observation variable(s), observation data
        will be read hear if skip observation flag is not set True. In case of
        sensitivity analysis, samples will be loaded.

        :return: (bool) true on completeness of the object;
                        false otherwise
        '''

        # step: check whether or not the station file is available when 'target cell from station file' flag is set ON
        if not (WaterGAP.station_filename and
                os.path.exists(os.path.join(WaterGAP.home_directory,
                                            WaterGAP.station_filename))):
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
