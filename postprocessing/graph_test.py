import sys
sys.path.append('..')

import numpy as np
from postprocessing.ParetoFront import ParetoDominance
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable


def index_num(x, y): return ((x+y-2)*(x+y-1)+2*x)/2


i = 15
calid = 'B1C' + str(i).rjust(2, '0')
f = '/media/sf_Experiments/%s_pareto_front.csv'%calid.lower()

d = np.loadtxt(f, delimiter=',')
d = d[~np.isnan(d).any(axis=1)]
d = d[d[:,4]<=0.6,:]

fx = 1-d[:,1:]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
fig.set_facecolor('white')


x = fx[:,0]
y = fx[:,1]
z = fx[:,2]
c = fx[:,3]

p = ax.scatter(x, y, z, c=c, cmap=plt.get_cmap('Greens'), edgecolors='face')
cbar = plt.colorbar(p, ticks=np.arange(.5,1.0,0.1), pad=0.0, fraction=0.05, aspect=12)
cbar.outline.set_linewidth(0.8)
# cbar.
# print(cbar.ax.get_yticks())
# cbar.ax.get_yaxis().set_ticks(np.arange(0.0,1.0,0.1))
cbar.ax.get_yaxis().labelpad = 15
cbar.ax.set_ylabel('KGE (TWSV)', rotation=270)

#cbar.ax.set_yticks(np.arange(0.6,1.0,0.1), minor=False)
# ax.plot_surface(x, y, z)

ax.set_ylabel('KGE (ET)')
ax.set_xlabel('KGE (Q)')
ax.set_zlabel('KGE (SWS)')
ax.set_ylim(1.01, 0.65)
ax.set_xlim(1.01, 0.65)
ax.set_zlim(1.01, 0.65)
ax.xaxis.set_ticks(np.arange(.7, 1.0, 0.1))
ax.yaxis.set_ticks(np.arange(.7, 1.0, 0.1))
ax.zaxis.set_ticks(np.arange(.7, 1.0, 0.1))
ax.scatter(1, 1, 1, marker='D', edgecolor='face', c='r')
ax.scatter(0.887335016,	0.924236304, 0.841865925, marker='+', edgecolor='face', c='r', s=250)

ax.view_init(25,230)
plt.show()

def plot_4d(labels=[]):

    return 0

# ax.view_init(20,230)
# plt.show()

# fxc = (d[:,1:]//0.025)+1
# ndx1 = index_num(fxc[:,0], fxc[:,3])
# ndx2 = index_num(fxc[:,1], fxc[:,2])
#
#
#
# d1 = d[:,2]
# d2 = d[:,3]
# #plt.plot(d1, d2, 'ro')
# #plt.show()
#
# fig, ((ax1, ax2, ax3)) = plt.subplots(1, 3)
# fig.subplots_adjust(left=0.2, wspace=0.6)
# fig.set_size_inches(40,20)
#
# d = 1-d
#
#
# ax.plot(d[:,1], d[:,2], 'r.')
# #ax1.set_title('ylabels not aligned')
# ax1.set_ylabel('KGE (Q)')
# ax1.set_xlabel('KGE (ET)')
# ax1.set_ylim(0.65, 1.01)
# ax1.set_xlim(0.65, 1.01)
# ax1.xaxis.set_ticks(np.arange(.7, 1.0, 0.1))
# ax1.yaxis.set_ticks(np.arange(.7, 1.0, 0.1))
#
# ax3.plot(d[:,1], d[:,3], 'r.')
# #ax3.set_title('ylabels not aligned')
# ax3.set_ylabel('KGE (Q)')
# ax3.set_xlabel('KGE (SWS)')
# ax3.set_ylim(0.65, 1.01)
# ax3.set_xlim(0.65, 1.01)
# ax3.xaxis.set_ticks(np.arange(.7, 1.0, 0.1))
# ax3.yaxis.set_ticks(np.arange(.7, 1.0, 0.1))
#
# labelx = -0.3  # axes coords
#
# ax2.plot(d[:,2], d[:,3], 'r.')
# #ax2.set_title('ylabels not aligned')
# ax2.set_ylabel('KGE (Q)')
# ax2.set_xlabel('KGE (SWS)')
# ax2.set_ylim(0.65, 1.01)
# ax2.set_xlim(0.65, 1.01)
# ax2.xaxis.set_ticks(np.arange(.7, 1.0, 0.1))
# ax2.yaxis.set_ticks(np.arange(.7, 1.0, 0.1))
#
# # ax4.plot(np.random.rand(10))
# # ax4.set_ylabel('aligned 2')
# # ax4.yaxis.set_label_coords(labelx, 0.5)
#
# plt.show()