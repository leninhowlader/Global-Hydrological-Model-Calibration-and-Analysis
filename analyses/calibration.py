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
    __world_rank = -1
    __world_size = 0
    __config = None

    __consistency_check = False
    __id_local = 0

    __nvars = 0
    __nobjs = 0
    __nconts = 0

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

        nprobs = config.poc_problem_count
        if nprobs == 1:
            Calibration.__nvars = config.get_parameter_count()
            Calibration.__nobjs = config.get_objective_count()
            Calibration.__nconts = config.get_constraints_count()
        else:
            Calibration.__nvars = np.sum(
                [config.get_parameter_count(i) for i in range(nprobs)]
            )
            
            Calibration.__nobjs = np.sum(
                [config.get_objective_count(i) for i in range(nprobs)]
            )
            
            Calibration.__nconts = np.sum(
                [config.get_constraints_count(i) for i in range(nprobs)]
            )

    @staticmethod
    def is_okay():
        if not Calibration.__consistency_check:
            config = Calibration.__config
            if not config: return False

            world_rank = Calibration.__world_rank
            world_size = Calibration.__world_size

            nvars, nobjs = Calibration.__nvars, Calibration.__nobjs
            if not (nvars > 0 and nobjs > 0 and world_rank >= 0 and 
                    world_size > 0): 
                return False
            else: Calibration.__consistency_check = True
        
        return Calibration.__consistency_check            

    @staticmethod
    def model_evaluation(*vars):
        # [step-x]: Preparation, information gathering
        config = Calibration.__config
        my_rank = Calibration.__world_rank
        
        nvars = Calibration.__nvars
        nobjs, nconts = Calibration.__nobjs, Calibration.__nconts
        objs, conts = [np.nan] * nobjs, [np.nan] * nconts


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
        
        if config.poc_problem_count == 1:
            messages.append('\tParameter values: ')
            for i in range(nvars):
                param = Calibration.__config.parameters[i]
                messages.append('\t[%02d] %s: %f'%(
                    i, param.parameter_name.ljust(40), param.parameter_value))
        else:
            # do not print the parameter values on screen
            pass

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
        messages.append('\n\tModel execution started at %s'%str(t1))
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
                WaterGAP.remove_files(arguments)
                succeed = False

            # [sub-step] compute spatial summary
            if succeed: succeed = var.aggregate_prediction_at_spatial_scale()
            # [end]

            # [sub-step] compute anomaly
            if succeed: var.do_anomaly_computation()
            # [end]

            # [sub-step] apply conversion factor
            var.apply_conversion_factor()
            # [end]
            
            if not succeed: break

        if not succeed: return (objs, conts)
        
        ## compute values of derived variable
        for var in config.derived_variables:
            var.derive_data(simvars=config.sim_variables)
            var.do_anomaly_computation()
        # end [step-x]
        
        # [step-x] compute objectives
        # 
        temp = Calibration.compute_objectives()
        if len(temp) == nobjs:
            for i in range(nobjs): objs[i] = temp[i]
        
        if config.poc_problem_count == 1:
            messages.append(
                '\n\tObjectives: %s'%(
                    ','.join(['%0.2f'%temp[i] for i in range(nobjs)])
                )
            )
        else:
            # do not print objective values for all problems on screen
            pass
        # end [step-x]

        # [step-x] compte constraints
        temp = Calibration.compute_constraints()
        if len(temp) == nconts:
            for i in range(nconts): conts[i] = temp[i]
        
        if config.poc_problem_count == 1:
            if nconts == 0: messages.append('\tConstraints: NA')
            else: 
                messages.append(
                    '\tConstraints: %s'%(
                        ','.join(['%0.2f'%temp[i] for i in range(nconts)])
                    )
                )
        else:
            # do not print constraints for all problems on screen
            pass
        # end [step-x]

        # [step-x] remove simulation output files
        WaterGAP.remove_files(arguments)
        # end [step-x]

        # [step-x] write predictions, parameter values, objectives etc..
        Calibration.write_parameter_values(evaluation_num, vars)
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
        """
        The function compute objectives by comparing the observation variables
        to corresponding simulation variable counterparts.

        Returns:
        (list of floats)
            the array of objectives. for the multi-problem optimization case, 
            a long one-dimentional array containing all objectives for all the 
            problems will be created. the long list of objectives will be 
            fragmented by the algorithm according to the problem definition.
        """
        objs = []
        config = Calibration.__config

        for obsvar in config.obs_variables:
            obsvar.objectives.queue.clear()
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
                obsvar.objectives.put(np.nan) 
                continue
            
            fun = obsvar.function
            ii, jj = DataCloud.index_coupling(
                obsvar.data_cloud,
                var.data_cloud
            )

            obs = obsvar.data_cloud.data[ii]
            sim = var.data_cloud.data[jj]

            lb, ub, use_uncertainty = np.empty(0), np.empty(0), False
            if obsvar.has_uncertainty_bound:
                lb = obsvar.data_cloud.lower_bound[ii]
                ub = obsvar.data_cloud.upper_bound[ii]
                
                if lb.shape[0] > 0 and ub.shape == lb.shape: 
                    use_uncertainty = True
            
            lim1, lim2 = np.empty(0), np.empty(0)

            if ((sim.ndim == 1 or sim.shape[1] == 1) and 
                (obs.ndim == 1 or obs.shape[1] == 1)):
                # this is the usual case where we would have one observation 
                # time-series to be compared with only one simulation series

                obs = obs.flatten()
                sim = sim.flatten()
                if use_uncertainty: 
                    lim1, lim2 = lb, ub

                f = stats.objective_function(
                        fun=fun, 
                        sim=sim, 
                        obs=obs,
                        lb=lim1,
                        ub=lim2
                    )

                obsvar.objectives.put(f)

            elif obs.ndim == 2 and (sim.ndim == 1 or sim.shape[1] == 1):
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
                    if use_uncertainty: lim1, lim2 = lb[:, i], ub[:, i]

                    f = stats.objective_function(
                        fun=fun, 
                        sim=sim, 
                        obs=o,
                        lb=lim1,
                        ub=lim2
                    )

                    obsvar.objectives.put(f)

            elif obs.ndim == 2 and sim.ndim == 2 and obs.shape[1] == sim.shape[1]:
                # When obs contains multiple time-series for different units, 
                # say for each cell or for multiple basins, this case will apply.
                # sim must contain simulation values for corresponding cells or
                # basins
                for i in range(obs.shape[1]):
                    o = obs[:, i].flatten()
                    s = sim[:, i].flatten()
                    
                    if use_uncertainty: lim1, lim2 = lb[:, i], ub[:, i]

                    f = stats.objective_function(
                        fun=fun, sim=s, obs=o, lb=lim1, ub=lim2
                    )

                    obsvar.objectives.put(f)
            
            else: obsvar.objectives.put(np.nan)

            # apply objective weighting factor, if applicable
            obsvar.apply_objective_weighting_factors()

        objectives = []
        if config.calibration_type in ['single', 'one']:
            for obsvar in config.obs_variables:
                # objectives += list(obsvar.objectives.queue)
                # obsvar.objectives.queue.clear()
                
                objectives += [
                    obsvar.objectives.get() 
                    for _ in range(obsvar.objectives.qsize())
                ]
        else:
            for obj_indices in config.multiproblem_objective_index_list:
                groups = OrderedDict()
                for num in obj_indices:
                    obsvar = config.obs_variables[num]
                    obj = obsvar.objectives.get()
                    
                    try: groups[num]['values'].append(obj)
                    except: 
                        fun = np.mean
                        if len(obsvar.weight_factors) > 0: fun = np.sum
                        groups[num] = {'values': [obj], 'fun': fun}
                
                for _, v in groups.items():
                    fun = v['fun'] 
                    objectives.append(fun(v['values']))
                
        return objectives

    @staticmethod
    def compute_constraints():
        conts = []

        # to be added

        return conts

    @staticmethod
    def update_parameters(vars):
        """
        The function update current values of the parameters in the parameter 
        objects stored in parameter list of the configuration object. cell level
        parameter value is only possible for single problem calibration. In case
        of multi-problem calibration, the parameter value is applied for the 
        entire unit considered in the particular problem.
        """
        config = Calibration.__config
        
        # [+] clear previous parameter values, if any
        for param in config.parameters:
            if type(param.parameter_value) is list:
                param.parameter_value.clear()
            else: param.parameter_value = None
        # [.]


        if config.calibration_type in ['single', 'one']:
            var_index = 0
            for i in range(len(config.parameters)):
                if config.parameters[i].cell_level_representation == True:
                    n = config.parameters[i].get_unit_count()
                    
                    config.parameters[i].parameter_value = \
                    vars[var_index, var_index + n]

                    var_index += n
                else:
                    config.parameters[i].parameter_value = vars[var_index]
                    var_index += 1
        
        else:
            var_index = 0

            param_indices = config.multiproblem_parameter_index_list
            for indices in param_indices:
                for num in indices:
                    config.parameters[num].add_unit_parameter_value(
                        vars[var_index]
                    )
                    var_index += 1
        #
    
    @staticmethod
    def write_parameter_values(evaluation_num, parameter_values):
        filename = Calibration.__config.parameter_value_output_filename
        
        t = [evaluation_num] + parameter_values
        if filename:
            filename = '%s_%d_.%s'%(
                filename[:-4], Calibration.__world_rank, filename[-3:]
            )

            f = open(filename, 'a')
            f.write(','.join([str(x) for x in t]) + '\n')
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
    __nproblems = 0         # Number of optimization problems

    __world_size = 0
    __world_rank = -1

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
    def BORG_Optimization_Problem_Create(
        poc_config:Configuration, eval_func
    ):
        """
        The function creates borg problem instance (both Python-instances and
        C-instances).

        Parameters:
        poc_config: Configuration
            The POC configuration object that define all necessary information
            concerning the calibration experiment.
        eval_func: function
            the reference of the evaluation function. the evaluation function
            must have the predefined signature. the function must have one
            parameter that passes values of the decision variables from the
            calibration algorithm and return objectives and optionally 
            constraints
        
        Returns:
        bool
            success report. on success the function return True, otherwise False
        """
        
        succeed = True
        
        if poc_config.calibration_type in ['single', 'one']:
            nvars = poc_config.get_parameter_count()
            nobjs = poc_config.get_objective_count()
            nconts = poc_config.get_constraints_count()


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

        elif poc_config.calibration_type in ['multiple', 'many']:
            nproblems = poc_config.poc_problem_count
            nconts = 0
            BorgMOEA.__borg_problem_array.clear()

            # [step]
            # Create borg-problem python instances
            # 
            # Borg problem instances are created in this step and stored in a
            # list in the Borg class. Please note that in this stage only python
            # instances are created which is different from single-problem
            # calibration. In single-problem calibration actual C-instances of
            # the borg-problem is created in the same step when Python-instance
            # is created. In case of multi-problem case, the C-instances are 
            # created in a separate step after assigning a common evaluation
            # funtion. 

            for problem_no in range(nproblems):
                nvars = poc_config.get_parameter_count(problem_no)
                nobjs = poc_config.get_objective_count(problem_no)
                epsilons = poc_config.get_epsilons(problem_no)
                
                lower_bound, upper_bound = poc_config.get_parameter_bounds(
                    problem_no
                )
                
                bounds = [
                    [lower_bound[i], upper_bound[i]] for i in range(nvars)
                ]

                problem = Borg(
                    nvars, nobjs, nconts, function=None, bounds=bounds, 
                    epsilons=epsilons
                )

                Borg.add_problem(problem)
                BorgMOEA.__borg_problem_array.append(problem)
            
            BorgMOEA.__nproblems = nproblems
            # end [step]

            # [step]
            # Set evaluate function:
            # Evaluation function is not provided while creating a problem 
            # instance. This is because, for multi-problem calibration the
            # algorithm the total number of parameters for all problems and 
            # total number of objectives for all problem, rather than parameter
            # and objective count for individual problems as done in single 
            # problem calibration. this is why the evaluation function is 
            # provided in a separate step
            
            Borg.set_function(eval_func)
            # end [step]

            # [step]
            # Instantiate all problems:
            # This separate step of instantiation is requred after the 
            # evaluation function is set up. In this step, problem instances in
            # the memory for to be used by the Borg C-library.
            
            Borg.instantiate_borg_problems()  
            # end [step]

        else: succeed = False

        BorgMOEA.__poc_config = poc_config

        return succeed
    
    @staticmethod
    def BORG_Problem_Description(out=sys.stdout):
        poc_config = BorgMOEA.__poc_config
        if not poc_config or BorgMOEA.__nproblems == 0:
            print('Problem description could not be retrieved!')
            return
        
        print('Problem definition:', file=out)
        if BorgMOEA.__nproblems == 1:
            line = '\tModel parameter(s):'.ljust(56) + 'Min'.ljust(10) + 'Max'.ljust(10)
            print(line, file=out)
            
            for param in poc_config.parameters:
                line = ('\t\t' + param.parameter_name.ljust(40) 
                        + str(param.get_lower_bound()).rjust(10) 
                        + str(param.get_upper_bound()).rjust(10))
                print(line, file=out)

            print('\n\tVariables:', file=out)
            line = '\tObservation Variables'.rjust(35) + 'Prediction variable'.rjust(35)
            print(line, file=out)

            line = '--------------------'.rjust(35) + '--------------------'.rjust(35)
            print(line, file=out)

            for i in range(len(poc_config.obs_variables)):
                var = poc_config.obs_variables[i]
                line = ('\t\t(%02d) '%(i+1) + var.varname.ljust(30) 
                        + var.counter_variable.ljust(30))
                print(line, file=out)
            
            n = poc_config.get_parameter_count()
            print('\n\tTotal number of decision variables: %d'%n, file=out)

            n = poc_config.get_objective_count()
            print('\tTotal number of objectives: %d'%n, file=out)
            
            n = poc_config.get_constraints_count()
            print('\tTotal number of constraints: %d'%n, file=out)
        elif BorgMOEA.__nproblems > 1:
            messages = '\t(summary info)\n'
            messages += '\tthis is a multi-problem calibration.\n'
            messages += '\ttotal number of problems: %d\n'%BorgMOEA.__nproblems
            
            nparams = np.array(
                [len(x) for x in poc_config.multiproblem_parameter_index_list]
            )
            messages += '\tmaximum parameter count: %d\n'%nparams.max()
            messages += '\tminimum parameter count: %d\n'%nparams.min()
            messages += '\taverage parameter count: %0.1f\n'%nparams.mean()
            
            nobjs = np.array(
                [np.unique(x).shape[0] 
                 for x in poc_config.multiproblem_objective_index_list]
            )
            messages += '\tmaximum objective count: %d\n'%nobjs.max()
            messages += '\tminimum objective count: %d\n'%nobjs.min()
            messages += '\taverage objective count: %0.1f\n'%nobjs.mean()
            
            print(messages)

            
    @staticmethod
    def BORG_Initialize(random_seed):
        BorgConfiguration.setStandardCLibrary(BorgMOEA.__libstdc_path)
        BorgConfiguration.setBorgLibrary(BorgMOEA.__libborg_path)
        BorgConfiguration.seed(random_seed)
        BorgConfiguration.startedMPI = False

    @staticmethod
    def MPI_Start():
        BorgConfiguration.startMPI(BorgMOEA.__libmpi_path)
        
        BorgMOEA.__world_rank = BorgConfiguration.getWorldRank()
        BorgMOEA.__world_size = BorgConfiguration.getWorldSize()

        return BorgMOEA.__world_size, BorgMOEA.__world_rank

    @staticmethod
    def BORG_SolveProblem():
        succeed = False
        
        poc_config = BorgMOEA.__poc_config
        if not poc_config or poc_config.poc_problem_count == 0: 
            return succeed
        
        max_evaluations = poc_config.maximum_iteration
        filename_runtime = poc_config.runtime_dynamics_output_filename
        frequency_runtime = poc_config.runtime_dynamics_frequency
        filename_results = poc_config.calibration_result_output_filename

        results = None
        if poc_config.calibration_type in ['single', 'one']:
            problem = BorgMOEA.__borg_problem_array[0]

            results = Borg.solveMPI(
                problem=problem,
                islands=1,
                maxEvaluations=max_evaluations,
                runtime=filename_runtime,
                runtimeFrequency=frequency_runtime,
                modeManyProblems=False
            )
            
            # print output 
            if results and BorgMOEA.__world_rank == 0:
                try:
                    f = open(filename_results, 'w')
                    results.display(out=f, separator=' ')
                    f.close()
                except: pass
                
            succeed = True
        
        elif poc_config.poc_problem_count > 1:
            results = Borg.solveMPI(
                problem=None,
                islands=1,
                maxEvaluations=max_evaluations,
                runtime=filename_runtime,
                runtimeFrequency=frequency_runtime,
                modeManyProblems=True
            )
            
            # print output 
            if results and BorgMOEA.__world_rank == 0:
                for problem_id in range(poc_config.poc_problem_count):
                    try:
                        filename_problem_results = '%s_%02d%s'%(
                            filename_results[:-4], problem_id, 
                            filename_results[-4:]
                        )
                        f = open(
                            filename_problem_results, 'w'
                        )
                        results[problem_id].display(out=f, separator=' ')
                        f.close()
                    except: pass
            
            succeed = True

        # clear results array
        Borg.results.clear()

        # delete lock file
        if BorgMOEA.__world_rank == 0: FileInputOutput.delete_lock_file()

        return succeed

    @staticmethod
    def MPI_Stop():
        BorgConfiguration.stopMPI()
    