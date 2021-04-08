import seaborn as sbn
from matplotlib import pyplot as plt
from collections import OrderedDict

from plots.plot import Plot

class density_plot(Plot):
    __fig__ = None

    def get_figure(self): return self.__fig__

    def __init__(
            self,
            struct_data:OrderedDict,
            figsize=(10,6),
            subplot_ncol=6,
            xlabels=(),
            xlims=(),
            tight_layout=False,
            filename_out='',
            use_xlabel_as_plot_title=True
        ):
        self.__fig__ = None
        proceed = self.__input_credibility__(struct_data, xlabels, xlims, subplot_ncol)

        if proceed:
            ## find number of parameters
            nsubplot = 0
            for key in struct_data.keys():
                nsubplot = struct_data[key]['data'].shape[1]
                break
            ##

            ##
            low_lims, high_lims = [], []
            if xlims:
                low_lims = [x[0] for x in xlims]
                high_lims = [x[1] for x in xlims]
            ##

            ##
            if not xlabels:
                xlabels = self.__get_titles__(nsubplot)
                use_xlabel_as_plot_title = True
            else:
                if use_xlabel_as_plot_title:
                    temp = self.generate_text_numbers(nsubplot)
                    xlabels = ['(%s) %s' %(temp[i], xlabels[i])
                               for i in range(nsubplot)]
            ##

            fig = plt.figure(figsize=figsize)

            t0, t1 = divmod(nsubplot, subplot_ncol)
            subplot_nrow = t0 + (t1 > 0)

            for i in range(nsubplot):
                ax = fig.add_subplot(subplot_nrow, subplot_ncol, i + 1)

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(True)
                ax.spines['left'].set_visible(True)

                for key, item in struct_data.items():
                    data, args = item['data'], item['args']

                    x = data[:, i]
                    sbn.kdeplot(x, bw=0.4, shade=False, ax=ax, lw=1.2,
                                legend=False, **args)

                if xlims:
                    low, high = low_lims[i], high_lims[i]
                    ax.xaxis.set_ticks([low, high])
                    ax.xaxis.set_ticklabels([str(low), str(high)])

                if use_xlabel_as_plot_title: ax.set_title(xlabels[i])
                else: ax.set_xlable(xlabels[i])

            if tight_layout: fig.tight_layout()
            if filename_out: fig.savefig(filename_out, dpi=600)

            self.__fig__ = fig


    def __get_titles__(self, nsubplot): return Plot.generate_text_numbers(nsubplot)

    def __input_credibility__(self, data:dict, xlabels, xlims, subplot_ncol):
        ncol = 0
        for key, value in data.items():
            if ncol == 0: ncol = data[key]['data'].shape[1]
            else:
                if data[key]['data'].shape[1] != ncol: return False
        if ncol == 0: return False

        if xlabels:
            if len(xlabels) != ncol: return False

        if xlims:
            if len(xlims) != ncol: return False

        if subplot_ncol <= 0: return False

        return True

