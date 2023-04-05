import sys, os, numpy as np
from core.configuration import Configuration
from wgap.watergap import WaterGAP
from algorithm.borg import *
from analyses.calibration import Calibration, BorgMOEA

config = None
libborg_path = '/home/mhasan/ProjectWGHM/algorithm/libborg.so'
# libborg_path = '/scratch/fuchs/agdoell/hosseini/watergap-calibration-and-analysis-with-python/algorithm/libborg.so'
libmpi_path = 'libmpi.so'
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


def main(argv):
    global config, world_rank, world_size
    global libborg_path, libmpi_path, libc_path

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

    # set borg, mpi, and std C libraries
    BorgMOEA.set_borg_library(libborg_path)
    BorgMOEA.set_stdandard_C_library(libc_path)
    BorgMOEA.set_mpi_library(libmpi_path)

    # initialize BORG
    BorgMOEA.BORG_Initialize(random_seed=random_seed)

    # initialize MPI
    world_size, world_rank = BorgMOEA.MPI_Start()

    # read configuration file
    config = Configuration.read_configuration_file(filename=filename_config)
    
    errcode = config.is_okay_errcode(skip_observation=False)
    if errcode != 0: 
        if world_rank == 0:
            print('Configuration check was not successful.')
        
        BorgMOEA.MPI_Stop()
        return errcode
    
    if not WaterGAP.is_okay():
        if world_rank == 0:
            print('Wrong model configuration!')
        BorgMOEA.MPI_Stop()
        return -1

    # define problem
    Calibration.set_calibration_configurations(config)
    eval_func = Calibration.model_evaluation
    Calibration.set_world_rank(world_rank)
    Calibration.set_world_size(world_size)
    
    succeed = BorgMOEA.BORG_Optimization_Problem_Create(
        poc_config=config, 
        eval_func=eval_func
    )
    
    if world_rank == 0: 
        BorgMOEA.BORG_Problem_Description(config_poc=config, out=sys.stdout)

    # solve optimization problem
    succeed = BorgMOEA.BORG_SolveProblem(config_poc=config)
    
    # Stop MPI
    BorgMOEA.MPI_Stop()

    return 0

def test_evaluation(*vars):
    global config

    x, y = vars[0], vars[1]
    objs = [x**2 + y**2, (x-2)**2 + y**2]
    cons = []
    return (objs, cons)

def test(argv):
    global world_rank, world_size
    BorgMOEA.BORG_Initialize(random_seed=37)

    world_size, world_rank = BorgMOEA.MPI_Start()

    from algorithm.borg import Borg
    borg = Borg(2, 2, 0, function=test_evaluation)
    borg.setBounds([-50, 50], [-50, 50])
    borg.setEpsilons(0.01, 0.01)

    result = borg.solveMPI(maxEvaluations=1000)
    if result: result.display()

    BorgMOEA.MPI_Stop()

    return 0

if __name__ == '__main__': main(sys.argv)
