__author__ = 'mhasan'

import sys, os, numpy as np
from datetime import datetime

if '..' not in sys.path: sys.path.append('..')
from calibration.variable import ObsVariable, SimVariable, DerivedVariable
from wgap.watergap import WaterGAP
from calibration.parameter import Parameter
from utilities.fileio import FileInputOutput as io
from utilities.station import Station
from utilities.upstream import Upstream
from utilities.globalgrid import GlobalGrid as gg
from wgap.paraminfo import ParameterInfo
from calibration.stats import stats

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

        # sensitivity measure as the change in prediction from reference
        self.__as_change_in_prediction = True
        # function to measure the change
        self.__function = None

        self.obs_variables = []
        self.sim_variables = []
        self.derived_variables = []
        self.parameters = []
        self.samples = []

    @property
    def sensitivity_as_change_in_prediction(self):
        return self.__as_change_in_prediction
    @sensitivity_as_change_in_prediction.setter
    def sensitivity_as_change_in_prediction(self, flag:bool):
        self.__as_change_in_prediction = bool(flag)

    @property
    def function(self): return self.__function
    @function.setter
    def function(self, fun): self.__function = fun

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

                        if key in ['mode']: config.mode = value.lower()

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

                            config.maximum_iteration = max_iter

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
                        elif key in ['as_change_in_prediction']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.sensitivity_as_change_in_prediction = True
                            else:
                                config.sensitivity_as_change_in_prediction = False
                        elif key in ['function']:
                            fun = None
                            value = value.lower()
                            if value == 'rmse': fun = stats.root_mean_square_error
                            # else: value = None
                            config.function = fun

        return False

    def is_okay(self, skip_observation=False, error_code=False):
        # if error_code: return self.is_okay_errcode(skip_observation=skip_observation)
        # else: return not bool(self.is_okay_errcode(skip_observation=skip_observation))

        err = self.is_okay_errcode(skip_observation=skip_observation)
        if error_code: return err
        else:
            if err == 0: return True
            else: return False

    def is_okay_errcode(self, skip_observation=False):
        '''
        This function checks the completeness of the configuration object. If
        the configuration object has observation variable(s), observation data
        will be read hear if skip observation flag is not set True. In case of
        sensitivity analysis, samples will be loaded.

        :return: (int)  Error Code
                        0	no error
                        100 failed to create target cell list from stations in station file
                        200 absence of sim-variable
                        20x error in sim variable no. x
                        300 failed to acquire observation dataset
                        30x obs-variable no. x
                        40x error in derived variable no. x
                        501 Sample file not found
                        502 Samples could not be read from sample file
                        600 error in sensitivity method selection
                        700 absence of parameters
                        70x error in parameter no. x
        '''

        # step: check whether or not the station file is available when 'target cell from station file' flag is set ON
        if not (WaterGAP.station_filename and
                os.path.exists(os.path.join(WaterGAP.home_directory,
                                            WaterGAP.station_filename))):
            self.compute_upstream_from_station_file = False
            self.disjoint_basin_extent = False

        # step: read the target cells from station file, if applicable
        if self.compute_upstream_from_station_file:
            succeed = self.generate_target_cells_from_station_file()
            if not succeed: return 100

        # step: check completeness of simulation variables. there must at least be one simulation variable
        if not self.sim_variables: return 200
        else:
            varnum = 0
            for var in self.sim_variables:
                varnum += 1
                var.data_source.file_endian = WaterGAP.output_endian_type
                if not var.is_okay(): return (200 + varnum)

        # step: check completeness of observation variables (if any). Try to load the observation data
        if not skip_observation:
            if len(self.obs_variables) > 0:
                if not ObsVariable.data_collection(self.obs_variables): return 300

                varnum = 0
                for var in self.obs_variables:
                    varnum += 1
                    if not var.is_okay(): return (300 + varnum)

        # step: check completeness of derived variables (if any)
        if len(self.derived_variables) > 0:
            varnum = 0
            for var in self.derived_variables:
                varnum += 1
                if not var.is_okay(): return (400 + varnum)
                if not var.evaluate_equation(simvars=self.sim_variables, obsvars=self.obs_variables):
                    return (400 + varnum)

        # step: check if the samples can be gathered in case of sensitivity analysis mode. load the samples.
        # if parameter file is specified instead of defining individual parameters, create the parameter
        # object with provided information in the parameter info file.
        if self.__mode in ['sensitivity', 'glue']:
            # check the sample file and load samples
            if not self.__input_sample_filename: return 501
            elif not self.samples:
                header, dt = io.read_flat_file(self.__input_sample_filename, separator=',')
                if dt:
                    for d in dt:
                        if len(d) != len(self.parameters): return 502
                    self.samples = dt
                else: return 502
            if not self.samples: return 502

            # create parameter objects from parameter info file (if given)
            if self.__parameter_info_input_filename:
                self.parameters = Parameter.read_parameter_list(
                                        self.__parameter_info_input_filename,
                                        header=True
                )

            if self.__mode == 'sensitivity':
                if not (self.sensitivity_as_change_in_prediction or
                        len(self.obs_variables) > 0): return 600

        # step: check completeness of parameters
        if not self.parameters: return 700
        else:
            pnum = 0
            for param in self.parameters:
                pnum += 1
                if not param.is_okey(): return (700 + pnum)

        return 0

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

    @staticmethod
    def runtime_report(
        filename_config:str,
        filename_out:str
    ):
        f = open(filename_out, 'a')

        today = datetime.now()
        text = """
_______________________________________________________________________________
                Runtime Configuration-Object Correctness Test
                         [Written by: H.M. Mehedi]
_______________________________________________________________________________
Date: %s
    
Name of the File: %s
\n\n\n""" % (str(today), filename_config)
        f.write(text)

        if not os.path.exists(filename_config):
            message = 'configuration file does not exist: %s\n'%filename_config
            f.write(message)
            f.close()
            return -1

        config = Configuration.read_configuration_file(filename_config)
        if not config:
            message = 'wrong file format: %s\n'%filename_config
            f.write(message)
            f.close()
            return -1

        err_code = config.is_okay(error_code=True)
        if err_code == 0:
            message = 'configuration overall check  [okay]\n'
        else: message = 'configuration overall check  [failed: error %d]\n' % \
                        err_code
        f.write(message)

        # report general setting
        message = '\n[SECTION] BASIC SETTINGS:\n'
        f.write(message)

        message = '\tMode:%s\n' % config.mode
        f.write(message)

        message = '\tOuput directory: %s\n' % config.output_directory
        f.write(message)

        if not os.path.exists(config.output_directory):
            message = '\tOutput directory: [does not exist]\n'
        else: message = '\tOutput directory: [exists] \n'
        f.write(message)

        message = '\tSample filename: %s\n' % config.input_sample_filename
        f.write(message)

        message = '\tNumber of samples: %d\n'%len(config.samples)
        f.write(message)

        # report model settings
        message = '\n[SECTION] MODEL CONFIGURATION:\n'
        f.write(message)

        if WaterGAP.is_okay():
            message = '\tWaterGAP model overall check [okay]\n'
        else: message = '\tWaterGAP model overall check [failed]\n'
        f.write(message)

        if os.path.exists(WaterGAP.home_directory):
            message = '\tModel home directory: [exists]\n'
        else: message = '\tModel home directory: [does not exist]\n'
        f.write(message)

        message = '\tstart year: %d\n'%WaterGAP.start_year
        f.write(message)

        message = '\tend year: %d\n'%WaterGAP.end_year
        f.write(message)

        message = '\n[SECTION] PARAMETER:\n'
        f.write(message)

        message = '\tNumber of parameter: %d\n' % len(config.parameters)
        f.write(message)

        param_names = []
        for p in config.parameters: param_names.append(p.parameter_name)
        param_info = ParameterInfo.get_selected_paramter_info(param_names=param_names)

        param_acronyms = ','.join([param_info[p]['acronym'] for p in param_names])
        message = '\tparameter names: %s\n' % param_acronyms
        f.write(message)

        succeed = True
        for p in config.parameters:
            if (p.get_lower_bound() != param_info[p.parameter_name]['min'] or
                p.get_upper_bound() != param_info[p.parameter_name]['max']):
                succeed = False; break
        if succeed: message = '\tparameter range: [correct]\n'
        else: message = '\tparameter range: [not correct]\n'
        f.write(message)


        message = '\tnumber of grid cells: '
        temp = config.parameters[0].cell_list
        if len(temp) > 1:
            for p in config.parameters:
                counts =[len(x) for x in p.cell_list]

                f.write(message + '\n')

                message = '\t\t%s: %s [total = %d]'%(
                    p.parameter_name,
                    ', '.join([str(x) for x in counts]),
                    sum(counts)
                )
            f.write(message)
        else:
            for p in config.parameters:
                try: count = len(p.cell_list[0])
                except: count = 0
                message = '\n\t\t%s: total count = %d'%(
                    p.parameter_name, count
                )

                f.write(message)

        message = '\n[SECTION] VARIABLE:\n'
        f.write(message)

        message = '\tnumber of simulation variables: %d\n' % len(config.sim_variables)
        f.write(message)

        succeed = True
        for v in config.sim_variables:
            if not v.is_okay(): succeed = False; break
        if succeed:  message = '\tgeneral check for variables: [okay]\n'
        else: message = '\tgeneral check for variables: [not okay]\n'
        f.write(message)

        if False: # if succeed:
            # erroneous
            counts =[len(v.basin_cell_list) for v in config.sim_variables]
            if np.mean(counts) == counts[0]:
                message = '\tnumber of basin in variables: [consistent]\n'
                f.write(message)

                message='\tnumber of basin: %d\n'%counts[0]
            else: message = '\tnumber of basin in variables: [not consistent]\n'
            f.write(message)

            succeed = True
            varlist = [v for v in config.sim_variables if len(v.basin_cell_list[0]) > 1]

            counts =[[len(v.basin_cell_list[i]) for i in range(len(v.basin_cell_list))]
                     for v in varlist]
            if np.abs(np.array(counts).mean(axis=0)-np.array(counts[0])).sum() != 0:
                succeed = False

            if succeed:
                counts =[np.array(v.basin_cell_list).size for v in varlist]
                if np.mean(counts) != counts[0]: succeed = False

            if succeed: message = '\ttarget cell list: [consistent]\n'
            else: message = '\ttarget cell list: [not consistent]\n'
            f.write(message)

            succeed = True
            for v in config.sim_variables:
                if len(v.cell_weights) != 0:

                    weight_counts = [len(v.cell_weights[i]) for i in range(len(v.cell_weights))]
                    cell_counts = [len(v.basin_cell_list[i]) for i in range(len(v.basin_cell_list))]

                    if np.abs(np.array(weight_counts)-np.array(cell_counts)).sum() == 0:
                        f.write('\t[%s] cell counts: [consistent]\n' % v.varname)
                    else: f.write('\t[%s] cell counts: [not consistent]\n' % v.varname)

                    weight_sums = [np.sum(v.cell_weights[i]) for i in range(len(v.cell_weights))]

                    message = '\t[%s] area sum: %s\n' % (v.varname, ','.join([str(x) for x in weight_sums]))
                    f.write(message)

        message = '\n\nreport success!!\n'
        f.write(message)
        f.close()

        return True
