import sys
sys.path.append('..')
import numpy as np
from postprocessing.ParetoFront import ParetoDominance
from utilities.fileio import write_flat_file



for i in range(1, 16):
    calid = 'B1C' + str(i).rjust(2, '0')
    f = '/media/sf_Experiments/FINAL_CALIBRATION/Brahmaputra Results/%s/funcval.csv'%calid

    # f = 'output/pareto_front.csv'
    d = np.loadtxt(f, delimiter=',')
    d = d[~np.isnan(d).any(axis=1)]
    fx = d[:,1:]

    epsilon = [0.025] * fx.shape[1]
    pareto_front = []

    pareto_front, ndces = ParetoDominance.ParetoFront(fx, epsilons=epsilon)
    ids = d[ndces,0:1]
    results = np.append(ids, pareto_front, axis=1)
    write_flat_file('/media/sf_Experiments/%s_pareto_front_epsilon_box.csv'%calid.lower(), results, separator=',', append=False)


    funname = 'pareto dominance'
    pareto_front, ndces = ParetoDominance.ParetoFront(fx, epsilons=epsilon, funname=funname)
    ids = d[ndces,0:1]
    results = np.append(ids, pareto_front, axis=1)
    write_flat_file('/media/sf_Experiments/%s_pareto_front.csv'%calid.lower(), results, separator=',', append=False)
