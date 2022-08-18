
from sqlite3 import paramstyle
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
from collections import OrderedDict

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

    @staticmethod
    def pcplot(
        param_values:np.ndarray,
        paramset_lebel:str,
        param_order:tuple=(),
        color:str='lightgrey',
        markeredgecolor:str='grey',
        linewidth:float=1.2,
        linestyle:tuple=(1, ()),
        zorder:int=-1,

        drow_axes_and_grid:bool=False,
        param_names:tuple=(),
        lows:tuple=(),
        highs:tuple=(),
        labelsize:float=14,
        xtick_label_rotation:float=0,

        ax:plt.axes=None,
        figsize:tuple=(10, 4),

        show_legend:bool=True,
        legend_handles:tuple=(),
        bbox_to_anchor:list=[1, 0], #[0, -0.35, 1, 0.2],
        legend_loc:str='lower right',
        legend_fontsize:float=14,
        legend_ncol:int=4
    ):
        """
        The function plots Parallel Coordinate Plot.

        Parameters:
        @param param_values: (numpy 2-d array) Parameter values
        @param paramset_lebel: (str) label of the parameter set
        @param param_order: (tuple of intger; optional) order of the parameters 
        @param color: (str) Primary color
        @param markeredgecolor: (str) marker edge 
        @param linewidth: (float) line width
        @param linestyle: (tuple) line style
        @param zorder: (int) (vertical) order art object

        @param drow_axes_and_grid: (bool) flag to represent whether backgroud 
                            axes and grids should be created/plotted
        @param param_names: (tuple of string) parameter names. length should be 
                            consisten with the shape of the parameter values 
        @param lows: (tuple of float) lower bound of the parameters
        @param highs: (tuple of float) upper bound of parameters
        @param labelsize: (float) label size / font size
        @param xtick_label_rotation: (float) rotation of x labels

        @param ax: (matplotlib axes; optional; default None) axes, if provided
                            elements will be ploted on the given axes 
        @param figsize: (tuple) size of the figure. this parameter will only be
                            used if the parameter 'ax' not provided

        @param show_legend: (bool) flag to indicate whether or not the legend to
                            be printed/plotted
        @param legend_handles: (tuple) legen handles or art objects of alread 
                            existed ploting axes
        @param bbox_to_anchor: (list) coordinate of the legend panel 
        @param legend_loc: (str) anchoring location of the legend panel
        @param legend_fontsize: (float) font size of the legend text/elements
        @param legend_ncol: (int) number of columns in legend elements
        @retrun (matplotlib figure) figure
        """

        if ax: fig = ax.get_figure()
        else: 
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(1, 1, 1)

        nparam = param_values.shape[1]

        lows, highs = np.array(lows), np.array(highs)
        if lows.shape[0] == 0: lows = param_values.min(axis=0)
        if highs.shape[0] == 0: highs = param_values.max(axis=0)
        
        if drow_axes_and_grid:
            param_names = (list(param_names) + 
                           ['param%02d'%(x+1) for x in range(nparam)])
            param_names = param_names[:nparam]
            
            ParallelCoordinatePlot.background(
                ax=ax,
                param_names=param_names,
                lows=lows,
                highs=highs,
                labelsize=labelsize,
                xtick_label_rotation=xtick_label_rotation,
                nparam=nparam
            )

        ## step: add solutions to the plot
        handles = list(legend_handles)
        if param_order: order = np.array(param_order, dtype=int)
        else: order = np.arange(nparam, dtype=int)
        
        x = np.arange(nparam) + 1
        
        pp = param_values[:, order]
        
        y = (pp - lows) / (highs - lows)
        h0 = ax.plot(x, y.T, color=color, marker='o', linestyle=linestyle,
                    fillstyle='full', markeredgecolor=markeredgecolor, 
                    markersize=10, linewidth=linewidth, label=paramset_lebel,
                    zorder=zorder)
        
        handles.append(h0[0])
        ## end [step]


        if show_legend:
            # handles, labels = ax.get_legend_handles_labels()
            # by_label = OrderedDict(zip(labels, handles))
            
            # handles = by_label.values()
            # labels = by_label.keys()

            labels = []
            for h in handles: labels.append(h.get_label())

            ax.legend(handles, labels, ncol=legend_ncol, frameon=False,
                      columnspacing=1, prop={'size': legend_fontsize},
                      loc=legend_loc, bbox_to_anchor=bbox_to_anchor, 
                      bbox_transform=ax.figure.transFigure)
        
        return ax, tuple(handles)

    @staticmethod
    def background(
        ax,
        param_names,
        lows,
        highs,
        labelsize=12,
        xtick_label_rotation=0,
        nparam=-1
    ):
        """
        The function draws the background axes, grids, x-axis labels.

        Parameters:
        @param ax: (matplotlib axes) axes on which the background be drawn
        @param param_names: (tuple of string) list of parameter names 
        @param lows: (tuple of float) parameter lower bounds
        @param highs: (tuple of float) parameter upper bounds
        @param labelsize: (float; optional; default 12) font size of text elements
        @param xtick_label_rotation: (float) rotation angle of the x-axis labels
        @param nparam: (int) number of parameters. this value should be the
                        maximum no. of parameters that could be addresses in the
                        parallel coordinate plot. Note that the number of 
                        parameters could be different in two calibrations
        """
        
        if nparam <= 0: nparam = len(param_names)
        if nparam == 0: return None
        if not (len(param_names)==len(lows)==len(highs)==nparam): return None
        
        pnames = np.array(param_names)
        lows, highs = np.array(lows), np.array(highs)

        ## [step] draw custom grid in x-axis
        for i in np.arange(nparam)+1:
            ax.plot([i, i], [0, 1], color='silver', zorder=-1)
        ax.set_ylim(-0.22, 1.22)
        
        #ax.spines['top'].set_visible(False)
        #ax.spines['bottom'].set_visible(True)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ## end [step]

        ## step: add parameter bounds
        ax.plot([0.4, nparam + 0.05], [1, 1], color='black', zorder=-1)
        ax.plot([0.4, nparam + 0.05], [0, 0], color='black', zorder=-1)

        x = np.arange(nparam) + 1
        for i in x:
            ax.text(i, -0.07, str(lows[i-1]), ha='center', va='top', 
                    fontsize=labelsize)
            ax.text(i, 1.07, str(highs[i-1]), ha='center', va='bottom', 
                    fontsize=labelsize)
        
        ax.text(0.75, -0.07, 'Min:', ha='right', va='top', 
                fontsize=labelsize)
        ax.text(0.75, 1.07, 'Max:', ha='right', va='bottom', 
                fontsize=labelsize)
        ## end [step]

        
        ## step: set axis limits, tick labels
        ax.set_xlim(0.3, nparam + 0.4)
        x = np.arange(nparam) + 1
        ax.xaxis.set_ticks(x)
        ax.xaxis.set_ticklabels(pnames, rotation=xtick_label_rotation)
        ax.xaxis.set_tick_params(pad=0, labelsize=labelsize, width=0)
        
        ax.yaxis.set_ticks([])
        ## end [step]
