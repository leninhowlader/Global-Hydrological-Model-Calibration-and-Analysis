import sys, numpy as np
sys.path.append('F:\mhasan\private\ProjectWGHM')
from matplotlib import pyplot as ppt


fnam = '/media/sf_Experiments/FINAL_CALIBRATION/Brahmaputra_Results/B1C07/funcval.csv'
data = np.loadtxt(fnam, delimiter=',')

ppt.scatter(1-data[:,1], 1-data[:,2])
ppt.show()