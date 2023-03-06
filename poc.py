import sys, os, numpy as np
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP
from algorithm.borg import *

config = None
libborg_path = './algorithm/libborg.so'
libmpi_path = './algorithm/libmpi.so'
libc_path = ''
world_rank = -1
world_size = 0
nvars = 0
nobjs = 0
nconts = 0

###
# (1) Modifications have been make in the borg c code. Two functions defined to 
# return the world rank and world size. Copy the code from 
# WaterGAPCalibration/borg directory
# 
# (2) Compile the borg algorithm c code by
#      [note: load mpi module before compilation]
#      > module load openmpi/openmpi-4.1.0
#      > mpic++ -shared -fPIC -O3 -o ./algorithm/libborg.so borgms.c mt19937ar.c 
# 
# (3) the original borg.py has been modified. the name of the Configuration 
# class has been changed to BorgConfiguration to avoid possible confusion of
# POC configuration class. Two funcitons were added in the BorgConfiguration
# class to retrieve world rank and world size. The original version was written
# for python2.7; thus following modification was made to run in python3.x:
#       a. c_char_p -> c_wchar_p to capture c character array
#       b. print() function in Solution.display() function been changed
# 
# (4) Make a soft link of libmpi.so by
#      > ln -s /cluster/openmpi/gcc-9.2.0/openmpi-4.1.0/lib/libmpi.so libmpi.so
#
###

def model_evaluation(*vars):
    global config

    # update parameters and create parameter file
    # run model
    # compute objectives and constraints

    x, y = vars[0], vars[1]
    objs = [x**2 + y**2, (x-2)**2 + y**2]
    cons = []
    
    return (objs, cons)

def BORG_Initialize(random_seed):
    global libborg_path, libmpi_path, libc_path

    BorgConfiguration.setStandardCLibrary(libc_path)
    BorgConfiguration.setBorgLibrary(libborg_path)
    BorgConfiguration.seed(random_seed)
    BorgConfiguration.startedMPI = False

def MPI_Start():
    global world_rank, world_size
    
    BorgConfiguration.startMPI(libmpi_path)
    
    world_rank = BorgConfiguration.getWorldRank()
    world_size = BorgConfiguration.getWorldSize()

def MPI_Stop():
    BorgConfiguration.stopMPI()


def BORG_Optimization_Problem():
    global config, nvars, nobjs, nconts
    
    nvars = config.get_parameter_count()
    nobjs = config.get_objective_count()
    nconts = config.get_constraints_count()

    problem = Borg(nvars, nobjs, nconts, function=model_evaluation)

    # set bounds of decision variables
    lower_bound, upper_bound = config.get_parameter_bounds()
    problem.setBounds(lower_bound, upper_bound)
    # [end]

    # set epsilons for objectives
    epsilons = config.get_epsilons()
    problem.setEpsilons(epsilons)
    # [end]

    return problem

def BORG_Problem_Description():
    global config, world_rank
    
    if world_rank == 0:
        out = sys.stdout

        print('Problem definition:', file=out)

        line = '\tModel parameter(s):'.ljust(56) + 'Min'.ljust(10) + 'Max'.ljust(10)
        print(line, file=out)
        
        for param in config.parameters:
            line = ('\t\t' + param.parameter_name.ljust(40) 
                    + str(param.get_lower_bound()).rjust(10) 
                    + str(param.get_upper_bound()).rjust(10))
            print(line, file=out)

        print('\n\tVariables:', file=out)
        line = '\tObservation Variables'.rjust(35) + 'Prediction variable'.rjust(35)
        print(line, file=out)

        line = '--------------------'.rjust(35) + '--------------------'.rjust(35)
        print(line, file=out)

        for i in range(len(config.obs_variables)):
            var = config.obs_variables[i]
            line = ('\t\t(%02d) '%(i+1) + var.varname.ljust(30) 
                    + var.counter_variable.ljust(30))
            print(line, file=out)
        
        n = config.get_parameter_count()
        print('\n\tTotal number of decision variables: %d'%n, file=out)

        n = config.get_objective_count()
        print('\tTotal number of objectives: %d'%n, file=out)
        
        n = config.get_constraints_count()
        print('\tTotal number of constraints: %d'%n, file=out)

def main(argv):
    global config, world_rank, world_size

    is_silent_mode = False
    random_seed = 37
    succeed = True

    argc = len(argv)
    if argc > 2:
        for i in range(1, argc):
            if argv[i] == '--silent.mode': is_silent_mode = True
            elif argv[i] == '--random.seed': 
                try: 
                    random_seed = int(argv[i+1])
                    i += 1
                except: pass
            elif argv[i] == '--config.file':
                filename_config = argv[i+1]
                i += 1
    if not filename_config: filename_config = argv[argc - 1]

    # read configuration file
    config = Configuration.read_configuration_file(filename=filename_config)
    
    errcode = config.is_okay_errcode(skip_observation=False)
    if errcode != 0: 
        print('Configuration check was not successful.')
        return errcode
    
    if not WaterGAP.is_okay():
        print('Wrong model configuration!')
        return -1

    # initialize BORG
    BORG_Initialize(random_seed=random_seed)

    # initialize MPI
    MPI_Start()

    # define problem
    problem = BORG_Optimization_Problem()
    
    BORG_Problem_Description()

    # solve optimization problem
    max_evaluations = config.maximum_iteration
    results = problem.solveMPI(
        islands=1,
        maxEvaluations=max_evaluations
    )

    # print output 
    if results:
        try:
            f = open(config.calibration_result_output_filename, 'w')
            results.display(out=f, separator=' ')
            f.close()
        except: pass
    
    # Stop MPI
    MPI_Stop()

    return 0

def test_evaluation(*vars):
    global config

    x, y = vars[0], vars[1]
    objs = [x**2 + y**2, (x-2)**2 + y**2]
    cons = []
    return (objs, cons)

def test(argv):
    BORG_Initialize()

    MPI_Start()

    borg = Borg(2, 2, 0, function=test_evaluation)
    borg.setBounds([-50, 50], [-50, 50])
    borg.setEpsilons(0.01, 0.01)

    result = borg.solveMPI(maxEvaluations=1000)
    if result: result.display()

    MPI_Stop()

    if world_rank == 0: print("Hi I am from master")
    else: print("I am worker no. %d" %world_rank)

    return 0

if __name__ == '__main__': main(sys.argv)
