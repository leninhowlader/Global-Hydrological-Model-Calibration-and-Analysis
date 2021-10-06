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
    def index_of_compromise_solution(objs:np.ndarray, wts=[], utopia=[]):
        wts, utopia = np.array(wts).flatten(), np.array(utopia)
        if utopia.size == 0: utopia = np.ones((1, objs.shape[1]))

        if wts.size > 0:
            if wts.size != objs.shape[1]:
                wts = wts.repeat(np.ceil(objs.shape[1]/wts.size))[:objs.shape[1]]
            objs = objs * wts

        return np.argmin(np.sum((utopia - objs) ** 2, axis=1))

    @staticmethod
    def index_of_behavioural_solutions(objs:np.ndarray, thresholds:np.ndarray):

        if not type(thresholds) in [np.ndarray or list]:
            thresholds = np.array([thresholds] * objs.shape[1])

        if thresholds.size != objs.shape[1]:
            thresholds = \
            thresholds.repeat(np.ceil(objs.shape[1] / thresholds.size)
                              )[:objs.shape[1]]

        cond = np.ones(objs.shape[0], dtype=bool)
        for i in range(objs.shape[1]):
            cond = (cond & (objs[:, i] >= thresholds[i]))

        return np.where(cond==True)[0]

    @staticmethod
    def find_nan_objectives(objs, nanvalue=np.float64('1.79769e+308')):
        return np.where((objs==nanvalue).any(axis=1))[0]

