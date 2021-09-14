__author__ = 'mhasan'

import json, os, sys
sys.path.append('..')
from copy import deepcopy
from utilities.enums import FileEndian, PredictionType
from subprocess import call
import shutil
from calibration.variable import DataCloud
from calibration.stats import stats
from collections import OrderedDict
from utilities.globalgrid import GlobalGrid as gg
from wgap.wgapconfig import WaterGapConfig

class DirInfo:
    def __init__(self):
        self.input_directory = ''
        self.output_directory = ''
        self.routing_directory = ''
        self.metdata_directory = ''
        self.additional_metdata_directory = ''

    def is_okay(self):
        if (self.input_directory and self.output_directory and self.routing_directory and
            self.metdata_directory and self.additional_metdata_directory): return True
        else: return False

    def create_directory_file(self, filename):
        succeed = True

        f = None
        try:
            f = open(filename, 'w')
            f.write(self.input_directory + '\n' + self.output_directory + '\n' + self.metdata_directory + '\n' +
                    self.routing_directory + '\n' + self.additional_metdata_directory)
        except: succeed = False
        finally:
            try: f.close()
            except: pass

        return succeed

    @staticmethod
    def read_directory_file(filename):
        dir_info = DirInfo()

        f = None
        try:
            f = open(filename, 'r')
            dir_info.input_directory = f.readline().strip('\n')
            dir_info.output_directory = f.readline().strip('\n')
            dir_info.metdata_directory = f.readline().strip('\n')
            dir_info.routing_directory = f.readline().strip('\n')
            dir_info.additional_metdata_directory = f.readline().strip('\n')
        except: return None
        finally:
            try: f.close()
            except: pass

        if dir_info.is_okay(): return dir_info
        else: return None

