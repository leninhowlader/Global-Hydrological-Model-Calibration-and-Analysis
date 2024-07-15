# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 13:56:40 2024

@author: H.M. Mehedi Hasan
@email: mehedi.hasan@gfz-potsdam.de
"""

import os, sys, numpy as np, pandas as pd
from copy import deepcopy

from core.configuration import Configuration
from core.parameter import Parameter
from analyses.borgoutput import BorgOutput
from wgap.watergap import WaterGAP
from utilities.fileio import FileInputOutput as io


config = None
path_experiment_home = ''
calunit_count = 0
repeat_count = 0
filename_config = ''
filename_solution_table = 'solution_table.csv'
all_stations_filename = 'STAIONS_5TESTCU.DAT'
world_size, world_rank = 0, -1
path_output = 'simulations'

class WaterGAPSimulation:
    @staticmethod
    def write_solution_table(
        path_experiment_home, calunit_count, repeat_count, filename_out
    ):
        df_out = pd.DataFrame()
        for i_calunit in range(calunit_count):
            
            for i_repeat in range(repeat_count):    
                f_outcome = os.path.join(
                    path_experiment_home,'output_%02d'%(i_repeat+1), 
                    'results_%02d.csv'%i_calunit
                )
                
                rr = BorgOutput.read_borg_output(f_outcome)
                
                t = pd.DataFrame(data=rr[:,0], columns=['solindex'])
                
                solution_ids = [
                    WaterGAPSimulation.create_solution_id(
                        i_calunit, i_repeat, x
                    ) for x in rr[:,0]
                ]
                t.insert(0, 'solution_id', solution_ids)
                
                t.insert(1, 'cuindex', i_calunit)
                t.insert(2, 'repindex', i_repeat)
                
                df_out = pd.concat((df_out, t), axis=0)
        
        df_out = df_out.reset_index(drop=True)
        df_out.to_csv(filename_out, index=False)
        
        return True
    
    @staticmethod
    def split_solution_id(solution_id):
        solution_id = '%d'%solution_id
        
        cuindex = int(solution_id[1:4])
        repeatindex = int(solution_id[4:6])
        solindex = int(solution_id[-5:])
        
        return cuindex, repeatindex, solindex
    
    @staticmethod
    def create_solution_id(cuindex, repeatindex, solindex):
        solution_id = int('1%03d%02d%05d'%(cuindex, repeatindex, solindex))
        
        return solution_id
    
    @staticmethod
    def get_staion_text(unit_id):
        
        f = os.path.join(WaterGAP.home_directory, all_stations_filename)
        
        line_text = ''
        try:
            file = open(f, 'r')
            lines = [l.strip() for l in file.readlines()]
            file.close()
            
            line_text = lines[unit_id] 
        except: pass
    
        return line_text     
    
    @staticmethod
    def write_station_file(unit_id):
        succeed = True
        
        f_station = 'STATIONS_%02d.DAT'%unit_id
        WaterGAP.model_config.station_filename = f_station
        
        f_station = os.path.join(WaterGAP.home_directory, f_station)
        if not os.path.exists(f_station):
            line_text = WaterGAPSimulation.get_staion_text(unit_id)
            
            if not line_text: return False
            
            file = open(f_station, 'w')
            file.write(line_text)
            file.close()
        
        return succeed
    
    @staticmethod
    def write_json_parameter_file(parameters, solution_id_text):
        filename = WaterGAP.get_json_parameter_filename()
        
        filename = (
            os.path.split(filename)[-1][:-5] + '_' + solution_id_text + '.json'
        )
        
        if WaterGAP.model_version == 'wghm2.2e':
            filename = os.path.join(
                WaterGAP.model_config.input_directory,
                filename
            )
            WaterGAP.model_config.parameter_filename = filename
    
            filename = os.path.join(WaterGAP.home_directory, filename)
        
        else: return False
            
        succeed = WaterGAP.update_parameter_file(parameters, filename)
        
        return succeed
    
    @staticmethod
    def get_simvar_copies(calunit_index):
        global config
        
        var_arr = []
        
        obj_arr_all, obj_arr_curr = [], []
        for (i, x) in enumerate(config.multiproblem_objective_index_list): 
            obj_arr_all += list(x)
            if i == calunit_index: 
                obj_arr_curr = list(x)
                break
        obj_arr_all = np.array(obj_arr_all)
        obj_arr_curr = np.array(obj_arr_curr)
        
        for var_index in np.unique(obj_arr_curr):
            sim_varname = config.obs_variables[var_index].counter_variable
            
            simvar = None
            for var in config.sim_variables:
                if var.varname == sim_varname:
                    simvar = deepcopy(var)
                    break
            
            # [ ] if target variable is not found in the sim-variables list, 
            #     examine the derived variable list
            if not simvar:
                for var in config.derived_variables:
                    if var.varname == sim_varname:
                        simvar = deepcopy(var)
                        break
            # [ ]
            
            m = (obj_arr_curr==var_index).sum()
            n = (obj_arr_all==var_index).sum()
            
            if simvar.basin_outlets_only:
                cell_list = []
                for x in simvar.basin_cell_list: cell_list += x
                
                simvar.basin_cell_list = [cell_list[n-m:n]]
            else: simvar.basin_cell_list = simvar.basin_cell_list[n-m:n]
            
            if simvar.cell_weights:
                simvar.cell_weights = simvar.cell_weights[n-m:n]
        
            var_arr.append(simvar)
        
        return var_arr
    
    @staticmethod
    def read_and_dump_watergap_output(var_arr, solution_id:int):
        global world_rank, path_experiment_home, path_output
        
        succeed = True
        
        dump_directory = os.path.join(path_experiment_home, path_output)
        if not os.path.exists(dump_directory): os.mkdir(dump_directory, 0o777)
        
        watergap_output_dir = os.path.join(
            WaterGAP.home_directory, WaterGAP.model_config.output_directory
        )
        
        for var in var_arr:
            succeed = var.cell_level_predicted_time_series(
                    start_year=WaterGAP.start_year,
                    end_year=WaterGAP.end_year,
                    prediction_directory=watergap_output_dir
                )
            
            if succeed: succeed = var.aggregate_prediction_at_spatial_scale()
            
            if succeed: var.do_anomaly_computation()
            
            var.apply_conversion_factor()
            
            succeed = var.dump_data_into_binary_file(
                    directory_out=dump_directory,
                    additional_filename_identifier=str(world_rank),
                    additional_attributes=[solution_id]
            )
            
            if not succeed: break
        
        return succeed
    
    @staticmethod
    def get_parameter_copies(calunit_index, repeat_index, solindex):
        global config, path_experiment_home
        
        param_indices = config.multiproblem_parameter_index_list[calunit_index]
        nparams = len(param_indices)
        
        f = os.path.join(
            path_experiment_home, 
            '%s_%02d'%(config.output_directory, repeat_index+1), 
            'results_%02d.csv'%calunit_index
        )
        
        rr = BorgOutput.read_borg_output(f)
        param_values = rr[solindex][1:nparams+1]
        
        parameter_list =[]
        for i in range(nparams):
            i_param = param_indices[i]
            
            param = Parameter()
            param.parameter_name = config.parameters[i_param].parameter_name
            
            param.parameter_value = param_values[i]
            param.cell_list=config.parameters[i_param].cell_list[calunit_index]
            parameter_list.append(param)
        
        return parameter_list
    
    @staticmethod
    def run(solution_id):
        text_solution_id = str(solution_id)
        
        calunit_index, repeat_index, solindex \
        = WaterGAPSimulation.split_solution_id(solution_id)
        
        # [+] create json parameter file
        parameter_list = WaterGAPSimulation.get_parameter_copies(
            calunit_index, repeat_index, solindex
        )
        
        arguments = {}
        succeed = WaterGAPSimulation.write_json_parameter_file(
            parameter_list, text_solution_id
        )
        # [.]
        
        # [+] create station file
        succeed = WaterGAPSimulation.write_station_file(calunit_index)
        # [.]
        
        # [+] create output directory
        if succeed:
            output_dir = 'output_' + text_solution_id
            if WaterGAP.temporary_output_directory:
                output_dir = os.path.join(WaterGAP.temporary_output_directory,
                                            output_dir)
            
            WaterGAP.model_config.output_directory = output_dir
            
            output_dir = os.path.join(WaterGAP.home_directory, output_dir)
            WaterGAP.create_output_directory(output_dir)
        # [.]
        
        # [+] write watergap configuration file
        mconfig_filename = os.path.join(
            WaterGAP.home_directory,
            '%s_%s.txt'%(WaterGAP.model_config_filename[:-4], text_solution_id)
        )
        
        succeed = WaterGAP.model_config.write_wgapConfig_file(mconfig_filename)
        arguments['c'] = os.path.split(mconfig_filename)[-1]
        # [.]
        
        # [+] run watergap
        if succeed:
            succeed = WaterGAP.execute_model(
                arguments, log_file='/dev/null', error_file='/dev/null'
            )
        # [.]
        
        # [+] read simulation output
        var_arr = WaterGAPSimulation.get_simvar_copies(calunit_index)
        if succeed: 
            succeed = WaterGAPSimulation.read_and_dump_watergap_output(
                var_arr, solution_id
            )
        # [.]
        
        # [+] remove simulation files
        WaterGAP.remove_files(arguments)
        # [.]
        
        return succeed
    
    @staticmethod
    def get_start_and_end_index(solution_count):
        global world_size, world_size
        
        x1 = solution_count % world_size
        x2 = solution_count // world_size
    
        if x1 != 0:
            if world_rank < x1:
                start_index = world_rank * x2 + world_rank
            else:
                start_index = world_rank * x2 + x1
        else:
            start_index = world_rank * x2
    
        end_index = start_index + x2 - 1
        if world_rank < x1: end_index += 1
    
        return start_index, end_index


def run_simulations(argv):
    global config, path_experiment_home, filename_config, calunit_count
    global repeat_count, filename_solution_table
    global world_size, world_rank
    
    try:
        path_experiment_home = argv[1]
        filename_config = argv[2]
        repeat_count = int(argv[3])
        if len(argv[:-2]) == 5: path_output = argv[4]
        world_size = int(argv[-2])
        world_rank = int(argv[-1])
    except: return -100

    os.chdir(path_experiment_home)
    
    f = os.path.join(path_experiment_home, filename_config)
    config = Configuration.read_configuration_file(f)
    
    if not config.is_okay(skip_observation=True) or not WaterGAP.is_okay(): 
        return 100
    
    calunit_count = len(config.multiproblem_parameter_index_list)
    
    f = os.path.join(path_experiment_home, filename_solution_table)
    if not os.path.exists(f):
        succeed = WaterGAPSimulation.write_solution_table(
            path_experiment_home=path_experiment_home, 
            calunit_count=calunit_count, 
            repeat_count=repeat_count,
            filename_out=f
        )
        if not succeed: return 200
    
    df = pd.read_csv(f)
    all_solution_ids = df['solution_id'].values
    solution_count = df.shape[0]
    
    start_index, end_index = WaterGAPSimulation.get_start_and_end_index(
        solution_count
    )
    
    solution_id = -1
    for i in range(start_index, end_index+1):
        solution_id = all_solution_ids[i]
        message = 'Solution %d is now under processing on processor %d'%(
            solution_id, world_rank
        )
        io.print_on_screen(message)
        
        succeed = WaterGAPSimulation.run(solution_id)
        if not succeed: return 300
        
    return 0

def test():
    global path_experiment_home, filename_config, calunit_count, repeat_count
    global path_output, world_size, world_rank
    
    path_experiment_home = os.path.join(
        '/mnt/d/mhasan/Experiments/POC_WB_II/poc_2024/test_experiments',
        '3Obj_NSEOU_With_PM'
    )
    
    filename_config = 'input/configuration_5CU_Experiemnt_NSEOU.txt'
    repeat_count = 5
    path_output = 'simulations'
    world_size = 5
    world_rank = 0

    filename_out = os.path.join(path_experiment_home, filename_solution_table)
    succeed = WaterGAPSimulation.write_solution_table(
        path_experiment_home=path_experiment_home, 
        calunit_count=calunit_count, 
        repeat_count=repeat_count,
        filename_out=filename_out
    )

    return 0
    
def dummy():
    text = """
    Before executing the entire script, please make sure all settings are 
    correct!!"""
    print(text)
    
    return 1
    
if __name__ == '__main__': run_simulations(sys.argv)