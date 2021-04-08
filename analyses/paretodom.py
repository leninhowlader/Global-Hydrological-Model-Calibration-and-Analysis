import os, numpy as np
from enum import Enum

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

