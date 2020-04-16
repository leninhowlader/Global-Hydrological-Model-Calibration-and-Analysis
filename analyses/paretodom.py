import os, numpy as np
from enum import Enum
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D         # required for 3D plotting


class Dominance(Enum):
    DOMINATES = -2,
    DOMINATES_SAME_BOX = -1,
    NONDOMINATED = 0,
    DOMINATED_SAME_BOX = 1,
    DOMINATED = 2

class ParetoDominance():
    @staticmethod
    def dominance(u, v, PSEUDO_EPSILON=None):
        # input: u, v (array): objectives of two solutions
        # output: (Dominance)
        #       DOMINATES = u dominates v
        #       NONDOMINATED = u and v are non-dominated
        #       DOMINATED = u is dominated by v (or v dominates u)

        dominate1, dominate2 = 0, 0
        num_obj = len(u)

        for i in range(num_obj):
            if u[i] < v[i]:
                dominate1 = 1
                if dominate2: return Dominance.NONDOMINATED
            elif u[i] > v[i]:
                dominate2 = 1
                if dominate1: return Dominance.NONDOMINATED

        if dominate1 == dominate2: return Dominance.NONDOMINATED
        elif dominate1: return Dominance.DOMINATES
        else: return Dominance.DOMINATED

    @staticmethod
    def epsilon_box_dominance(u, v, epsilons):
        # input:
        #       u, v (array): objectives of two solutions
        #       epsilon (array): objectives thresholds
        # output: (Dominance)
        #       DOMINATES = u dominates v
        #       DOMINATES_SAME_BOX = u dominates v within the grid cell
        #       NONDOMINATED = u and v are non-dominated
        #       DOMINATED_SAME_BOX = u is dominated by v within the grid cell i.e., v dominates u
        #       DOMINATED = u is dominated by v (or v dominates u)

        dominate1, dominate2 = 0, 0
        for i in range(len(u)):
            epsilon = epsilons[i]
            index1, index2 = np.floor(u[i]/epsilon), np.floor(v[i]/epsilon)

            if index1 < index2:
                dominate1 = 1
                if dominate2: return Dominance.NONDOMINATED
            elif index1 > index2:
                dominate2 = 1
                if dominate1: return Dominance.NONDOMINATED

        if not dominate1 and not dominate2:
            dist1, dist2 = 0, 0
            for i in range(len(u)):
                epsilon = epsilons[i]
                index1, index2 = np.floor(u[i] / epsilon), np.floor(v[i] / epsilon)

                dist1 += (u[i] - index1 * epsilon) ** 2
                dist2 += (v[i] - index2 * epsilon) ** 2

            if dist1 < dist2: return Dominance.DOMINATES_SAME_BOX
            else: return Dominance.DOMINATED_SAME_BOX
        elif dominate1: return Dominance.DOMINATES
        else: return Dominance.DOMINATED

    @staticmethod
    def ParetoFront(fx, funname='pareto-box dominance', epsilons=None):
        fx = np.array(fx)

        if funname.replace('-', '').replace(' ', '').replace('_', '').lower() == 'paretodominance' or funname == 1 or epsilons == None:
            fun = ParetoDominance.dominance
        else: fun = ParetoDominance.epsilon_box_dominance

        if epsilons and len(epsilons) != fx.shape[1]: return None, None
        ndces = []

        for i in range(fx.shape[0]):
            add = True
            for j in reversed(range(len(ndces))):
                dominance = fun(fx[i], fx[ndces[j]], epsilons)
                if dominance in [Dominance.DOMINATES, Dominance.DOMINATES_SAME_BOX]: ndces.pop(j)
                elif dominance in [Dominance.DOMINATED, Dominance.DOMINATED_SAME_BOX]:
                    add = False
                    break

            if add: ndces.append(i)

        mask = np.zeros(fx.shape[0], dtype=bool)
        mask[ndces] = True

        return fx[mask], ndces

    @staticmethod
    def Rotation_R2(vectors:np.ndarray, theta:float, origin:tuple=(0,0)):
        '''
        Rotates vectors in R^2 space by specified angle

        :param vectors (2d-array)   : list of vectors
        :param theta (float)        : rotation angle in degree
        :param origin (tuple; optional) : origin of R^2 space. default value (0,0)
        :return (2d-array)          : rotated vectors
        '''
        if theta == 0: return vectors

        ox, oy = origin
        angle = np.radians(theta)

        rotated_fx = []
        for point in vectors:
            px, py = point

            qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
            qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)

            rotated_fx.append([qx, qy])

        return np.array(rotated_fx)

    @staticmethod
    def FalseParetoFront_2D(fx:np.ndarray, rotation_start:int=-60, rotation_end:int=60, rotation_interval:int=15):
        '''
        Finds false Pareto Front in 2D objective space.

        :param fx: (2d-array) objective values
        :param rotation_start: (int, optional, default=-60) starting angle in Degree for rotation of objective space
        :param rotation_end: (int, optional, default=60) ending angle in Degree for rotation of objective space
        :param rotation_interval: (int, optional, default=15) interval angle in Degree
        :return: (tuple of (2d-array, 1d-array)) False Pareto Front and their indices
        '''
        pf, indices = [], []
        if fx.shape[1] != 2: return np.array(pf)

        for theta in range(rotation_start, rotation_end + 1, rotation_interval):
            temp_fx = ParetoDominance.Rotation_R2(fx, theta)
            temp_fx, ndx = ParetoDominance.ParetoFront(temp_fx)

            # t1 = [tuple(fx[i]) for i in ndx]
            # for i in range(len(t1)):
            #     if t1[i] not in pf: pf.append(t1[i])
            
            for i in ndx:
                t = tuple(fx[i])
                if t not in pf:
                    pf.append(t)
                    indices.append(i)
        
        return np.array(pf), indices

