import sys, os, numpy as np
sys.path.append('..')

import pandas as pd
#from utilities.fileio import FileInputOutput as io


class BorgOutput:
    @staticmethod
    def read_borg_output(filename, delimiter=' '):
        r = []
        
        
        r = np.loadtxt(filename, delimiter=delimiter, ndmin=2)

        return r

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
    
    @staticmethod
    def find_nan_objectives(objs, nanvalue=np.float64('1.79769e+308')):
        return np.where((objs==nanvalue).any(axis=1))[0]

class RuntimeDynamicReport:
    def __init__(self):
        self.nfe = -1
        
        self.sbx = 0
        self.de = 0
        self.pcx = 0
        self.spx = 0
        self.undx = 0
        self.um = 0
        
        self.improvements = 0
        self.restarts = 0
        self.population_size = 0
        self.archive_size = 0
        self.mutation_index = 0
        
        self.solutions = []
        
    @staticmethod
    def read_runtime_dynamic_file(filename):
        
        reports = []
        
        try:
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
            
            rpt = None
            
            for line in lines:
                if line.find('NFE') > 0:
                    if rpt: reports.append(rpt)
                    
                    rpt = RuntimeDynamicReport()
                    
                    try: x = int(line.split('=')[1])
                    except: x = -1
                    
                    rpt.nfe = x
                
                elif line.find('SBX') > 0:
                    try: x = float(line.split('=')[1])
                    except: x = -1
                    
                    rpt.sbx = x
                
                elif line.find('DE') > 0:
                    try: x = float(line.split('=')[1])
                    except: x = -1
                    
                    rpt.de = x
                
                elif line.find('PCX') > 0:
                    try: x = float(line.split('=')[1])
                    except: x = -1
                    
                    rpt.pcx = x
                
                elif line.find('SPX') > 0:
                    try: x = float(line.split('=')[1])
                    except: x = -1
                    
                    rpt.spx = x
                    
                elif line.find('UNDX') > 0:
                    try: x = float(line.split('=')[1])
                    except: x = -1
                    
                    rpt.undx = x
                
                elif line.find('UM') > 0:
                    try: x = float(line.split('=')[1])
                    except: x = -1
                    
                    rpt.um = x
                
                elif line.find('Improvements') > 0:
                    try: x = int(line.split('=')[1])
                    except: x = -1
                    
                    rpt.improvements = x
                
                elif line.find('Improvements') > 0:
                    try: x = int(line.split('=')[1])
                    except: x = -1
                    
                    rpt.improvements = x
                    
                elif line.find('Restarts') > 0:
                    try: x = int(line.split('=')[1])
                    except: x = -1
                    
                    rpt.restarts = x
                    
                elif line.find('PopulationSize') > 0:
                    try: x = int(line.split('=')[1])
                    except: x = -1
                    
                    rpt.population_size = x
                    
                elif line.find('ArchiveSize') > 0:
                    try: x = int(line.split('=')[1])
                    except: x = -1
                    
                    rpt.archive_size = x
                    
                elif line.find('MutationIndex') > 0:
                    try: x = int(line.split('=')[1])
                    except: x = -1
                    
                    rpt.mutation_index = x
                    
                else:
                    temp = line.split(' ')
                    if len(temp) > 1:
                        try:
                            for i in range(len(temp)): temp[i] = float(temp[i])
                        except: temp = []
                        if temp: rpt.solutions.append(temp)
            
            if rpt: reports.append(rpt)
        except: pass
        
        return reports

class BorgSolutionEvaluation:

    @staticmethod
    def prediction_time_series(data: np.ndarray, prediction_id: int):
        # extract prediction of single model run
        ii = np.where(data[:, 0] == prediction_id)[0]
        d = data[ii, -13:]

        # sort by year
        ii = np.argsort(d[:, 0])
        d = d[ii]

        # add year and month column
        nyear = d.shape[0]
        y = d[:, 0].repeat(12).reshape(-1, 1)
        m = np.arange(1, 12 + 1).reshape(1, 12).repeat(nyear, axis=0).reshape(
            -1, 1)
        d = np.concatenate((y, m, d[:, 1:].reshape(-1, 1)), axis=1)

        # create and return data frame
        return pd.DataFrame(data=d, columns=['year', 'month', 'prediction'])

    @staticmethod
    def observation_time_series(filename):
        df = pd.read_csv(filename, delimiter=',')

        df = df.iloc[:, 1:]
        df.columns.values[-1] = 'observation'

        return df

    @staticmethod
    def couple_prediction_observation(predictions: pd.DataFrame,
                                      observations: pd.DataFrame):
        d = predictions.merge(observations, on=['year', 'month'], how='inner')

        sim, obs = d.prediction.values, d.observation.values

        return sim, obs

    @staticmethod
    def compute_objectives(filename_prediction:pd.DataFrame,
                           filename_observation:pd.DataFrame,
                           funs:list):
        from wgap.wgapio import WaterGapIO as wio
        __self = BorgSolutionEvaluation

        fx = np.empty(0)

        observations = __self.observation_time_series(filename_observation)

        data = wio.read_unf(filename_prediction)
        if data.shape[0] == 0: return fx

        ids = np.unique(data[:, 0])
        for id in ids:
            predictions = __self.prediction_time_series(data, id)

            sim, obs = __self.couple_prediction_observation(predictions,
                                                            observations)
            x = np.array([f(sim, obs) for f in funs]).reshape(1, -1)
            try: fx = np.concatenate((fx, x), axis=0)
            except: fx = x

        return fx

    @staticmethod
    def compute_storage_sum(directory_sim, filename_out, *filenames_storage):
        from wgap.wgapio import WaterGapIO as wio

        if not filename_out: return False

        # check length of input filenames
        nvars = len(filenames_storage)
        if nvars < 2: return False

        # read simulated storages
        storages = []
        for i in range(nvars):
            f = os.path.join(directory_sim, filenames_storage[i])
            if not os.path.exists(f): return False

            d = wio.read_unf(f)
            if d.shape[0] == 0: return False

            storages.append(d)

        # check shape of all prediction variables
        shape = storages[-1].shape
        for i in range(nvars - 1):
            if storages[i].shape != shape: return False

        # sort indices (column 1 to 3)
        for i in range(nvars):
            d = storages[i]
            ii = np.lexsort((d[:, 2], d[:, 1], d[:, 0]))
            storages[i] = d[ii]

        # check whether the indices of each storage variable is the same or not
        ind = storages[-1][:, :3]
        for i in range(nvars - 1):
            if np.sum(storages[i][:, :3] - ind) != 0: return False

        # sum all storage variable
        storage_sum = storages[-1][:, -12:]
        for i in range(nvars - 1): storage_sum += storages[i][:, -12:]

        # export storage sum into file
        filename_out = os.path.join(directory_sim, filename_out)
        data_out = np.concatenate((ind, storage_sum), axis=1)

        return wio.write_unf(filename_out, data=data_out)