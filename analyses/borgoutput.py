import sys, os, numpy as np, pandas as pd
from matplotlib import pyplot as plt, patches
from collections import OrderedDict
from datetime import datetime
from calendar import monthrange

sys.path.append('..')
from wgap.wgapio import WaterGapIO as wio

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
    def get_operators_probabilities(
            report_filenames:list,
            nfe=20000
    ):
        self = RuntimeDynamicReport

        sbx, de, pcx, spx, undx, um = [], [], [], [], [], []

        for filename in report_filenames:
            reports = self.read_runtime_dynamic_file(filename)
            for report in reports:
                if report.nfe == nfe:
                    sbx.append(report.sbx)
                    de.append(report.de)
                    pcx.append(report.pcx)
                    spx.append(report.spx)
                    undx.append(report.undx)
                    um.append(report.um)
                    break
        sbx, de, pcx = np.array(sbx), np.array(de), np.array(pcx)
        spx, undx, um = np.array(spx), np.array(undx), np.array(um)

        return sbx, de, pcx, spx, undx, um

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
            axis_labels=[]
    ):

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

    @staticmethod
    def paretofront_improvement_over_nfe(
            runtime_report_files:list,
            series_labels:list,
            is_multi_objective:bool=False,
            report_minimum_euclidian_distance:bool=True,
            report_average_euclidian_distance:bool=False,
            nobjectives=1,
            figsize:tuple=(7, 5),
            title:str='',
            linestyles:list=[],
            marker='o', markersize=3,
            show_grid_xaxis:bool=False, show_grid_yaxis:bool=False,
            apply_tight_layout:bool=True,
            filename_out:str='',
            xticks=(), yticks=()
    ):
        self = RuntimeDynamicReport

        # inner function
        def summary(objs:np.ndarray):
            ed = np.sqrt(np.power(1-objs, 2).sum(axis=1))

            if report_minimum_euclidian_distance:
                i = np.argmin(ed)
                return ed[i].reshape(1)
            else:
                ii = np.argsort(ed)[:objs.shape[0] // 2]
                if report_average_euclidian_distance:
                    return ed[ii].mean().reshape(1)
                else: return objs[ii].mean().reshape(1)
        # end of inner function

        # inner function
        def extract_xy(reports, nobjs):
            nfes = []

            objectives = np.empty(0)
            for report in reports:
                nfes.append(report.nfe)

                o = np.array(report.solutions)[:,-nobjs:] * -1
                if is_multi_objective: o = summary(o)

                try: objectives = np.concatenate((objectives, o), axis=0)
                except: objectives = o

            nfes = np.array(nfes)
            ii = np.argsort(nfes)

            return nfes[ii], objectives[ii]
        # end of inner function

        # inner function

        # end of inner function

        # [step] check inputs
        ncal = len(runtime_report_files)
        if ncal == 0: return False

        if len(series_labels) != ncal: return False

        if not is_multi_objective: nobjectives = 1
        else:
            if (type(nobjectives) is np.ndarray or
                type(nobjectives) is list) and len(nobjectives) != ncal: return False

            if type(nobjectives) is int:
                if nobjectives <= 1: return False
                else: nobjectives = [nobjectives] * ncal

        in_color = True
        if len(linestyles) == ncal: in_color = False
        # end [step]

        # [step] create canvas
        fig = plt.figure(figsize=figsize)
        fig.subplots_adjust(left=0.15, bottom=0.1, right=0.9, top=0.9,
                            wspace=None, hspace=None)
        # end [step]

        # [step] add plot and set visibility of spines
        ax = fig.add_subplot(1, 1, 1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)
        # end [step]

        for i in range(ncal):
            reports = self.read_runtime_dynamic_file(runtime_report_files[i])
            if len(reports) == 0: return False

            if is_multi_objective: nobjs = nobjectives[i]
            else: nobjs = 1

            x, y = extract_xy(reports, nobjs)
            x = x/1000

            label = series_labels[i]

            if in_color:
                ax.plot(x, y, marker=marker, markersize=markersize,
                        label=label)
            else:
                ax.plot(x, y, color='black', linestyle=linestyles[i],
                        marker=marker, markersize=markersize,
                        label=label)

        # [step] manipulate axis properties
        ax.set_xlabel('NFE (in Thousands)', fontsize=15, labelpad=15)

        if xticks: ax.xaxis.set_ticks(xticks)
        else: ax.xaxis.set_ticks(np.arange(0, 21, 5, dtype=int))

        ax.set_xlim(0, 20)
        ax.xaxis.set_tick_params(direction='out', which='both', labelsize=15)

        ax.set_ylabel('NSE', fontsize=15, labelpad=15)

        if yticks: ax.yaxis.set_ticks(yticks)

        ax.yaxis.set_ticks_position('left')
        ax.yaxis.set_tick_params(direction='out', which='both', labelsize=15)
        # end [step]

        # [step] add grid
        if show_grid_yaxis:
            ax.yaxis.grid(which='major', linestyle='--', color='silver',
                          zorder=-1)
        if show_grid_xaxis:
            ax.xaxis.grid(which='major', linestyle='--', color='silver',
                          zorder=-1)
        # end [step]

        # [step] set title
        if title: ax.set_title(title, fontsize=18, fontweight='none')
        # end [step]

        # [step] add legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), frameon=False,
                  fontsize=12, ncol=2)
        # end [step]

        # [step] apply tight layout
        if apply_tight_layout: fig.tight_layout()
        # end [step]

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

    @staticmethod
    def top_solutions(
            solution_ids,
            number_of_top_solution,
            selection_method='euclid',
            solution_fx:np.ndarray=np.empty(0),
            prediction_dumpfile='',
            observation_filename='',
            compute_anomaly=False
    ):
        # inner function
        def rmse(sim, obs):
            try: return np.sqrt(np.mean((obs - sim) ** 2))
            except: return np.nan
        # end of inner function

        self = BorgSolutionEvaluation

        obs_data, sim_data = pd.DataFrame(), np.empty(0)
        # [step] check inputs
        nsol = solution_ids.shape[0]
        ntop = number_of_top_solution

        if nsol == 0: return np.empty(0)
        if selection_method not in ['rmse', 'euclid']: return np.empty(0)

        if selection_method == 'rmse':
            if observation_filename == '': return np.empty(0)
            if prediction_dumpfile == '': return np.empty(0)

            obs_data = self.observation_time_series(observation_filename)
            if obs_data.shape[0] == 0: return np.empty(0)

            sim_data = wio.read_unf(prediction_dumpfile)
            if sim_data.shape[0] == 0: return np.empty(0)
        else:
            if solution_fx.shape[0] != nsol: return np.empty(0)
        # end [step]

        if selection_method == 'rmse':
            if compute_anomaly: obs_data.observation -= obs_data.observation.mean()

            errors = []
            for sid in solution_ids:
                pred = BorgSolutionEvaluation.prediction_time_series(sim_data,
                                                                     sid)
                if compute_anomaly:
                    pred.prediction -= pred.prediction.mean()

                s, o = BorgSolutionEvaluation.couple_prediction_observation(
                    pred, obs_data)
                errors.append(rmse(s, o))

            errors = np.array(errors)
            ii = np.argsort(errors)[:ntop]
        else:
            if solution_fx.ndim ==1: ed = np.power(1-solution_fx, 2)
            else: ed = np.power(1-solution_fx, 2).sum(axis=1)


            ii = np.argsort(ed)[:ntop]

        return solution_ids[ii]

    @staticmethod
    def top_solution_indices(
            solution_ids,
            number_of_top_solution,
            selection_method='euclid',
            solution_fx:np.ndarray=np.empty(0),
            prediction_dumpfile='',
            observation_filename='',
            compute_anomaly=False
    ):
        # inner function
        def rmse(sim, obs):
            try: return np.sqrt(np.mean((obs - sim) ** 2))
            except: return np.nan
        # end of inner function

        self = BorgSolutionEvaluation

        obs_data, sim_data = pd.DataFrame(), np.empty(0)
        # [step] check inputs
        nsol = solution_ids.shape[0]
        ntop = number_of_top_solution

        if nsol == 0: return np.empty(0)
        if selection_method not in ['rmse', 'euclid']: return np.empty(0)

        if selection_method == 'rmse':
            if observation_filename == '': return np.empty(0)
            if prediction_dumpfile == '': return np.empty(0)

            obs_data = self.observation_time_series(observation_filename)
            if obs_data.shape[0] == 0: return np.empty(0)

            sim_data = wio.read_unf(prediction_dumpfile)
            if sim_data.shape[0] == 0: return np.empty(0)
        else:
            if solution_fx.shape[0] != nsol: return np.empty(0)
        # end [step]

        if selection_method == 'rmse':
            if compute_anomaly: obs_data.observation -= obs_data.observation.mean()

            errors = []
            for sid in solution_ids:
                pred = BorgSolutionEvaluation.prediction_time_series(sim_data,
                                                                     sid)
                if compute_anomaly:
                    pred.prediction -= pred.prediction.mean()

                s, o = BorgSolutionEvaluation.couple_prediction_observation(
                    pred, obs_data)
                errors.append(rmse(s, o))

            errors = np.array(errors)
            ii = np.argsort(errors)[:ntop]
        else:
            if solution_fx.ndim ==1: ed = np.power(1-solution_fx, 2)
            else: ed = np.power(1-solution_fx, 2).sum(axis=1)


            ii = np.argsort(ed)[:ntop]

        return ii

    @staticmethod
    def plot_predictions_with_solutions(
            prediction_dumpfile,
            solution_ids,
            observation_filename='',
            standard_model_dumpfile='',
            compute_anomaly=False,
            solution_fx:np.ndarray=np.empty(0),
            accept_lim=0.4,
            show_top_solutions=0,
            top_selection_method='euclid',    # options: 'rmse', 'euclid'
            top_solution_ids=np.empty(0),
            figsize = (14, 5),
            filename_out = '',
            title='',
            apply_tightlayout=False,
            ylim=(), yticks=(), yticklabels=[], ylabel='',
            xlim=(), xticks=(), xticklabels=[], xlabel='',
            color_allsolution='silver', color_topsolution = 'lime',
            color_observation='dodgerblue', color_stdpmodel = 'red',
            linestyle_allsolution = '-', linestyle_topsolution = '-',
            linestyle_observation = '-', linestyle_stdmodel = '--',
            show_month_averages=False,
            start_year=-1, end_year=-1,
            rotate_xticklabel=False
    ):
        self = BorgSolutionEvaluation

        # inner function
        def monthenddate(years: np.ndarray, months: np.ndarray):
            def enddate(year, month):
                return datetime(year, month, monthrange(year, month)[1])

            dates = np.array([enddate(int(years[i]), int(months[i])) for i
                              in range(len(years))], dtype=np.datetime64)

            return dates.reshape(-1, 1)
        # end of inner function

        # inner function
        def generate_year_month_pair(start_year, end_year):
            years = np.repeat(np.arange(start_year, end_year + 1), 12).reshape(
                -1, 1)
            months = np.repeat(np.arange(1, 12 + 1)[np.newaxis, :],
                               (end_year-start_year+1), axis=0).reshape(-1,1)
            yrmon = pd.DataFrame(data=np.concatenate((years, months), axis=1),
                                 columns=['year', 'month'])
            return yrmon
        # end of inner function

        # inner function
        def find_start_and_end_year():
            yrs = np.unique(data_sim[:, 2]).astype(int)
            return yrs.min(), yrs.max()
        # end of inner function

        # inner function
        def extract_predictions_multiple(sids, monthly_average=False):
            predicts = np.empty(0)

            if monthly_average:
                for sid in sids:
                    p = self.prediction_time_series(data_sim, sid)
                    p = p[(p.year >= start_year) & (p.year <= end_year)]
                    if compute_anomaly: p.prediction -= p.prediction.mean()
                    p = p.iloc[:, -2:].groupby(by='month').mean().\
                        prediction.values.reshape(-1, 1)

                    try: predicts = np.concatenate((predicts, p), axis=1)
                    except: predicts = p
            else:
                for sid in sids:
                    p = self.prediction_time_series(data_sim, sid)
                    p = p[(p.year >= start_year) & (p.year <= end_year)]
                    if compute_anomaly: p.prediction -= p.prediction.mean()
                    p = p.prediction.values.reshape(-1, 1)

                    try: predicts = np.concatenate((predicts, p), axis=1)
                    except: predicts = p

            return predicts
        # end of inner function

        # inner function
        def rmse(sim, obs):
            try: return np.sqrt(np.mean((obs - sim) ** 2))
            except: return np.nan
        # end of inner function

        # [step] check inputs
        if len(solution_ids) == 0: return None

        if top_solution_ids.shape[0] > 0: show_top_solutions = top_solution_ids.shape[0]
        if show_top_solutions >  len(solution_ids):
            show_top_solutions = 0
            color_allsolution = 'green'
        if solution_ids.shape[0] == 1:
            color_allsolution = 'tomato'
            color_observation = 'dodgerblue'
            linestyle_observation = (1, (5, 2))
        # end [step]

        # [step] read simulation dump file
        data_sim = wio.read_unf(prediction_dumpfile)
        if data_sim.shape[0] == 0: return None
        # end [step]

        # [step] prepare data that would be plotted
        data_plot = OrderedDict()

        # x-axis data: dates or month numbers
        if start_year <=1900 or end_year <= 1900 or start_year > end_year:
            start_year, end_year = find_start_and_end_year()

        yrmon = generate_year_month_pair(start_year, end_year)
        if show_month_averages:
            x = np.arange(1, 12 + 1)
            if not xticks: xticks = x.tolist()
            if not xticklabels:
                xticklabels = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                               'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        else: x = monthenddate(yrmon.iloc[:, 0].values, yrmon.iloc[:, 1].values)

        # prediction with borg solutions
        if solution_fx.shape[0] == len(solution_ids):
            if solution_fx.ndim == 1: ii = np.where(solution_fx>=accept_lim)
            else: ii = np.where((solution_fx>=accept_lim).all(axis=1))

            y = extract_predictions_multiple(solution_ids[ii], show_month_averages)
            #if compute_anomaly: y = y - y.mean(axis=0)
            data_plot['Pareto solution'] = {'data': y,
                                                 'linestyle': linestyle_allsolution,
                                                 'color': color_allsolution}

        else:
            y = extract_predictions_multiple(solution_ids, show_month_averages)
            #if compute_anomaly: y = y - y.mean(axis=0)
            data_plot['Pareto solution'] = {'data': y,
                                           'linestyle': linestyle_allsolution,
                                           'color': color_allsolution}

        # prediction of top solutions
        obs = pd.DataFrame()
        if show_top_solutions > 0:
            if top_solution_ids.shape[0] == 0:
                if top_selection_method == 'rmse':
                    top_solution_ids = self.top_solutions(
                                        solution_ids=solution_ids,
                                        number_of_top_solution=show_top_solutions,
                                        selection_method=top_selection_method,
                                        prediction_dumpfile=prediction_dumpfile,
                                        observation_filename=observation_filename
                                        )
                else:
                    top_solution_ids = self.top_solutions(
                                        solution_ids=solution_ids,
                                        number_of_top_solution=show_top_solutions,
                                        selection_method='euclid',
                                        solution_fx=solution_fx
                                        )

            nsol = top_solution_ids.shape[0]
            y = extract_predictions_multiple(top_solution_ids, show_month_averages)
            #if compute_anomaly: y = y - y.mean(axis=0)
            data_plot['Top %d solution(s)'%nsol] = {'data': y,
                                                    'linestyle': linestyle_topsolution,
                                                    'color': color_topsolution}

        # observations
        if observation_filename:
            if obs.shape[0] == 0:
                obs = self.observation_time_series(
                                                observation_filename)
            obs = yrmon.merge(right=obs, how='left', on=['year', 'month'])

            if compute_anomaly: obs.observation -= obs.observation.mean()
            if show_month_averages:
                obs = obs.iloc[:, -2:].groupby(by='month').mean()
            data_plot['Observations'] = {'data': obs.observation.values,
                                         'linestyle': linestyle_observation,
                                         'color': color_observation}

        # standard model prediction
        if standard_model_dumpfile:
            std = wio.read_unf(standard_model_dumpfile)

            if std.shape[0] > 0:
                std = self.prediction_time_series(std, 0)
                std = std[(std.year >= start_year) & (std.year <= end_year)]
                std = yrmon.merge(right=std, how='left', on=['year', 'month'])

                if show_month_averages:
                    std = std.iloc[:, -2:].groupby(by='month').mean()
                if compute_anomaly: std.prediction -= std.prediction.mean()
                data_plot['Standard WGHM'] = {'data': std.prediction.values,
                                              'linestyle': linestyle_stdmodel,
                                              'color': color_stdpmodel}
        # end [step]

        # [step] create canvas
        fig = plt.figure(figsize=figsize)
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9,
                            wspace=None, hspace=None)
        # end [step]

        # [step] add plot and set visibility of spines
        ax = fig.add_subplot(1, 1, 1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)
        # end [step]

        # [step] plot data
        for key, value in data_plot.items():
            ax.plot(x, value['data'], color=value['color'],
                    linestyle=value['linestyle'], label=key)
        # end [step]

        # [step] set axes properties
        if len(ylim) == 2: ax.set_ylim(ylim[0], ylim[1])
        if yticks: ax.yaxis.set_ticks(yticks)
        if yticklabels: ax.yaxis.set_ticklabels(yticklabels)
        ax.yaxis.set_ticks_position('left')
        ax.yaxis.set_tick_params(direction='out', which='both', labelsize=15)
        ax.set_ylabel(ylabel, fontsize=20, labelpad=15)
        ax.yaxis.grid(which='major', linestyle='--', color='silver', zorder=-1)

        if len(xlim) == 2: ax.set_xlim(xlim[0], xlim[1])
        if xticks: ax.xaxis.set_ticks(xticks)
        if xticklabels: ax.xaxis.set_ticklabels(xticklabels)
        if xlabel: ax.set_xlabel(xlabel, fontsize=20, labelpad=15)

        ax.xaxis.set_tick_params(direction='out', which='both', labelsize=15)
        if rotate_xticklabel: ax.xaxis.set_tick_params(rotation=90)
        # end [step]

        # [step] add legend
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), frameon=False,
                  fontsize=15)
        # end [step]

        # [step] set plot title
        ax.set_title(title, fontsize=20, fontweight='bold')
        # end [step]

        # [step] apply tight layout
        if apply_tightlayout: fig.tight_layout()
        # end [step]

        # [step] save figure into image file
        if filename_out: fig.savefig(filename_out, dpi=600)
        # end [step]

        return fig

    @staticmethod
    def random_realization_of_observation(
            obs:np.ndarray,
            observation_error,
            no_of_realization=1000,
            non_stationary_error=True
    ):
        # [step] check inputs
        if obs.shape[0] == 0: return np.empty(0)
        if no_of_realization <= 1: return np.empty(0)

        if (type(observation_error) is np.ndarray or type(observation_error) is list):
            if len(observation_error) > 1 and len(observation_error) != len(obs):
                return np.empty(0)
            observation_error = np.ndarray(observation_error)
        # end [step]

        # [step] generate array of random error
        if non_stationary_error:
            errors = np.random.rand(no_of_realization, obs.shape[0])
        else: errors = np.random.rand(no_of_realization, 1)
        errors = errors * observation_error

        # choose signs randomly
        ii = np.random.randint(2, size=errors.size, dtype=bool).reshape(errors.shape)
        errors[ii] = errors[ii] * -1

        # percentage error = |observation - actual value|/actual value
        # thus, actual value = observation / (1 plus_or_minus percentage error)
        obs = obs / (1 + errors)
        # end [step]

        return obs

    @staticmethod
    def plot_objectives_with_random_observation_realizations(
            solution_ids,
            prediction_dumpfile_var1,
            prediction_dumpfile_var2,
            observation_filename_var1,
            observation_filename_var2,
            observation_error_var1,
            observation_error_var2,
            objective_function,
            number_of_random_realization=1000,
            non_stationary_error=True,
            compute_anomaly_var1=False,
            compute_anomaly_var2=False,
            figsize = (6, 6),
            xlim=(), xticks=(), xticklabels=(), xlabel='',
            ylim=(), yticks=(), yticklabels=(), ylabel='',
            marker='+', markersize=7, markercolor='silver',
            show_grid_xaxis=False, show_grid_yaxis=False,
            apply_tight_layout=False,
            filename_out = ''
    ):
        __self = BorgSolutionEvaluation
        fun = objective_function

        # inner function
        def generate_year_month_pair(start_year, end_year):
            years = np.repeat(np.arange(start_year, end_year + 1),
                              12).reshape(-1, 1)
            months = np.repeat(np.arange(1, 12 + 1)[np.newaxis, :],
                               (end_year-start_year+1), axis=0).reshape(-1,1)

            yrmon = pd.DataFrame(data=np.concatenate((years, months), axis=1),
                                 columns=['year', 'month'])
            return yrmon
        # end of inner function

        # inner function
        def find_start_and_end_year(data_sim):
            yrs = np.unique(data_sim[:, 2]).astype(int)
            return yrs.min(), yrs.max()
        # end of inner function

        # inner function
        def compute_objectives(sid):
            s1 = __self.prediction_time_series(data_sim_var1, sid)
            s1 = s1.merge(right=yrmon_var1, how='inner', on=['year', 'month'])

            s1 = s1.prediction.values
            if compute_anomaly_var1: s1 = s1 - s1.mean()

            x1 = np.array([fun(s1, o) for o in obs_with_error_var1])
            x2 = fun(s1, obs_var1.observation.values)

            s2 = __self.prediction_time_series(data_sim_var2, sid)
            s2 = s2.merge(right=yrmon_var2, how='inner', on=['year', 'month'])

            s2 = s2.prediction.values
            if compute_anomaly_var2: s2 = s2 - s2.mean()

            y1 = np.array([fun(s2, o) for o in obs_with_error_var2])
            y2 = fun(s2, obs_var2.observation.values)

            return x1, y1, x2, y2
        # end of inner function

        # inner function
        def get_boundary_box(x1, y1, x2, y2):
            left = min(x1.min(), x2)
            bottom = min(y1.min(), y2)

            width = max(x1.max(), x2) - left
            height = max(y1.max(), y2) - bottom

            return left, bottom, width, height
        # end of inner function

        # [step] check inputs
        if len(solution_ids) == 0: return None

        if not (os.path.exists(prediction_dumpfile_var1) and
                os.path.exists(prediction_dumpfile_var2) and
                os.path.exists(observation_filename_var1) and
                os.path.exists(observation_filename_var2)
        ): return None

        if (type(observation_error_var1) is np.ndarray or
            type(observation_error_var1) is list
        ) and len(observation_error_var1) == 0: return None

        if (type(observation_error_var2) is np.ndarray or
            type(observation_error_var2) is list
        ) and len(observation_error_var2) == 0: return None
        # end [step]

        # [step] read prediction and observation files
        data_sim_var1 = wio.read_unf(prediction_dumpfile_var1)
        data_sim_var2 = wio.read_unf(prediction_dumpfile_var2)

        obs_var1 = __self.observation_time_series(observation_filename_var1)
        obs_var2 = __self.observation_time_series(observation_filename_var2)

        start_year, end_year = find_start_and_end_year(data_sim_var1)
        yrmon = generate_year_month_pair(start_year, end_year)
        obs_var1 = obs_var1.merge(right=yrmon, how='inner', on=['year', 'month'])

        start_year, end_year = find_start_and_end_year(data_sim_var2)
        yrmon = generate_year_month_pair(start_year, end_year)
        obs_var2 = obs_var2.merge(right=yrmon, how='inner', on=['year', 'month'])

        # year-month columns will be used during objective calculation. only
        # simulation values at these months will be considered
        yrmon_var1, yrmon_var2 = obs_var1.iloc[:,:2], obs_var2.iloc[:, :2]

        if (data_sim_var1.shape[0] == 0 or data_sim_var2.shape[0] == 0 or
            obs_var1.shape[0] == 0 or obs_var2.shape[0] == 0
        ): return None
        # end [step]

        # [step] generate random observation realizations
        obs_with_error_var1 = __self.random_realization_of_observation(
            obs=obs_var1.observation.values,
            observation_error=observation_error_var1,
            no_of_realization=number_of_random_realization,
            non_stationary_error=non_stationary_error
        )

        obs_with_error_var2 = __self.random_realization_of_observation(
            obs=obs_var2.observation.values,
            observation_error=observation_error_var2,
            no_of_realization=number_of_random_realization,
            non_stationary_error=non_stationary_error
        )
        # end [step]

        # [step] compute anomalies of observations
        if compute_anomaly_var1:
            obs_var1.observation -= obs_var1.observation.mean()
            obs_with_error_var1 -= obs_with_error_var1.mean(axis=1).reshape(-1, 1)

        if compute_anomaly_var2:
            obs_var2.observation -= obs_var2.observation.mean()
            obs_with_error_var2 -= obs_with_error_var2.mean(axis=1).reshape(-1, 1)
        # end [step]

        # [step] create canvas
        fig = plt.figure(figsize=figsize)
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9,
                            wspace=None, hspace=None)
        # end [step]

        # [step] add plot and set visibility of spines
        ax = fig.add_subplot(1, 1, 1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)
        # end [step]

        # [step] process and plot data
        for sid in solution_ids:
            x1, y1, x2, y2 = compute_objectives(sid)
            ax.plot(x1, y1, linewidth=0, marker=marker, markersize=markersize,
                    color=markercolor, zorder=-1,
                    label='Objective with perturbed observation')

            ax.plot(x2, y2, linewidth=0, marker=marker, markersize=markersize,
                    markeredgewidth=1.5,
                    color='black', zorder=0,
                    label='Objective value at PF')

            left, bottom, width, height = get_boundary_box(x1, y1, x2, y2)
            rect = patches.Rectangle((left, bottom), width, height,
                                     edgecolor='grey', facecolor='none',
                                     linewidth = 1.5, zorder = 1,
                                     label='Uncertainty bound of a solution')
            ax.add_patch(rect)
        # end [step]

        # [step] set axes properties
        if len(ylim) == 2: ax.set_ylim(ylim[0], ylim[1])
        if yticks: ax.yaxis.set_ticks(yticks)
        if yticklabels: ax.yaxis.set_ticklabels(yticklabels)
        ax.yaxis.set_ticks_position('left')
        ax.yaxis.set_tick_params(direction='out', which='both', labelsize=15)
        ax.set_ylabel(ylabel, fontsize=20, labelpad=15)

        if len(xlim) == 2: ax.set_xlim(xlim[0], xlim[1])
        if xticks: ax.xaxis.set_ticks(xticks)
        if xticklabels: ax.xaxis.set_ticklabels(xticklabels)
        if xlabel: ax.set_xlabel(xlabel, fontsize=20, labelpad=15)
        ax.xaxis.set_tick_params(direction='out', which='both', labelsize=15)

        if show_grid_yaxis:
            ax.yaxis.grid(which='major', linestyle='--', color='silver',
                          zorder=-1)
        if show_grid_xaxis:
            ax.xaxis.grid(which='major', linestyle='--', color='silver',
                          zorder=-1)
        # end [step]

        # [step] add legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), frameon=False,
                  fontsize=15)
        # end [step]

        # [step] apply tight layout
        if apply_tight_layout: fig.tight_layout()
        # end [step]

        if filename_out: fig.savefig(filename_out, dpi=600)
        return fig
