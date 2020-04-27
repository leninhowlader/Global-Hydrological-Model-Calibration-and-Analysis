import sys, os, numpy as np, pandas as pd
from matplotlib import pyplot as plt
sys.path.append('..')


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

    @staticmethod
    def draw_operator_probabilities(
            runtime_reports,
            figsize = (6, 4),
            title = '',
            filename_out = '',
            marker='o',
            markersize=3
    ):
        rr = runtime_reports
        if len(rr) == 0: return None


        nfe = []
        sbx, de, pcx, spx, undx, um = [], [], [], [], [], []

        for r in rr:
            nfe.append(r.nfe)
            sbx.append(r.sbx)
            de.append(r.de)
            pcx.append(r.pcx)
            spx.append(r.spx)
            undx.append(r.undx)
            um.append(r.um)

        nfe =  np.array(nfe)
        sbx, de, pcx = np.array(sbx), np.array(de), np.array(pcx)
        spx, undx, um = np.array(spx), np.array(undx), np.array(um)

        # sort operators according to nfe
        ii = np.argsort(nfe)
        sbx, de, pcx, spx, undx, um = sbx[ii], de[ii], pcx[ii], spx[ii], undx[ii], um[ii]
        nfe = nfe[ii]

        fig = plt.figure(figsize=figsize)
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.88,
                            wspace=None, hspace=None)

        ax = fig.add_subplot(1, 1, 1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)

        ax.plot(nfe, sbx, label='SBX', linestyle=(0, ()), color='green',
                marker=marker, markersize=markersize)
        ax.plot(nfe, pcx, label='PCX', linestyle=(0, (1, 2)), color='green',
                marker=marker, markersize=markersize)
        ax.plot(nfe, spx, label='SPX', linestyle=(0, ()), color='black',
                marker=marker, markersize=markersize)
        ax.plot(nfe, undx, label='UNDX', linestyle=(0, (1, 2)), color='black',
                marker=marker, markersize=markersize)
        ax.plot(nfe, de, label='DE', linestyle=(0, ()), color='red',
                marker=marker, markersize=markersize)
        ax.plot(nfe, um, label='UM', linestyle=(0, (1, 2)), color='red',
                marker=marker, markersize=markersize)

        ax.set_title(title)

        ax.set_ylim(0, 1.0)
        ax.set_xlabel('Number of Function Evaluation')
        ax.set_ylabel('Operator Probability')

        ax.legend(frameon=False)

        if filename_out: fig.savefig(filename_out, dpi=600)

        return fig

    @staticmethod
    def draw_operator_probabilities_among_calibrations(
            sbx, de, pcx, spx, undx, um,
            calibration_names=[],
            title='',
            figsize=(6, 4),
            marker='o',
            markersize=3,
            tight_layout=False,
            filename_out=''
    ):
        # [step] check inputs
        ncalib = sbx.shape[0]
        if ncalib == 0: return None
        if not (de.shape[0] == pcx.shape[0] == spx.shape[0] == undx.shape[0] == um.shape[0]):
            return None
        if calibration_names and len(calibration_names) != ncalib: return None
        # end [step]

        # [step] prepare canvas
        fig = plt.figure(figsize=figsize)
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.88,
                            wspace=None, hspace=None)

        ax = fig.add_subplot(1, 1, 1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)
        # end [step]

        # [step] draw lines
        x = np.arange(1, ncalib + 1)
        ax.plot(x, sbx, label='SBX', linestyle=(0, ()), color='green',
                marker=marker, markersize=markersize)
        ax.plot(x, pcx, label='PCX', linestyle=(0, (1, 2)), color='green',
                marker=marker, markersize=markersize)
        ax.plot(x, spx, label='SPX', linestyle=(0, ()), color='black',
                marker=marker, markersize=markersize)
        ax.plot(x, undx, label='UNDX', linestyle=(0, (1, 2)), color='black',
                marker=marker, markersize=markersize)
        ax.plot(x, de, label='DE', linestyle=(0, ()), color='red',
                marker=marker, markersize=markersize)
        ax.plot(x, um, label='UM', linestyle=(0, (1, 2)), color='red',
                marker=marker, markersize=markersize)
        # end [step]

        ax.set_title(title)

        ax.set_ylim(0, 1.0)
        ax.set_xlabel('Calibration Exercises')
        ax.set_ylabel('Operator Probability')

        ax.xaxis.set_ticks(x)
        if calibration_names:
            ax.xaxis.set_ticklabels(calibration_names, rotation=90)

        ax.legend(frameon=False)

        if tight_layout: fig.tight_layout()

        if filename_out: fig.savefig(filename_out, dpi=600)

        return fig

    @staticmethod
    def draw_paretofront_at_different_nfe_2D(
            ax,
            filename_runtime_dynamics,
            nfes=[1000, 5000, 10000, 20000],
            linestyle=(0, ()),
            marker='*',
            markersize=7,
            do_color_plot=True,
            axis_labels=[]):

        # inner function
        def extract_xy(nfe):
            for rpt in rpt_list:
                if rpt.nfe == nfe:
                    d = np.array(rpt.solutions)[:, -2:] * -1
                    ii = np.argsort(d[:, 1])
                    d = d[ii]

                    x, y = d[:, 0], d[:, 1]
                    return x, y

            return np.empty(0), np.empty(0)

        # end of inner function

        # inner function
        def draw_pf_color(ax, x, y, linestyle, zorder, label=''):
            p = ax.plot(x, y, linestyle=linestyle,
                        marker=marker,
                        markersize=markersize,
                        label=label,
                        zorder=zorder)
            return p

        # end of inner function

        # inner function
        def draw_pf(ax, x, y, linestyle, zorder, label='',
                    markerfacecolor='white'):
            p = ax.plot(x, y, linestyle=linestyle,
                        marker=marker,
                        markersize=markersize,
                        label=label,
                        zorder=zorder,
                        color='black',
                        markerfacecolor=markerfacecolor)
            return p

        # end of inner function
        if not os.path.exists(filename_runtime_dynamics): return None

        rpt_list = RuntimeDynamicReport.read_runtime_dynamic_file(
                                                filename_runtime_dynamics)
        if not rpt_list: return None

        max_pf_count = 4
        pf_styles = [(0, (5, 5)), (0, (2, 2)), (0, (1, 1)), (0, ())]

        nfes.sort()
        if len(nfes) > max_pf_count: nfes = nfes[-max_pf_count:]

        pf_count = len(nfes)
        if pf_count < 4: pf_styles = pf_styles[-pf_count:]

        pf_lines_2D = []
        for i in range(pf_count):
            x, y = extract_xy(nfes[i])

            zorder = pf_count - 1 - i
            label = 'PF after %d NFE' % nfes[i]

            if do_color_plot:
                p = draw_pf_color(ax, x, y, linestyle=pf_styles[i],
                                  zorder=zorder, label=label)
            else:
                markerfacecolor = 'white'
                if i == pf_count - 1: markerfacecolor = 'black'
                p = draw_pf(ax, x, y,
                            linestyle=pf_styles[i],
                            zorder=zorder,
                            label=label,
                            markerfacecolor=markerfacecolor)
            pf_lines_2D += p

        ax.xaxis.tick_top()
        ax.yaxis.tick_right()

        # ax.spines['top'].set_visible(True)
        # ax.spines['right'].set_visible(True)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        if axis_labels:
            ax.set_xlabel(axis_labels[0])
            ax.xaxis.set_label_position('top')

            ax.set_ylabel(axis_labels[1])
            ax.yaxis.set_label_position('right')

        return pf_lines_2D

    @staticmethod
    def paretofront_at_different_nfe_of_two_objective_calibrations(
            runtime_report_files:list,
            axis_labels:list,
            figsize=(12, 7),
            filename_out='',
            markersize=6,
            use_color=True
            ):
        # [step] check input
        nplots = len(runtime_report_files)
        if nplots > 6 or nplots < 1: return False
        if len(axis_labels) != nplots: return False

        for x in axis_labels:
            if len(x) != 2: return False
        # end [step]

        fig = plt.figure(figsize=figsize)

        for i in range(nplots):
            filename_runtime_report = runtime_report_files[i]
            xy_labels = axis_labels[i]

            ax = fig.add_subplot(2, 3, i + 1)

            lines_2D = RuntimeDynamicReport.draw_paretofront_at_different_nfe_2D(
                                                ax,
                                                filename_runtime_report,
                                                axis_labels=xy_labels,
                                                do_color_plot=use_color,
                                                markersize=markersize)

            if i == 3: ax.legend(frameon=False)

        fig.tight_layout()

        if filename_out: fig.savefig(filename_out, dpi=600)

        return True

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
                           funs:list,
                           compute_anomaly=False):
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

            if compute_anomaly: sim, obs = sim - np.mean(sim), obs - np.mean(obs)

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