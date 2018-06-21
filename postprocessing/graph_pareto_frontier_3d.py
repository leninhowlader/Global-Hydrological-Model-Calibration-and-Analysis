import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# step 1: get data
calid = 'B1C15'
f = '/media/sf_Experiments/%s_pareto_front.csv'%calid.lower()
d = np.loadtxt(f, delimiter=',')        # read data from file

# step-2: exclude data points outside preferred limits
d = d[~np.isnan(d).any(axis=1)]         # remove rows having any nan value
fx = d[:, 1:]                           # crop objective columns
fx = 1-fx                               # additional step: 1-KGE was used as objective function during calibration.
                                        # thus, it is necessary to convert the objective values back to KGE values

lmt = 0.4                               # set minimum efficiency limit i.e., min f(x)
for i in range(fx.shape[1]):            # exclude data below the minimum limit
    fx = fx[fx[:,i]>=lmt,:]

# step-3: initialize and draw figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
fig.set_facecolor('white')

# split data into four dimensions
x = fx[:,0]
y = fx[:,1]
z = fx[:,2]
c = fx[:,3]                             # the fourth dimension will be shown as color map

# plot the scatter diagram
p = ax.scatter(x, y, z, c=c, cmap=plt.get_cmap('Greens'), edgecolors='face')

# set axes limits
ax.set_ylim(1.01, min(y))
ax.set_xlim(1.01, min(x))
ax.set_zlim(1.01, min(z))

# set axes ticks
ax.xaxis.set_ticks(np.arange(lmt, 1.0, 0.1))
ax.yaxis.set_ticks(np.arange(lmt, 1.0, 0.1))
ax.zaxis.set_ticks(np.arange(lmt, 1.0, 0.1))

# add axes labels
ax.set_ylabel('KGE (ET)')
ax.set_xlabel('KGE (Q)')
ax.set_zlabel('KGE (SWS)')

# draw the colour bar
cbar = plt.colorbar(p, ticks=np.arange(lmt,1.0,0.1), pad=0.0, fraction=0.05, aspect=12)
cbar.outline.set_linewidth(0.8)
cbar.ax.get_yaxis().labelpad = 15
cbar.ax.set_ylabel('KGE (TWSV)', rotation=270)

# add the optimal (utopia) point and the chosen best point
ax.scatter(1, 1, 1, marker='D', edgecolor='face', c='r')
ax.scatter(0.887335016,	0.924236304, 0.841865925, marker='+', edgecolor='face', c='r', s=250)

# show or save the graph
ax.view_init(25,230)                    # adjust viewing angle
f = 'output/%s_pareto_frontier.png' % calid
fig.savefig(f)
plt.show()
# plt.close(fig)
