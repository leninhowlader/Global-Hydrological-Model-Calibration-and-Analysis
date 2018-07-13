import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D         # required for 3D plotting


# method of best point selection (respecting euclidian distance from utopia)
def best_point_ed(ds):
    ed = []
    for i in range(ds.shape[0]):
        ed.append(np.sum((1-ds[i,:])**2))

    if not ed: return []
    else:
        ndx = ed.index(min(ed))
        return np.ndarray.tolist(ds[ndx])


# step 1: get data
calid = 'B1C15'
f = '/media/sf_Experiments/%s_pareto_front.csv'%calid.lower()
d = np.loadtxt(f, delimiter=',')        # read data from file

# step-2: exclude data points outside preferred limits
d = d[~np.isnan(d).any(axis=1)]         # remove rows having any nan value
fx = d[:, 1:]                           # crop objective columns
fx = 1-fx                               # additional step: 1-KGE was used as objective function during calibration.
                                        # thus, it is necessary to convert the objective values back to KGE values

lmt = 0.6                               # set minimum efficiency limit i.e., min f(x)
for i in range(fx.shape[1]):            # exclude data below the minimum limit
    fx = fx[fx[:,i]>=lmt,:]

# step-3: initialize and draw figure
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(left=0, bottom=0.05, right=0.95, top=.85, wspace=None, hspace=None)
fig.set_facecolor('white')
title = '(k) PF for Q, ET, SWS, TWSV'
plt.suptitle(title, fontsize=22, style='italic')

# split data into four dimensions
x = fx[:,0]
y = fx[:,1]
z = fx[:,2]
c = fx[:,3]                             # the fourth dimension will be shown as color map

# plot the scatter diagram
# p = ax.plot_trisurf(x, y, z, linewidth=0, antialiased=True, edgecolor='blue', color='yellow')
p = ax.scatter(x, y, z, c=c, cmap=plt.get_cmap('Greys'), edgecolors='face', s=40)


# set axes limits
ax.set_ylim(1.01, min(y))
ax.set_xlim(1.01, min(x))
ax.set_zlim(1.01, min(z))

# set axes ticks
ax.xaxis.set_ticks(np.arange(lmt, 1.0, 0.1))
ax.yaxis.set_ticks(np.arange(lmt, 1.0, 0.1))
ax.zaxis.set_ticks(np.arange(lmt, 1.0, 0.1))
ax.tick_params(axis='both', which='major', labelsize=20)

# add axes labels
ax.set_ylabel('KGE for ET', fontsize=20)
ax.set_xlabel('KGE for Q', fontsize=20)
ax.set_zlabel('KGE for SWS', fontsize=20)

ax.xaxis.labelpad = 20
ax.yaxis.labelpad = 20
ax.zaxis.labelpad = 20

# draw the colour bar
cbar = plt.colorbar(p, ticks=np.arange(lmt,1.0,0.1), pad=0, fraction=0.05, aspect=12)
cbar.outline.set_linewidth(0.8)
cbar.ax.get_yaxis().labelpad = 18
# cbar.ax.get_yaxis().set_ticks_position = 'right'
cbar.ax.get_yaxis().tick_left()

for a in dir(cbar.ax.get_yaxis()): print(a)
cbar.ax.tick_params(axis='both', which='major', labelsize=20, pad=10)
cbar.ax.set_ylabel('KGE for TWSV', rotation=270, fontsize=20)


# add the optimal (utopia) point and the chosen best point
ax.scatter(1, 1, 1, marker='o', edgecolor='face', c='r', zorder=1, s=150)
p1, p2, p3, p4 = best_point_ed(fx)
ax.scatter(p1, p2, p3, marker='+', edgecolor='face', c='r', s=500, zorder=-1, linewidths=4)

# show or save the graph
ax.view_init(30,-110)                    # adjust viewing angle
f = '/media/sf_Experiments/%s_pareto_frontier.png' % calid
fig.savefig(f)
plt.show()
# plt.close(fig)