class RuntimeDynamicReport:
    def __init__(self):
        self.problemid = -1
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

    def is_okay(self):
        if (self.problemid < 0 or self.nfe < 0 or self.archive_size <= 0 or
            len(self.solutions) != self.archive_size): return False
        return True

    @staticmethod
    def read_runtime_dynamic_file(filename):
        
        reports = []

        if True:
        #try:
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
            
            rpt = None
            
            for line in lines:
                if not rpt: rpt = RuntimeDynamicReport()
                else:
                    if rpt.is_okay():
                        reports.append(rpt)
                        rpt = None
                        continue

                if line.find('Problem no') > 0:
                    try: x = int(line.split('=')[1])
                    except: x = -1

                    rpt.problemid = x

                elif line.find('NFE') > 0:
                    #if rpt: reports.append(rpt)
                    #rpt = RuntimeDynamicReport()
                    
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
        #except: pass
        
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
            nfes=(1000, 5000, 10000, 20000),
            linestyle=(0, ()),
            marker='*',
            markersize=7,
            do_color_plot=True,
            axis_labels=(), fontsize_label=14,
            title='', fontsize_title=15, pad_title=20,
            xlim=(), ylim=(),
            ticksize=13,
            pad_axislabel=5
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

        #nfes.sort()
        if len(nfes) > max_pf_count: nfes = nfes[-max_pf_count:]

        pf_count = len(nfes)
        if pf_count < 4: pf_styles = pf_styles[-pf_count:]

        pf_lines_2D = []
        for i in range(pf_count):
            x, y = extract_xy(nfes[i])

            zorder = pf_count - 1 - i
            label = '%d Model runs' % nfes[i]

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
            ax.set_xlabel(axis_labels[0], fontsize=fontsize_label,
                          labelpad=pad_axislabel)
            ax.xaxis.set_label_position('top')

            ax.set_ylabel(axis_labels[1], fontsize=fontsize_label,
                          labelpad=pad_axislabel)
            ax.yaxis.set_label_position('right')

        if title: ax.set_title(title, fontsize=fontsize_title, pad=pad_title)
        if xlim:
            xticks = np.arange(xlim[0], xlim[1] + 0.01, 0.05)
            ax.xaxis.set_ticks(xticks)
            ax.set_xlim(xlim)
        if ylim:
            yticks = np.arange(ylim[0], ylim[1] + 0.01, 0.05)
            ax.yaxis.set_ticks(yticks)
            ax.set_ylim(ylim)

        ax.tick_params('both', labelsize=ticksize)

        return pf_lines_2D

    @staticmethod
    def paretofront_at_different_nfe_of_two_objective_calibrations(
            report_filename:str,
            axis_labels:list,
            figsize=(12, 7),
            filename_out='',
            marker='*',
            markersize=6,
            use_color=True,
            show_legend=True,
            title='',
            xlim=(),
            ylim=(),
            fontsize_title=15, pad_title=20,
            ticksize=13,
            fontsize_label=14, fontsize_legend=12,
            tight_layout=False,
            adjust_left=0.03, adjust_right=0.90, adjust_bottom=0.1, adjust_top=0.80,
            adjust_hspace=0, adjust_wspace=0.30,
            legend_ncol=4,
            bbox_to_anchor=(0, 0., 0.5, 0.5),
            legend_loc='lower right',
            ax=None,
            columnspacing=1
    ):
        if not ax:
            fig = plt.figure(figsize=figsize)

            ax = fig.add_subplot(1, 1, 1)

            fig.subplots_adjust(
                left=adjust_left, right=adjust_right, bottom=adjust_bottom,
                top=adjust_top, hspace=adjust_hspace, wspace=adjust_wspace
            )
        else: fig = ax.get_figure()

        RuntimeDynamicReport.draw_paretofront_at_different_nfe_2D(
            ax,
            report_filename,
            axis_labels=axis_labels,
            fontsize_label=fontsize_label,
            do_color_plot=use_color,
            marker=marker,
            markersize=markersize,
            title=title,
            fontsize_title=fontsize_title,
            pad_title=pad_title,
            xlim=xlim, ylim=ylim,
            ticksize=ticksize
        )

        if show_legend:
            ax.legend(
                frameon=False, fontsize=fontsize_legend,
                ncol=legend_ncol, loc=legend_loc,
                bbox_to_anchor=bbox_to_anchor, columnspacing=columnspacing
            )

        if tight_layout: fig.tight_layout()

        if filename_out: fig.savefig(filename_out, dpi=600)

        return True

    @staticmethod
    def paretofront_improvement_over_nfe(
            runtime_report_files:list,
            experiment_nobjs:list,
            objective_conversion_factor:float=-1.0,
            report_average_objective:bool=True,
            report_minimum_euclidian_distance:bool=False,
            report_average_euclidian_distance:bool=False,

            top_solutions=0,
            minimum_nsol_to_consider_Qtop50:int=51,

            # figure and axes arguments
            ax=None,
            figsize:tuple=(7, 5),
            left=0.15, right=9.0, bottom=0.1, top=9.0, hspace=0, wspace=0,
            tight_layout:bool=False,
            filename_out:str='',

            title:str='', title_fontsize=18, pad_title=10,
            series_labels:tuple= (),
            series_linestyles:tuple=(),
            series_linewidths:tuple=(),
            series_colors:tuple=(),
            marker='o', markersize=3,
            show_grid_xaxis:bool=False, show_grid_yaxis:bool=False,

            xticks=(), yticks=(),
            xlim=(0.5, 20.0), ylim=(0.5, 1.0),
            ylabel='',
            ticks_labelsize=14,
            axislabel_fontsize=14,
            pad_axislabel=5,

            show_legend=True,
            bbox_to_anchor=(0.5, 0., 0.5, 0.5),
            legend_fontsize=12,
            legend_ncol=5,
            legend_loc='lower right',
            columnspacing=1.0
    ):
        self = RuntimeDynamicReport

        # inner function
        def summary(objs:np.ndarray):
            nsol = objs.shape[0]

            ed = np.sqrt(np.power(1-objs, 2).sum(axis=1))
            if report_minimum_euclidian_distance: return ed.min()

            if top_solutions > 0:
                ii = np.argsort(ed)[:10]
            elif nsol >= minimum_nsol_to_consider_Qtop50:
                Qtop50 = np.quantile(ed, 0.5)
                ii = np.where(ed <= Qtop50)[0]
            else: ii = np.arange(nsol, dtype=int)

            if report_average_euclidian_distance: return ed[ii].mean()
            if report_average_objective: return objs[ii].mean()

            return None
        # end of inner function

        # inner function
        def extract_xy(reports, nobjs, cf):
            xvalues, yvalues = [], []

            for report in reports:
                xvalues.append(report.nfe)

                o = np.array(report.solutions)[:,-nobjs:] * cf
                yvalues.append(summary(o))

            xvalues, yvalues = np.array(xvalues), np.array(yvalues)
            ii = np.argsort(xvalues)

            return xvalues[ii], yvalues[ii]
        # end of inner function

        # inner function

        # end of inner function

        ## step: validate input arguments
        ncal = len(runtime_report_files)

        if ncal == 0: return None
        if len(experiment_nobjs) != ncal: return None
        if not (report_minimum_euclidian_distance
                or report_average_euclidian_distance
                or report_average_objective): return None

        if series_linestyles and len(series_linestyles) < ncal: return None
        if series_colors and len(series_colors) < ncal: return None

        if (type(objective_conversion_factor) is list and
            len(objective_conversion_factor) == ncal):
            conversion_factors = objective_conversion_factor
        else:  conversion_factors = [objective_conversion_factor] * ncal

        if len(series_labels) != ncal:
            series_labels = ['Experiment %d'%(x+1) for x in range(ncal)]

        if not series_colors: series_colors = ['black'] * ncal
        if not series_linestyles: series_linestyles = [(1, ())] * ncal
        if len(series_linewidths) < ncal: series_linewidths = [1.0] * ncal
        ## end [step]

        ## step: create canvas
        if ax == None:
            fig = plt.figure(figsize=figsize)
            fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top,
                                wspace=wspace, hspace=hspace)
            ax = fig.add_subplot(1, 1, 1)

            #tight_layout = False
            filename_out = ''
        else: pass#; fig = ax.get_figure()
        ## end [step]

        ## step: set visibility of spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)
        ## end [step]

        for i in range(ncal):
            reports = self.read_runtime_dynamic_file(runtime_report_files[i])
            if len(reports) == 0: return False

            nobj = experiment_nobjs[i]
            cf = conversion_factors[i]

            x, y = extract_xy(reports, nobj, cf)
            x = x/1000

            ax.plot(x, y, color=series_colors[i], linestyle=series_linestyles[i],
                        marker=marker, markersize=markersize,
                        linewidth=series_linewidths[i],
                        label=series_labels[i])

        # [step] manipulate axis properties
        ax.set_xlabel('NFE (in Thousands)', fontsize=axislabel_fontsize,
                      labelpad=pad_axislabel)

        if xticks: ax.xaxis.set_ticks(xticks)
        else: ax.xaxis.set_ticks([0.5] + np.arange(5, 21, 5, dtype=int).tolist())

        if xlim: ax.set_xlim(xlim)
        ax.xaxis.set_tick_params(direction='out', which='both', 
                                 labelsize=ticks_labelsize)

        if ylim: ax.set_ylim(ylim)
        # ylabel = 'Mean objective (NSE)'
        # if report_average_euclidian_distance: ylabel = 'Mean ED'
        # if report_minimum_euclidian_distance: ylabel = 'Minimum ED'
        if ylabel: 
            ax.set_ylabel(ylabel, fontsize=axislabel_fontsize, 
                          labelpad=pad_axislabel)

        if yticks: ax.yaxis.set_ticks(yticks)

        ax.yaxis.set_ticks_position('left')
        ax.yaxis.set_tick_params(direction='out', which='both', 
                                 labelsize=ticks_labelsize)
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
        if title: ax.set_title(title, fontsize=title_fontsize, pad=pad_title)
        # end [step]

        # [step] add legend
        if show_legend:
            handles, labels = ax.get_legend_handles_labels()
            by_label = OrderedDict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), frameon=False,
                      loc=legend_loc, bbox_to_anchor=bbox_to_anchor,
                      fontsize=legend_fontsize, ncol=legend_ncol,
                      columnspacing=columnspacing)
            # end [step]

        # [step] apply tight layout
        if tight_layout: fig.tight_layout()
        # end [step]

        if filename_out: fig.savefig(filename_out, dpi=600)

        return True

