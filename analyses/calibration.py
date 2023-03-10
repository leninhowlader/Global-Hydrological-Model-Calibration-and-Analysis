import os, sys, numpy as np
from collections import OrderedDict
from datetime import datetime

from core.configuration import Configuration
from wgap.watergap import WaterGAP
from core.stats import stats
from core.variable import DataCloud
from algorithm.borg import *
from utilities.fileio import FileInputOutput

class Calibration:
    __nvars = 0
    __nobjs = 0
    __nconts = 0

    __world_rank = -1
    __world_size = 0
    __config = None

    __consistency_check = False
    __id_local = 0

    @staticmethod
    def get_nvars(): return Calibration.__nvars
    @staticmethod
    def set_nvars(nvars:int): Calibration.__nvars = nvars

    @staticmethod
    def get_nobjs(): return Calibration.__nobjs
    @staticmethod
    def set_nobjs(nobjs:int): Calibration.__nobjs = nobjs

    @staticmethod
    def get_nconts(): return Calibration.__nconts
    @staticmethod
    def set_nconts(nconts:int): Calibration.__nconts = nconts

    @staticmethod
    def get_world_rank(): return Calibration.__world_rank
    @staticmethod
    def set_world_rank(rank:int): Calibration.__world_rank = rank

    @staticmethod
    def get_world_size(): return Calibration.__world_size
    @staticmethod
    def set_world_size(world_size:int): Calibration.__world_size = world_size

    @staticmethod
    def get_calibration_configurations(): return Calibration.__config
    @staticmethod
    def set_calibration_configurations(config:Configuration):
        Calibration.__config = config

        Calibration.__nvars = config.get_parameter_count()
        Calibration.__nobjs = config.get_objective_count()
        Calibration.__nconts = config.get_constraints_count()
        
    
    @staticmethod
    def is_okay():
        if not Calibration.__consistency_check:
            nvars = Calibration.__nvars
            nobjs, nconts = Calibration.__nobjs, Calibration.__nconts

            world_rank = Calibration.__world_rank
            world_size = Calibration.__world_size

            config = Calibration.__config
            if not (nvars > 0 and nobjs > 0 and world_rank > 0 and 
                    world_size > 0): Calibration.__consistency_check = False
            else: Calibration.__consistency_check = config.is_okay()
        
        return Calibration.__consistency_check            

    @staticmethod
    def model_evaluation(*vars):
        # [step-x]: Preparation, information gathering
        nvars = Calibration.__nvars
        nobjs, nconts = Calibration.__nobjs, Calibration.__nconts
        objs, conts = [np.nan] * nobjs, [np.nan] * nconts

        config = Calibration.__config
        my_rank = Calibration.__world_rank
        
        succeed = True
        messages = []
        arguments = OrderedDict()

        # assign id for each model run
        Calibration.__id_local += 1
        evaluation_num = int(my_rank * 1e5 + Calibration.__id_local)
        filename_specifier = '%s_%d'%(config.experiment_name, evaluation_num)
        #

        messages.append(
            '\n\nModel evaluation started with ID-%d:'%evaluation_num)
        t0 = datetime.now()
        # end [step-x]


        ## [step-x]: update parameters
        Calibration.update_parameters(vars)
        for i in range(nvars):
            param = Calibration.__config.parameters[i]
            messages.append('\t(%02d) %s: %f'%(
                i, param.parameter_name.ljust(40), param.parameter_value))
        
        filename = WaterGAP.get_json_parameter_filename()
        filename = os.path.split(filename)[-1][:-5] + '_' \
                    + filename_specifier + '.json'
        
        if WaterGAP.model_version == 'wghm2.2e':
            filename = os.path.join(
                WaterGAP.model_config.input_directory,
                filename
            )
            WaterGAP.model_config.parameter_filename = filename

            filename = os.path.join(WaterGAP.home_directory, filename)
        else:
            arguments['p'] = filename
            filename = os.path.join(
                WaterGAP.home_directory,
                WaterGAP.dir_info.input_directory,
                filename
            )
        
        if not WaterGAP.update_parameter_file(config.parameters, filename):
            return (objs, conts)
        ## end [step-x]

        # [step-x]: create output directory (and directory file)
        output_dir = 'output_' + filename_specifier
        if WaterGAP.temporary_output_directory:
            output_dir = os.path.join(WaterGAP.temporary_output_directory,
                                        output_dir)
                                        
        if WaterGAP.model_version == 'wghm2.2e':
            WaterGAP.model_config.output_directory = output_dir
        else:
            dir_filename = 'data_' + filename_specifier + '.dir'
            if not WaterGAP.update_directory_info(output_dir, dir_filename):
                return (objs, conts)
            arguments['d'] = dir_filename

        output_dir = os.path.join(WaterGAP.home_directory, output_dir)
        WaterGAP.create_output_directory(output_dir)
        # end [step-x]

        # [step-x]: write model configuration file for WaterGap2.2e
        if WaterGAP.model_version == 'wghm2.2e':
            mconfig_filename = os.path.join(
                    WaterGAP.home_directory,
                    '%s_%s.txt'%(WaterGAP.model_config_filename[:-4],
                                    filename_specifier)
            )

            if not WaterGAP.model_config.write_wgapConfig_file(
                    mconfig_filename): return (objs, conts)

            arguments['c'] = os.path.split(mconfig_filename)[-1]
        # end [step-x]
        
        # [step-x]: generate log and error filenames
        if WaterGAP.log_directory:
            log_file = os.path.join(
                    WaterGAP.home_directory, WaterGAP.log_directory,
                    '%s.log'%filename_specifier
            )
            error_file = os.path.join(
                    WaterGAP.home_directory, WaterGAP.log_directory,
                    '%s.err'%filename_specifier
            )
        else:
            log_file = '/dev/null'
            error_file = '/dev/null'
        # end [step-x]

        # [step-x]: execute model with new parameters
        t1 = datetime.now()
        messages.append('\tModel execution started at %s'%str(t1))
        if not WaterGAP.execute_model(
            arguments, log_file=log_file, error_file=error_file):
            WaterGAP.remove_files(arguments)
            return (objs, conts)
        t2 = datetime.now()
        messages.append('\tExecution ended at %s'%str(t2))
        messages.append(
            '\tTotal duration (in min): %0.2f'%((t2-t1).total_seconds()/60))
        # end [step-x]

        # [step-x] read simulation output
        succeed = True
        for var in config.sim_variables:
            try:
                succeed = var.cell_level_predicted_time_series(
                    start_year=WaterGAP.start_year,
                    end_year=WaterGAP.end_year,
                    prediction_directory=output_dir
                )
            except:
                succeed = False

            # [sub-step] compute spatial summary
            if succeed: succeed = var.aggregate_prediction_at_spatial_scale()
            # [end]

            # [sub-step] compute anomaly
            if succeed: succeed = var.do_anomaly_computation()
            # [end]
            
            if not succeed: break

        if not succeed: return (objs, conts)
        
        ## compute values of derived variable
        for var in config.derived_variables:
            var.derive_data(simvars=config.sim_variables)
        # end [step-x]
        
        # [step-x] compute objectives
        # 
        temp = Calibration.compute_objectives()
        if len(temp) == nobjs:
            for i in range(nobjs): objs[i] = temp[i]
        messages.append('\tObjectives: %s'%(','.join(
                                    ['%0.2f'%temp[i] for i in range(nobjs)])))
        # end [step-x]

        # [step-x] compte constraints
        temp = Calibration.compute_constraints()
        if len(temp) == nconts:
            for i in range(nconts): conts[i] = temp[i]
        messages.append('\tConstraints: %s'%(','.join(
                                    ['%0.2f'%temp[i] for i in range(nconts)])))
        # end [step-x]

        # [step-x] remove simulation output files
        WaterGAP.remove_files(arguments)
        # end [step-x]

        # [step-x] write predictions, parameter values, objectives etc..
        Calibration.write_parameter_values(evaluation_num=evaluation_num)
        Calibration.write_objective_values(evaluation_num, objs)
        # end [step-x]

        t3 = datetime.now()
        messages.append(
            '\tTotal duration of model evaluation [in min]: %0.2f'
            %((t3-t0).total_seconds()/60)
        )

        #for line in messages: print(line, file=sys.stdout)
        FileInputOutput.print_on_screen(messages)
        
        return (objs, conts)
    
    @staticmethod
    def compute_objectives():
        objs = []
        config = Calibration.__config

        for obsvar in config.obs_variables:
            var = None
            target = obsvar.counter_variable
            
            for simvar in config.sim_variables:
                if simvar.varname == target:
                    var = simvar
                    break
            
            if not var:
                for dervar in config.derived_variables:
                    if dervar.varname == target:
                        var = dervar
                        break
            
            if not var: 
                objs.append(np.nan)
                continue
            
            fun = obsvar.function
            ii, jj = DataCloud.index_coupling(
                obsvar.data_cloud,
                var.data_cloud
            )

            obs = obsvar.data_cloud.data[ii]
            sim = var.data_cloud.data[jj]
            
            if ((sim.ndim == 1 or sim.shape[1] == 1) and 
                (obs.ndim == 1 or obs.shape[1] == 1)):
                # this is the usual case where we would have one observation 
                # time-series to be compared with only one simulation series

                obs = obs.flatten()
                sim = sim.flatten()
                f = stats.objective_function(
                        fun=fun, 
                        sim=sim, 
                        obs=o
                    )
                objs.append(f)

            if obs.ndim == 2 and (sim.ndim == 1 or sim.shape[1] == 1):
                # this case might arrise when observation is perturbed with in 
                # the confidence interval. in such a case, no. of objectives 
                # would depend on the number of perturbed observation 
                # time-series.
                #  
                # note that in this case simulation data array must not contain
                # more than one time-series (e.g., time-series for each cell in
                # a basin)    

                sim = sim.flatten()
                for i in range(obs.shape[1]):
                    o = obs[:, i].flatten()
                    f = stats.objective_function(
                        fun=fun, 
                        sim=sim, 
                        obs=o
                    )
                    objs.append(f)

            elif obs.ndim == 2 and sim.ndim == 2 and obs.shape[1] == sim.shape[1]:
                # When obs contains multiple time-series for different units, 
                # say for each cell or for multiple basins, this case will apply.
                # sim must contain simulation values for corresponding cells or
                # basins
                for i in range(obs.shape[1]):
                    o = obs[:, i].flatten()
                    for j in range(sim.shape[1]):
                        s = sim[:, j].flatten()
                        f = stats.objective_function(fun=fun, sim=s, obs=o)
                        objs.append(f)
            
            else: objs.append(np.nan)

        return objs

    @staticmethod
    def compute_constraints():
        conts = []

        # to be added

        return conts

    @staticmethod
    def update_parameters(vars):
        config = Calibration.__config
        
        for i in range(len(vars)):
            config.parameters[i].parameter_value = vars[i]
    
    @staticmethod
    def write_parameter_values(evaluation_num):
        filename = Calibration.__config.parameter_value_output_filename
        if filename:
            filename = '%s_%d_.%s'%(
                filename[:-4], Calibration.__world_rank, filename[-3:]
            )

            values = [evaluation_num] +  [
                p.parameter_value for p in  Calibration.__config.parameters]

            f = open(filename, 'a')
            f.write(','.join([str(x) for x in values]) + '\n')
            f.close()
    
    @staticmethod
    def write_objective_values(evaluation_num, objs):
        filename = Calibration.__config.objective_values_output_filename
        if filename:
            filename = '%s_%d_.%s'%(
                filename[:-4], Calibration.__world_rank, filename[-3:]
            )

            values = [str(evaluation_num)] + [
                str(x) for x in objs
            ]
            
            f = open(filename, 'a')
            f.write(','.join(values) + '\n')
            f.close()

