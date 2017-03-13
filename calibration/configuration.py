__author__ = 'mhasan'

import sys
sys.path.append('..')
from calibration.variable import ObsVariable, SimVariable, DerivedVariable
from calibration.watergap import WaterGAP
from calibration.parameter import Parameter
from utilities.fileio import read_flat_file

class Configuration:
    def __init__(self, mode='sensitivity'):
        self.__mode = mode

        # variables for sensitivity-mode
        self.input_file_for_parameters = ''
        self.sample_file = ''
        self.prediction_statistics = False

        self.monthly_prediction_summary_filename = 'prediction_summary_monthly.dat'
        self.yearly_prediction_summary_filename = 'prediction_summary_yearly.dat'
        self.prediction_summary_filename = 'prediction_summary.dat'
        self.prediction_efficiency_filename = 'prediction_efficiency.dat'

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
                            if value == 'sa-settings': Configuration.read_settings(lines, config)
                            elif value == 'settings': Configuration.read_calibration_settings(lines, config)
                            elif value == 'parameter' and config.get_mode() == 'calibration':
                                param_list = Parameter.read_parameters(lines)
                                if param_list: config.parameters = param_list
                            elif value == 'obs-variable': config.obs_variables = ObsVariable.read_variables(lines)
                            elif value == 'sim-variable': config.sim_variables = SimVariable.read_variables(lines)
                            elif value == 'model-options': WaterGAP.read_model_settings(lines)
                            elif value == 'derived-variable': config.derived_variables = DerivedVariable.read_variables(lines)
        except: config = None

        return config

    @staticmethod
    def read_settings(lines, config):
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
                        if key in ['prediction_summary_filename', 'prediction summary config_filename',  'prediction_summary',
                                   'prediction summary']:
                            config.prediction_summary_filename = value
                        elif key in ['monthly_summary_filename', 'monthly summary config_filename',  'month_summary',
                                   'monthly_summary', 'month summary', 'monthly summary']:
                            config.monthly_prediction_summary_filename = value
                        elif key in ['yearly_summary_filename', 'yearly summary config_filename', 'yearly_summary', 'yearly summary',
                                   'year_summary', 'year summary']: config.yearly_prediction_summary_filename = value
                        elif key in ['output_model_efficiency', 'output model efficiency', 'output_efficiency',
                                     'output efficiency']: config.prediction_efficiency_filename = value
                        elif key in ['input_parameter_list_filename', 'input_parameter_list', 'parameter_list',
                                     'input parameter list config_filename', 'input parameter list', 'parameter list']:
                            config.input_file_for_parameters = value
                        elif key in ['sample_list_file', 'sample list file', 'sample file', 'sample_file']:
                            config.sample_file = value
                        elif key in ['prediction_statistics', 'predictionstatistics']:
                            value = value.lower()
                            if value in ['true', 't', '1', 'yes', 'y']: config.prediction_statistics = True
                            else: config.prediction_statistics = False
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
                        elif key in ['save_simulation_output', 'save simulation output']:
                            config.set_prediction_output_filename(value)
                        elif key in ['save_param_values', 'save param values', 'save_param_value', 'save param value']:
                            config.set_paramvalue_filename(value)
                        elif key in ['save_function_values', 'save function values', 'save_function_value', 'save function value']:
                            config.set_model_efficiency_filename(value)
                        elif key in ['prediction_filename']:
                            config.set_calibration_output_filename(value)
                        elif key in ['parallel_evaluations', 'parallel_evaluation', 'parallel evaluations', 'parallel evaluation', 'parallel', 'parallelization']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']: config.set_parallel_evaluation_flag(True)
                            else: config.set_parallel_evaluation_flag(False)
        return False

    def is_okay(self):
        if self.sim_variables and len(self.sim_variables) == 0: return False
        else:
            if not self.sim_variables: return False
            for var in self.sim_variables:
                if not var.is_okay(): return False

        if self.obs_variables and len(self.obs_variables) > 0:
            if not ObsVariable.data_collection(self.obs_variables): return False
            else:
                if not self.obs_variables: return False
                for var in self.obs_variables:
                    if not var.is_okay(): return False

        if self.__mode == 'sensitivity':
            if not self.sample_file: return False
            elif not self.samples:
                header, dt = read_flat_file(self.sample_file, separator=',')
                if dt:
                    for d in dt:
                        if len(d) != len(self.parameters): return False
                    self.samples = dt
                else: return False

            if not self.samples: return False

            if not self.input_file_for_parameters: return False
            else: self.parameters = Parameter.read_parameter_list(self.input_file_for_parameters, header=True)

        if not self.parameters: return False
        if self.get_executable_name(): WaterGAP.executable = self.get_executable_name()
        else: return False

        return True
