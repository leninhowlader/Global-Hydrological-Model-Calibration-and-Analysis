import sys, numpy as np
sys.path.append('..')
from utilities.fileio import read_flat_file


class BorgOutput:
    @staticmethod
    def read_borg_output(filename, separator=' '):
        result_set = []

        h, result_set = read_flat_file(filename, separator=separator, header=False)

        return result_set

    @staticmethod
    def find_best_parameterset(optimals, nobj, wts=[]):
        ndx = -1
        best_paramset = []
        if wts and len(wts) != nobj: return best_paramset, ndx

        if optimals and nobj > 0:
            optimals = np.array(optimals)

            cumd = np.array([0.0]*len(optimals))
            if not wts:
                for i in range(1,nobj+1):
                    temp = optimals[:, -i]
                    mn = np.min(temp)
                    cumd += (temp - mn)
            else:
                for i in range(1,nobj+1):
                    wt = abs(wts[-i])
                    temp = optimals[:, -i]
                    mn = np.min(temp)
                    cumd += (temp - mn) * wt

            try: ndx = cumd.argmin()
            except: pass

            if ndx > -1: best_paramset = list(optimals[ndx][:-nobj])


        return best_paramset, ndx