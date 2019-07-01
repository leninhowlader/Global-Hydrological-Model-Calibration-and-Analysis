import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D         # required for 3D plotting


# method of best point selection (respecting euclidian distance from utopia)
def best_point_ed(fx_pf:np.ndarray):
    ed = []
    for i in range(fx_pf.shape[0]):
        ed.append(np.sum((1 - fx_pf[i, :]) ** 2))

    if not ed: return []
    else:
        ndx = ed.index(min(ed))
        return np.ndarray.tolist(fx_pf[ndx])

def best_point_thresold(fx_pf:np.ndarray, thresold):
    ndx = np.where((fx_pf[:,0] > thresold) & (fx_pf[:,1] > thresold) & (fx_pf[:,2] > thresold) & (fx_pf[:,3] > thresold))
    return ndx

# step 1: get data
calid = 'BRH_CAL3P0_15'
f = 'F:/mhasan/experiments/Calibration3.0/output/pareto_front/PF_Ebox_%s.csv'%calid.lower()
d = np.loadtxt(f, delimiter=',')        # read data from file

# step-2: exclude data points outside preferred limits
d = d[~np.isnan(d).any(axis=1)]         # remove rows having any nan value
fx = d[:, 1:5]                          # crop objective columns
fx = 1-fx                               # additional step: 1-KGE was used as objective function during calibration.
                                        # thus, it is necessary to convert the objective values back to KGE values

lmt = 0.5                               # set minimum efficiency limit i.e., min f(x)
for i in range(fx.shape[1]):            # exclude data below the minimum limit
    fx = fx[fx[:,i]>=lmt,:]

# step-3: initialize and draw figure
fig = plt.figure(figsize=(7,6))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(left=0, bottom=0.05, right=0.95, top=.85, wspace=None, hspace=None)
fig.set_facecolor('white')
title = '(b) Brahmaputra'
plt.suptitle(title, fontsize=22, style='italic')

# split data into four dimensions
x = fx[:,0]
y = fx[:,3]
z = fx[:,2]
c = fx[:,1]                             # the fourth dimension will be shown as color map

# plot the scatter diagram
# p = ax.plot_trisurf(x, y, z, linewidth=0, antialiased=True, edgecolor='blue', color='yellow')
p = ax.scatter(x, y, z, c=c, cmap=plt.get_cmap('YlGn'), edgecolors='face', s=30, vmin=0.8, vmax=1.0)


# set axes limits
# ax.set_ylim(1.01, min(y))
# ax.set_xlim(1.01, min(x))
# ax.set_zlim(1.01, min(z))

ax.set_ylim(1.01, 0.79)
ax.set_xlim(1.01, 0.79)
ax.set_zlim(1.01, 0.79)

# set axes ticks
ax.xaxis.set_ticks(np.arange(lmt, 1.01, 0.1))
ax.yaxis.set_ticks(np.arange(lmt, 1.01, 0.1))
ax.zaxis.set_ticks(np.arange(lmt, 1.01, 0.1))
ax.tick_params(axis='both', which='major', labelsize=15)

# add axes labels
ax.set_xlabel('kge (q)', fontsize=20)
ax.set_ylabel('kge (twsv)', fontsize=20)
ax.set_zlabel('kge (sws)', fontsize=20)

ax.xaxis.labelpad = 20
ax.yaxis.labelpad = 20
ax.zaxis.labelpad = 20

#ax.zaxis.
# draw the colour bar
cbar = plt.colorbar(p, ticks=np.arange(0.8,1.01,0.1), pad=0.01, fraction=0.05, aspect=30)
cbar.ax.tick_params(labelsize=15) 
cbar.outline.set_linewidth(0.6)
cbar.ax.get_yaxis().labelpad = -50
cbar.ax.get_yaxis().set_ticks_position('right')

#cbar.ax.tick_params(axis='both', which='major', labelsize=20, pad=10)
cbar.ax.set_ylabel('kge (et)', rotation=270, fontsize=20)
#cbar.set_ticks([0,0.5,1.])

# add the optimal (utopia) point and the chosen best point
ax.scatter(1, 1, 1, marker='o', edgecolor='face', c='r', zorder=1, s=40)
ndx = best_point_thresold(fx, 0.85)
bp = fx[ndx]
# p1, p2, p3, p4 = best_point_ed(fx)
# ax.scatter(p1, p2, p3, marker='+', edgecolor='face', c='r', s=500, zorder=-1, linewidths=4)

for p in bp:
    p1, p4, p3, p2 = p
    ax.scatter(p1, p2, p3, marker='+', edgecolor='face', c='r', s=200, zorder=-1, linewidths=2)


# show or save the graph
ax.view_init(55,-105)                    # adjust viewing angle
f = 'pf_test.png'
fig.savefig(f)
fig.tight_layout()
plt.show()
# plt.close(fig)

