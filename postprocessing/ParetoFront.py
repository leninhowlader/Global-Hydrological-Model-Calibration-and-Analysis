import numpy as np
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