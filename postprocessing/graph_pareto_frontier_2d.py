import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D         # required for 3D plotting


csetting = np.array(
            [[1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,0,1],
            [1,1,0,0],
            [1,0,1,0],
            [1,0,0,1],
            [0,1,1,0],
            [0,1,0,1],
            [0,0,1,1],
            [1,1,1,0],
            [1,1,0,1],
            [1,0,1,1],
            [0,1,1,1],
            [1,1,1,1]])
cvar = np.array(['Q', 'ET', 'SWS', 'TWSV'])

def get_labels(cid):
    global csetting, cvar
    labels = []

    cs = csetting[cid-1]
    var_count = sum(cs)

    conj = ''
    if var_count == 2: conj = 'between'
    elif var_count >= 2: conj = 'among'

    vars = cvar[cs.astype(bool)]
    if var_count > 1: labels.append('Pareto-Frontier ' + conj + ' Efficiencies (KGE) in ' + ', '.join(vars[:-1]) + ' and ' + vars[-1])

    for v in vars: labels.append('KGE for %s' % v)
    return labels

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
cid = 6
labels = get_labels(cid)      # B1C13
title = labels.pop(0)
cid = 'B1C' + str(cid).rjust(2, '0')

f = '/media/sf_Experiments/%s_pareto_front.csv'%cid.lower()
d = np.loadtxt(f, delimiter=',')        # read data from file

# step-2: exclude data points outside preferred limits
d = d[~np.isnan(d).any(axis=1)]         # remove rows having any nan value
fx = d[:, 1:]                           # crop objective columns
fx = 1-fx                               # additional step: 1-KGE was used as objective function during calibration.
                                        # thus, it is necessary to convert the objective values back to KGE values

lmt = max([np.min(fx), 0.6])                              # set minimum efficiency limit i.e., min f(x)
print(lmt)
for i in range(fx.shape[1]):            # exclude data below the minimum limit
    fx = fx[fx[:,i]>=lmt,:]
fx.sort()

# step-3: initialize and draw figure
fig = plt.figure()
if fx.shape[1] == 3:
    ax = fig.add_subplot(111, projection='3d')
else: ax = fig.add_subplot(111)
fig.set_facecolor('white')
plt.title(title)


# split data into four dimensions
x, y, z = None, None, None

x = fx[:,0]
y = fx[:,1]

ax.set_ylim(1.01, min([min(y),0.8]))
ax.set_xlim(1.01, min([min(x),0.8]))

ax.xaxis.set_ticks(np.arange(lmt, 1.0, 0.1))
ax.yaxis.set_ticks(np.arange(lmt, 1.0, 0.1))

ax.set_xlabel(labels[0])
ax.set_ylabel(labels[1])
if fx.shape[1] == 3:
    z = fx[:,2]

# plot the scatter diagram
    p = ax.scatter(x, y, z, edgecolors='face', c='green')

    ax.set_zlim(1.01, min([min(z), 0.8]))

    # set axes ticks

    ax.zaxis.set_ticks(np.arange(lmt, 1.0, 0.1))

    # add axes labels

    ax.set_zlabel(labels[2])
else:
    p = ax.scatter(x, y, edgecolors='face', c='green')
# p = ax.plot_trisurf(x, y, z, linewidth=0, antialiased=False)


# set axes limits



# draw the colour bar
# cbar = plt.colorbar(p, ticks=np.arange(lmt,1.0,0.1), pad=0.0, fraction=0.05, aspect=12)
# cbar.outline.set_linewidth(0.8)
# cbar.ax.get_yaxis().labelpad = 15
# cbar.ax.set_ylabel('KGE (TWSV)', rotation=270)

# add the optimal (utopia) point and the chosen best point


if fx.shape[1] == 3:
    p1, p2, p3 = best_point_ed(fx)
    ax.scatter(1, 1, 1, marker='D', edgecolor='face', c='r')
    ax.scatter(p1, p2, p3, marker='+', edgecolor='face', c='r', s=250)
else:
    p1, p2 = best_point_ed(fx)
    ax.scatter(1, 1, marker='D', edgecolor='face', c='r')
    ax.scatter(p1, p2, marker='+', edgecolor='face', c='r', s=250)


# show or save the graph
flag_animation = False
rf_angle1, rf_angle2 = 40, 230
f = 'output/%s_pareto_frontier.png' % cid

if flag_animation:
    h = [0, 10, 20, 30, 20, 10, 0, -10, -20, -30, -40, -30, -20, -10, 0]
    v = [0, 10, 20, 30, 40, 30, 20, 10, 0, -10, -20, -30, -20, -10, 0]

    counter = 0
    for angle in h:
        f1 = f[:-4] + str(counter) + '.png'
        ax.view_init(rf_angle1, rf_angle2 + angle)  # adjust viewing angle
        fig.savefig(f1)
        counter += 1

    for angle in v:
        f1 = f[:-4] + str(counter) + '.png'
        ax.view_init(rf_angle1 + angle, rf_angle2)  # adjust viewing angle
        fig.savefig(f1)
        counter += 1

else:
    # ax.view_init(rf_angle1, rf_angle2)                    # adjust viewing angle
    fig.savefig(f)
plt.show()
plt.close(fig)