class WaterGAP:
    home_directory = ''
    json_parameter_file = ''
    directory_filename = ''
    executable = ''
    start_year = 1901
    end_year = 2100
    output_endian_type = FileEndian.big_endian
    log_directory = ''

    __system_arguments = ''

    model_version = ''
    ngc = -1

    json_paramset = None
    dir_info = None

    station_filename = ''

    remove_waterGap_files_after_evaluation = True

    model_config_filename = ''
    model_config = None

    @staticmethod
    def get_json_parameter_filename():
        param_filename = ''
        if WaterGAP.model_version == 'wghm22e':
            if WaterGAP.model_config.parameter_filename:
                param_filename = os.path.join(
                    WaterGAP.home_directory,
                    WaterGAP.model_config.parameter_filename
                )
        else:
            if WaterGAP.json_parameter_file:
                param_filename = os.path.join(
                    WaterGAP.home_directory,
                    WaterGAP.dir_info.input_directory,
                    WaterGAP.json_parameter_file
                )

        return param_filename

    @staticmethod
    def set_system_arguments(argument_str):
        WaterGAP.__system_arguments = argument_str

    @staticmethod
    def get_argument_string(): return WaterGAP.__system_arguments

    @staticmethod
    def set_model_version(version):
        if (version in ['wghm22b', 'wghm22d', 'wghm22e'] and
            version != WaterGAP.model_version):
            WaterGAP.model_version = version

            # set version to GlobalGrid class
            # note that version wghm22d and wghm22e use the same grid configuration
            if version == 'wghm22e': version = 'wghm22d'
            gg.set_model_version(version)
            if WaterGAP.ngc <= 0: WaterGAP.ngc = gg.get_wghm_cell_count()

    @staticmethod
    def get_model_version(): return WaterGAP.model_version

    @staticmethod
    def set_station_filename(filename:str): WaterGAP.station_filename = filename

    @staticmethod
    def get_station_filename(): return WaterGAP.station_filename

    @staticmethod
    def get_grid_cell_count(): return WaterGAP.ngc

    @staticmethod
    def is_okay():
        if not(WaterGAP.home_directory and WaterGAP.executable): return False

        if WaterGAP.model_version == 'wghm22e':
            if not WaterGAP.model_config:
                mconfig = WaterGapConfig.read_watergap_config_file(
                            os.path.join(WaterGAP.home_directory,
                                         WaterGAP.model_config_filename)
                )
                if mconfig: WaterGAP.model_config = mconfig
                else: return False
        else:
            if not WaterGAP.dir_info:
                dinfo = DirInfo.read_directory_file(
                                os.path.join(WaterGAP.home_directory,
                                             WaterGAP.directory_filename)
                )

                if dinfo: WaterGAP.dir_info = dinfo
                else: return False

        if not WaterGAP.json_paramset:
            parameter_filename = WaterGAP.get_json_parameter_filename()

            if not WaterGAP.read_json_parameter_file(parameter_filename):
                return False

        if WaterGAP.log_directory:
            log_directory = os.path.join(WaterGAP.home_directory,
                                         WaterGAP.log_directory)

            if not os.path.exists(log_directory): os.mkdir(log_directory, 0o777)
        return True

    @staticmethod
    def update_parameter_file(parameter_list, filename):
        succeed = True

        if not (parameter_list and filename): succeed = False
        else:
            if not WaterGAP.json_paramset:
                parameter_filename = WaterGAP.get_json_parameter_filename()
                if parameter_filename:
                    WaterGAP.read_json_parameter_file(parameter_filename)

            if not WaterGAP.json_paramset: succeed = False
            else:
                param_set = deepcopy(WaterGAP.json_paramset)

                for param in parameter_list:
                    try:
                        key = param.parameter_name
                        value = param_set[key]
                        param_value = param.get_parameter_value()
                        if type(value) is list:
                            if param.has_multiple_cells() and param.get_single_value_flag():
                                clist = param.get_cell_list()
                                if clist:
                                    temp = []
                                    for c in clist:
                                        if type(c) is list: temp+= c
                                        else: temp.append(c)
                                    clist = temp
                                for c in clist: value[c-1] = param_value
                            else:
                                for i in range(len(value)): value[i] = param_value
                        else: param_set[key] = param_value
                    except:
                        succeed = False
                        break

                if succeed:
                    f = None
                    try:
                        f = open(filename, 'w')
                        json.dump(param_set, f)
                    except: succeed = False
                    finally:
                        try: f.close()
                        except: pass
        return succeed

    @staticmethod
    def read_json_parameter_file(filename):
        succeed = True

        if filename:
            f = None
            try:
                f = open(filename, 'r')
                WaterGAP.json_paramset = json.load(f, object_pairs_hook=OrderedDict)
            except: succeed = False
            finally:
                try: f.close()
                except: pass
        else: succeed = False

        return succeed

    @staticmethod
    def read_model_settings(list_of_lines):
        succeed = True
        try:
            while list_of_lines:
                line = list_of_lines.pop(0).strip()
                temp = line.split()
                temp[0] = temp[0].strip().lower()
                if temp[0] == 'end': return succeed
                else:
                    temp = line.split('=')
                    if len(temp) == 2:
                        key, value = temp[0].strip().lower(), temp[1].strip()

                        if key in ['home_directory', 'home output_directory']:
                            WaterGAP.home_directory = value
                        elif key in ['wgap_config_filename',
                                     'wgap config filename']:
                            WaterGAP.model_config_filename = value
                            if WaterGAP.model_version != 'wghm22e':
                                WaterGAP.set_model_version('wghm22e')
                        elif key in ['system_arguments', 'arguments']:
                            WaterGAP.set_system_arguments(value)

                        elif key in ['parameter_file', 'parameter_filename',
                                     'parameter file',
                                     'parameter config_filename']:
                            WaterGAP.json_parameter_file = value
                        elif key in ['start_year', 'start year']:
                            try: WaterGAP.start_year = int(value)
                            except: pass
                        elif key in ['end_year', 'end year']:
                            try: WaterGAP.end_year = int(value)
                            except: pass
                        elif key in ['datadir_filename', 'directory_file',
                                     'directory_filename',
                                     'datadir config_filename',
                                     'output_directory file',
                                     'output_directory config_filename',
                                     'data_directory_file',
                                     'data output_directory file']:
                            WaterGAP.directory_filename = value
                        elif key in ['log_directory', 'log directory', 'log']:
                            WaterGAP.log_directory = value
                        elif key in ['output_endian_type', 'output endian type',
                                     'endian_type', 'endian type']:
                            if value == '1':
                                WaterGAP.output_endian_type = FileEndian.little_endian
                            else: WaterGAP.output_endian_type = FileEndian.big_endian
                        elif key in ['executable', 'model_executable', 'model',
                                     'model executable', 'executable_name',
                                     'executable name']:
                            WaterGAP.executable = value
                        elif key in ['grid_cell_count', 'grid cell count',
                                     'ng', 'ngc']:
                            try: WaterGAP.ngc = int(value)
                            except: pass
                        elif key in ['station_file', 'station_filename',
                                     'station file', 'station filename']:
                            WaterGAP.station_filename = value
                        elif key in ['model_version', 'model version']:
                            WaterGAP.set_model_version(value)
                        elif key in ['remove_modelfiles_after_evaluation',
                                     'remove modelfiles after evaluation']:
                            if value.lower() in ['n', 'no', 'false', 'f', '0']:
                                WaterGAP.remove_waterGap_files_after_evaluation \
                                = False

        except: succeed = False

        return succeed

    @staticmethod
    def execute_model(arguments={}, log_file='', error_file=''):
        succeed = True

        arg_str = ''
        if WaterGAP.model_version == 'wghm22e':
            # key 'c' should provide model config file
            arg_str += ' ' + arguments['c']
        else:
            for key in arguments.keys():
                arg_str += ' -' + key.lower() + ' ' + arguments[key]

        command_str = os.path.join(WaterGAP.home_directory,
                                   WaterGAP.executable) + arg_str

        if log_file: command_str += ' > ' + log_file
        if error_file: command_str += ' 2> ' + error_file

        try: call(command_str, shell=True)
        except: succeed = False

        return succeed

    @staticmethod
    def update_directory_info(output_dir, directory_filename):
        succeed = True
        if not (WaterGAP.dir_info or WaterGAP.directory_filename): succeed = False
        else:
            if not WaterGAP.dir_info:
                WaterGAP.dir_info = DirInfo.read_directory_file(
                                                    WaterGAP.directory_filename)

            if WaterGAP.dir_info:
                WaterGAP.dir_info.output_directory = output_dir

                directory_filename = os.path.join(WaterGAP.home_directory,
                                                  directory_filename)

                if not WaterGAP.dir_info.create_directory_file(directory_filename): succeed = False
            else: succeed = False

        return succeed

    @staticmethod
    def create_output_directory(output_directory):
        if not os.path.exists(output_directory):
            os.mkdir(output_directory, 0o777)

    @staticmethod
    def remove_files(arguments={}):
        if WaterGAP.remove_waterGap_files_after_evaluation:
            try:
                output_dir = ''
                if WaterGAP.model_version == 'wghm22e':
                    parameter_file = os.path.join(
                                        WaterGAP.home_directory,
                                        WaterGAP.model_config.parameter_filename
                    )
                    os.remove(parameter_file)

                    config_file = os.path.join(WaterGAP.home_directory,
                                               arguments['c'])
                    os.remove(config_file)

                    output_dir = os.path.join(
                                        WaterGAP.home_directory,
                                        WaterGAP.model_config.output_directory
                    )
                else:
                    parameter_file = \
                    os.path.join(WaterGAP.home_directory,
                                 WaterGAP.dir_info.input_directory, arguments['p'])

                    dir_file = os.path.join(WaterGAP.home_directory, arguments['d'])
                    os.remove(parameter_file)
                    os.remove(dir_file)

                    output_dir = \
                    os.path.join(WaterGAP.home_directory,
                                 WaterGAP.dir_info.output_directory)
                shutil.rmtree(output_dir)
            except: return False

        return True

    @staticmethod
    def read_predictions(sim_vars, output_directory_name=''):
        '''
        This method reads model predictions for all simulation variables.

        Parameters:
        :param sim_vars: (list of SimVariable)  list of simulation variables
        :param output_directory_name: (string; optional) path of model output directory
        :return: (bool) True on success,
                        False otherwise
        '''

        # step: if not provided, get output directory name from directory object of WaterGAP static class
        if not output_directory_name: output_directory_name = WaterGAP.dir_info.output_directory
        output_directory_name = os.path.join(WaterGAP.home_directory, output_directory_name)

        # step: update file endian in variable object and read data using data collection method
        succeed = True
        for var in sim_vars:
            # var.data_source.filename = os.path.join(output_directory_name, var.data_source.filename)
            var.data_source.file_endian = WaterGAP.output_endian_type
            succeed = var.data_collection(WaterGAP.start_year, WaterGAP.end_year, prediction_directory=output_directory_name)
            if not succeed: break

        return succeed

    @staticmethod
    def prediction_efficiency(sim_vars, obs_vars, iter_no=-1):
        results = []
        for obs_var in obs_vars:
            for sim_var in sim_vars:
                if (obs_var.counter_variable == sim_var.varname):
                    sim, obs = DataCloud.cloud_coupling(sim_var.data_cloud, obs_var.data_cloud)
                    if sim and obs:
                        s, r = stats.all_efficiencies(sim, obs)
                        results.append([iter_no, obs_var.varname, sim_var.varname] + r)
                    break
        return results

    @staticmethod
    def prediction_statistics(sim_vars, funs=['mean', 'std', 'min', 'max', 'q1', 'median', 'q3']):
        basic_summary, month_summary, year_summary = OrderedDict(), OrderedDict(), OrderedDict()

        for var in sim_vars:
            results = []
            if var.group_stats:
                ndx_str, ndx_end = 0, 0
                for i in range(len(var.cell_groups)):
                    ndx_end += len(var.cell_groups[i])
                    r = [i+1] + stats.multiple_statistics(var.data_cloud.crop([0], [i+1]), funs)
                    results.append(r)
                    ndx_str = ndx_end
            else: results.append(stats.multiple_statistics(var.data_cloud.data, funs))
            basic_summary[var.varname] = results

            if var.data_source.prediction_type == PredictionType.monthly:
                if var.group_stats:
                    results = var.data_cloud.group_stat([0, 2], funs)
                    month_summary[var.varname] = results

                    results = var.data_cloud.group_stat([0, 1], funs)
                    year_summary[var.varname] = results
                else:
                    results = var.data_cloud.group_stat([2], funs)
                    month_summary[var.varname] = results

                    results = var.data_cloud.group_stat([1], funs)
                    year_summary[var.varname] = results

        return basic_summary, month_summary, year_summary