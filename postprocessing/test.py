import sys
sys.path.append('..')
import numpy as np
from postprocessing.ParetoFront import ParetoDominance
from utilities.fileio import write_flat_file




#
i = 6
calid = 'B1C' + str(i).rjust(2, '0')
f = '/media/sf_Experiments/FINAL_CALIBRATION/Brahmaputra Results/%s/funcval.csv'%calid
#
# # f = 'output/pareto_front.csv'
d = np.loadtxt(f, delimiter=',')
d = d[~np.isnan(d).any(axis=1)]
fx = d[:,1:]
#
epsilon = [0.025] * fx.shape[1]
# pareto_front = []
#
pareto_front, ndces = ParetoDominance.ParetoFront(fx, epsilons=epsilon, funname='paretodominance')
# ids = d[ndces,0:1]

# print(pareto_front)
# if 1: exit()
# results = np.append(ids, pareto_front, axis=1)
# write_flat_file('/media/sf_Experiments/%s_pareto_front_epsilon_box.csv'%calid.lower(), results, separator=',', append=False)
#
#
# funname = 'pareto dominance'
# pareto_front, ndces = ParetoDominance.ParetoFront(fx, epsilons=epsilon, funname=funname)
# ids = d[ndces,0:1]
# results = np.append(ids, pareto_front, axis=1)
# write_flat_file('/media/sf_Experiments/%s_pareto_front.csv'%calid.lower(), results, separator=',', append=False)

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import numpy as np


x = pareto_front[:,0]
y = pareto_front[:,1]
# print(x)
plt.scatter(x, y, edgecolor='face', marker='+', c='r')


plt.show()