class ParetoFrontPlot:
    @staticmethod
    def get_index_of_compromised_solutions(fx, threshold):
        return np.where((fx>threshold).all(axis=1))[0]

    @staticmethod
    def plot_pareto_front_4d(fx, figsize=(7, 6), xyz_2d_projection=True):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(left=0.1, bottom=0.05, right=0.95, top=.85,
                            wspace=None, hspace=None)
        fig.set_facecolor('white')
        title = '(a) Ganges'
        plt.suptitle(title, fontsize=22, style='italic')

        # split data into four dimensions
        x = fx[:, 0]
        y = fx[:, 3]
        z = fx[:, 2]
        c = fx[:, 1]  # the fourth dimension will be shown as color map

        # plot the scatter diagram
        p = ax.scatter(x, y, z, c=c, cmap=plt.get_cmap('winter'),
                       edgecolors='face', s=30, vmin=0.6, vmax=1.0)

        if xyz_2d_projection:
            ax.plot(x, z, '+', zdir='y', zs=0.4, color='grey', markersize=8,
                    linewidth=1.3)  # color='blueviolet'
            ax.plot(y, z, '+', zdir='x', zs=0.4, color='grey', markersize=8,
                    linewidth=1.3)  # color='peru'
            ax.plot(x, y, '+', zdir='z', zs=0.4, color='grey', markersize=8,
                    linewidth=1.3)  # color='magenta')

            utopia = np.array([1.0])
            ax.plot(utopia, utopia, '+', zdir='y', zs=0.4, color='black',
                    markersize=8, markeredgewidth=2)  # color='blueviolet'
            ax.plot(utopia, utopia, '+', zdir='x', zs=0.4, color='black',
                    markersize=8, markeredgewidth=2)  # color='peru'
            ax.plot(utopia, utopia, '+', zdir='z', zs=0.4, color='black',
                    markersize=8, markeredgewidth=2)

        lim_lo, lim_hi = 0.4, 1.05

        ax.set_xlim([lim_lo, lim_hi])
        ax.set_ylim([lim_lo, lim_hi])
        ax.set_zlim([lim_lo, lim_hi])

        # set axes ticks
        ax.xaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, 0.1))
        ax.yaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, 0.1))
        ax.zaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, 0.1))

        ax.tick_params(axis='both', which='major', labelsize=15)

        # add axes labels
        ax.set_xlabel('$f_1$: kge (q)', fontsize=20)
        ax.set_ylabel('$f_4$: kge (twsv)', fontsize=20)
        ax.set_zlabel('$f_3$: kge (sws)', fontsize=20)

        ax.xaxis.labelpad = 20
        ax.yaxis.labelpad = 20
        ax.zaxis.labelpad = 20

        # draw the colour bar
        cbar = plt.colorbar(p, ticks=np.arange(0.6, 1.01, 0.1), pad=0.01,
                            fraction=0.05, aspect=30)
        cbar.ax.tick_params(labelsize=15)
        cbar.outline.set_linewidth(0.6)
        cbar.ax.get_yaxis().labelpad = -50
        cbar.ax.get_yaxis().set_ticks_position('right')

        cbar.ax.set_ylabel('$f_2$: kge (et)', rotation=270, fontsize=20)
        # add the optimal (utopia) point and the chosen best point
        ax.scatter(1, 1, 1, marker='o', edgecolor='face', c='r', zorder=-1,
                   s=40)
        ii = ParetoFrontPlot.get_index_of_compromised_solutions(fx, 0.85)
        bp = fx[ii]

        p1 = bp[:, 0]
        p2 = bp[:, 3]
        p3 = bp[:, 2]
        ax.scatter(p1, p2, p3, marker='o', edgecolor='face', c='black', s=60,
                   zorder=-1, linewidths=1.5)

        # show or save the graph
        # ax.view_init(35,-135)                    # adjust viewing angle
        ax.view_init(27, 25)
        f = 'pf_Ganges_C15.png'
        fig.savefig(f)
        # fig.tight_layout()
        plt.show()