class BorgMOEA:
    __libborg_path = './algorithm/libborg.so'
    __libmpi_path = './algorithm/libmpi.so' 
    __libstdc_path = ''
    
    __poc_config = None
    __borg_problem_array = []
    __nproblems = 1         # Number of optimization problems

    @staticmethod
    def set_borg_library(path): BorgMOEA.__libborg_path = path 

    @staticmethod
    def set_mpi_library(path): BorgMOEA.__libmpi_path = path

    @staticmethod
    def set_stdandard_C_library(path): BorgMOEA.__libstdc_path = path

    @staticmethod
    def set_calibration_configuration(poc_config): 
        BorgMOEA.__poc_config = poc_config

    @staticmethod
    def BORG_Optimization_Problem_Create(poc_config, eval_func):
        succeed = True
        
        nvars = poc_config.get_parameter_count()
        nobjs = poc_config.get_objective_count()
        nconts = poc_config.get_constraints_count()

        is_one_problem = poc_config.single_problem_mode
        if is_one_problem:
            problem = Borg(nvars, nobjs, nconts, function=eval_func)

            # set bounds of decision variables
            lower_bound, upper_bound = poc_config.get_parameter_bounds()
            bounds = [[lower_bound[i], upper_bound[i]] for i in range(nvars)]
            problem.setBounds(*bounds)
            # [end]

            # set epsilons for objectives
            epsilons = poc_config.get_epsilons()
            problem.setEpsilons(*epsilons)
            # [end]

            BorgMOEA.__borg_problem_array.clear()
            BorgMOEA.__borg_problem_array.append(problem)
            BorgMOEA.__nproblems = 1

        BorgMOEA.__poc_config = poc_config

        return succeed
    
    @staticmethod
    def BORG_Problem_Description(config_poc, out = sys.stdout):
        print('Problem definition:', file=out)

        line = '\tModel parameter(s):'.ljust(56) + 'Min'.ljust(10) + 'Max'.ljust(10)
        print(line, file=out)
        
        for param in config_poc.parameters:
            line = ('\t\t' + param.parameter_name.ljust(40) 
                    + str(param.get_lower_bound()).rjust(10) 
                    + str(param.get_upper_bound()).rjust(10))
            print(line, file=out)

        print('\n\tVariables:', file=out)
        line = '\tObservation Variables'.rjust(35) + 'Prediction variable'.rjust(35)
        print(line, file=out)

        line = '--------------------'.rjust(35) + '--------------------'.rjust(35)
        print(line, file=out)

        for i in range(len(config_poc.obs_variables)):
            var = config_poc.obs_variables[i]
            line = ('\t\t(%02d) '%(i+1) + var.varname.ljust(30) 
                    + var.counter_variable.ljust(30))
            print(line, file=out)
        
        n = config_poc.get_parameter_count()
        print('\n\tTotal number of decision variables: %d'%n, file=out)

        n = config_poc.get_objective_count()
        print('\tTotal number of objectives: %d'%n, file=out)
        
        n = config_poc.get_constraints_count()
        print('\tTotal number of constraints: %d'%n, file=out)
            
    @staticmethod
    def BORG_Initialize(random_seed):
        BorgConfiguration.setStandardCLibrary(BorgMOEA.__libstdc_path)
        BorgConfiguration.setBorgLibrary(BorgMOEA.__libborg_path)
        BorgConfiguration.seed(random_seed)
        BorgConfiguration.startedMPI = False

    @staticmethod
    def MPI_Start():
        BorgConfiguration.startMPI(BorgMOEA.__libmpi_path)
        
        world_rank = BorgConfiguration.getWorldRank()
        world_size = BorgConfiguration.getWorldSize()

        return world_size, world_rank

    @staticmethod
    def BORG_SolveProblem(config_poc):
        succeed = False
        max_evaluations = config_poc.maximum_iteration
        
        results = None
        if config_poc.single_problem_mode:
            problem = BorgMOEA.__borg_problem_array[0]

            results = problem.solveMPI(
                islands=1,
                maxEvaluations=max_evaluations,
                runtime=config_poc.runtime_dynamics_output_filename,
                runtimeFrequency=config_poc.runtime_dynamics_frequency
            )
            succeed = True

        # print output 
        if results:
            try:
                f = open(config_poc.calibration_result_output_filename, 'w')
                results.display(out=f, separator=' ')
                f.close()
            except: pass
        
        return succeed

    @staticmethod
    def MPI_Stop():
        BorgConfiguration.stopMPI()
    