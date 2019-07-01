import sys, os
sys.path.append('..')
import numpy as np
from postprocessing.ParetoFront import ParetoDominance
from utilities.fileio import write_flat_file


result_directory = 'F:/mhasan/experiments/Calibration3.0/output/new output gan 11'

for i in range(1, 16):
    calid = 'gan_cal3p0_%s'%str(i).rjust(2, '0')
    # calid = 'gan_cal3p0_12'
    # read parameter file
    filename = os.path.join(result_directory, 'param_value_%s.csv' % calid)
    if not os.path.exists(filename): continue
    p = np.loadtxt(filename, delimiter=',')


    filename = os.path.join(result_directory, 'function_value_%s.csv'%calid)
    if not os.path.exists(filename): continue

    # read function file
    d = np.loadtxt(filename, delimiter=',')
    d = d[~np.isnan(d).any(axis=1)]
    fx = d[:,1:]

    epsilon = [0.025] * fx.shape[1]

    pareto_front, ndces = ParetoDominance.ParetoFront(fx, epsilons=epsilon)
    ids = d[ndces,0:1]
    ndx = np.where(p[:,0]==ids)[1]
    results = np.concatenate((ids, pareto_front, p[ndx]), axis=1)
    filename = os.path.join(result_directory, 'pareto_front', 'PF_Ebox_%s.csv'%calid)
    write_flat_file(filename, results, separator=',', append=False)

    funname = 'pareto dominance'
    pareto_front, ndces = ParetoDominance.ParetoFront(fx, epsilons=epsilon, funname=funname)
    ids = d[ndces,0:1]
    results = np.append(ids, pareto_front, axis=1)
    filename = os.path.join(result_directory, 'pareto_front', 'PF_%s.csv' % calid)
    write_flat_file(filename, results, separator=',', append=False)
