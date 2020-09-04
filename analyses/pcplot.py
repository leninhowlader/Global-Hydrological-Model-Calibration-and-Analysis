
import numpy as np
from datetime import datetime

class ParallelCoordinatePlot:
    @staticmethod
    def parameter_pairs(n):
        pairs = []
        for i in range(n - 1):
            for j in range(i + 1, n): pairs.append(set([i, j]))
        return pairs

    @staticmethod
    def remove_included_pairs(pairs, ii):
        def interacted_pairs(ii):
            return [set([ii[i], ii[i + 1]]) for i in range(len(ii) - 1)]

        actpairs = interacted_pairs(ii)
        for i in reversed(range(len(pairs))):
            if pairs[i] in actpairs: t = pairs.pop(i)

    @staticmethod
    def new_combination(pairs):
        def get_orders(list_of_pairs):
            ii = []
            for pair in list_of_pairs:
                p = pair.copy()
                x = p.pop()
                if x not in ii: ii.append(x)

                x = p.pop()
                if x not in ii: ii.append(x)
            return ii

        def next_pair(pair, current_order):
            if current_order:
                x = current_order[-1]

                for i in range(len(pairs)):
                    if x in pairs[i]:
                        if list(pairs[i] - set([x]))[0] not in current_order[
                                                               :-1]:
                            return pairs.pop(i)

            else:
                p = pair.copy()

                x = p.pop()
                for i in range(len(pairs)):
                    if x in pairs[i]: return pairs.pop(i)

                x = p.pop()
                for i in range(len(pairs)):
                    if x in pairs[i]: return pairs.pop(i)

            return set()

        temp, param_orders = [], []

        if pairs:
            np.random.seed = datetime.now().microsecond
            i_rand = np.random.randint(0, len(pairs))
            pair = pairs.pop(i_rand)

            while pair:
                temp.append(pair)
                param_orders = get_orders(temp)

                pair = next_pair(pair, param_orders)

        return param_orders

    @staticmethod
    def parameter_combinations(n):
        pairs = ParallelCoordinatePlot.parameter_pairs(n)

        combinations = []
        ii = list(range(n))

        while ii:
            if len(ii) != n: ii += list(set(range(n)) - set(ii))
            combinations.append(ii)

            ParallelCoordinatePlot.remove_included_pairs(pairs, ii)
            ii = ParallelCoordinatePlot.new_combination(pairs)

        return combinations