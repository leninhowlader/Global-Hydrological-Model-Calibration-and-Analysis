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

def get_labels(cid, sl='(a)'):
    global csetting, cvar
    labels = []

    cs = csetting[cid-1]
    var_count = sum(cs)

    # conj = ''
    # if var_count == 2: conj = 'between'
    # elif var_count >= 2: conj = 'among'

    vars = cvar[cs.astype(bool)]
    if var_count > 1: labels.append(sl + ' PF for ' + vars[0] + ' and ' + vars[1])

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
cid = 10
labels = get_labels(cid, '(f)')      # B1C13
title = labels.pop(0)
cid = 'B1C' + str(cid).rjust(2, '0')

f = '/media/sf_Experiments/%s_pareto_front.csv'%cid.lower()
d = np.loadtxt(f, delimiter=',')        # read data from file

# step-2: exclude data points outside preferred limits
d = d[~np.isnan(d).any(axis=1)]         # remove rows having any nan value
fx = d[:, 1:]                           # crop objective columns
fx = 1-fx                               # additional step: 1-KGE was used as objective function during calibration.
                                        # thus, it is necessary to convert the objective values back to KGE values

lmt = 0.6                             # set minimum efficiency limit i.e., min f(x)
print(lmt)
for i in range(fx.shape[1]):            # exclude data below the minimum limit
    fx = fx[fx[:,i]>=lmt,:]


# step-3: initialize and draw figure
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111)
fig.set_facecolor('white')
plt.suptitle(title, fontsize=22, style='italic')


# split data into four dimensions
x = fx[:,0]
y = fx[:,1]

xlim_lo = round(min([min(x),0.8])*10)*0.1
ylim_lo = round(min([min(y),0.8])*10)*0.1

ax.set_ylim(1.01, ylim_lo)
ax.set_xlim(1.01, xlim_lo)

ax.xaxis.set_ticks(np.arange(xlim_lo, 1.01, 0.1))
ax.yaxis.set_ticks(np.arange(ylim_lo, 1.01, 0.1))

ax.set_xlabel(labels[0], fontsize=20)
ax.set_ylabel(labels[1], fontsize=20)
ax.tick_params(axis='both', which='major', labelsize=20)
p = ax.scatter(x, y, edgecolors='face', c='black', marker='o', s=100)
# p = ax.plot_trisurf(x, y, z, linewidth=0, antialiased=False)


# set axes limits



# draw the colour bar
# cbar = plt.colorbar(p, ticks=np.arange(lmt,1.0,0.1), pad=0.0, fraction=0.05, aspect=12)
# cbar.outline.set_linewidth(0.8)
# cbar.ax.get_yaxis().labelpad = 15
# cbar.ax.set_ylabel('KGE (TWSV)', rotation=270)

# add the optimal (utopia) point and the chosen best point



p1, p2 = best_point_ed(fx)
ax.scatter(1, 1, marker='o', edgecolor='face', c='r', s=150)
ax.scatter(p1, p2, marker='+', edgecolor='face', c='r', s=500, linewidths=4)


# show or save the graph
f = '/media/sf_Experiments/%s_pareto_frontier.png' % cid
fig.savefig(f)
plt.show()
plt.close(fig)
