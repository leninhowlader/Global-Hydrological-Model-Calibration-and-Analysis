import os, sys, numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from plots.plot import Plot

class ParetoFrontPlot(Plot):
    @staticmethod
    def draw_paretofront_4d(
            fx,
            figsize=(7, 6),
            add_2d_projection=True,
            lim_visible=0.5,
            behavioral_lim=0.7,
            axis_labels=[],
            title='', pad_title=-2000,
            axis_labelfontsize=18,
            axis_labelpad=16,
            azimuth=30,
            elevation=25,
            filename_out= '',
            show_utopia=False,
            show_compromise_solution=True,
            color_compromise_solution='red',
            color_behavioral_solution='black',
            ax=None,
            xlim=(), ylim=(), zlim=(),
            grid_dist=(0.2, 0.2, 0.2),
            adj_top=0.9, adj_bottom=0.1, adj_left=0.05, adj_right=0.97,
            adj_hspace=0.2, adj_wspace=0.2
            
        ):
        # inner function
        def index_compromise_solution(fx:np.ndarray):
            return np.argmin(np.sum((1-fx)**2, axis=1))
        # end of inner function


        # [step] input validation
        if fx.shape[0] == 0 or fx.shape[1] != 4: return None
        if axis_labels and len(axis_labels) != fx.shape[1]: return None
        if not axis_labels:
            axis_labels += [r'$f_1$', r'$f_2$', r'$f_3$', r'$f_4$']
        # end [step]


        # [step] screen solutions
        # screen out solutions outside visible limit
        ii = np.where((fx > lim_visible).all(axis=1))
        fx = fx[ii]
        # end [step]

        # [step] create plot
        if not ax:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111, projection='3d')
        else: fig = ax.figure
        
        fig.subplots_adjust(left=adj_left, bottom=adj_bottom, right=adj_right, 
                            top=adj_top, wspace=adj_wspace, hspace=adj_hspace)
        fig.set_facecolor('white')
        if title: 
            ax.set_title(title, fontsize=22, pad=pad_title)
            #plt.suptitle(title, fontsize=22, style='italic')
        # end [step]
        
        
        ## get axes limits
        lo, hi = lim_visible - 0.1, 1.05
        if not xlim: xlim = [lo, hi]
        if not ylim: ylim = [lo, hi]
        if not zlim: zlim = [lo, hi]
        ## [end]
        
        
        
        # [step] draw point on the plot
        # split data into four dimensions
        x = fx[:, 0]
        y = fx[:, 1]
        z = fx[:, 2]
        c = fx[:, 3]  # the fourth dimension will be shown as color map

        # plot the scatter diagram
        p = ax.scatter(x, y, z, c=c, cmap=plt.get_cmap('winter_r'),
                       edgecolors='face', s=30, alpha=.8, zorder=4,
                       vmin=lim_visible, vmax=1.0)

        if add_2d_projection:
            color, markersize = 'grey', 7
            ax.plot(x, z, '+', zdir='y', zs=ylim[0], color=color, markersize=markersize,
                    linewidth=1.3)
            ax.plot(y, z, '+', zdir='x', zs=xlim[0], color=color, markersize=markersize,
                    linewidth=1.3)
            ax.plot(x, y, '+', zdir='z', zs=zlim[0], color=color, markersize=markersize,
                    linewidth=1.3)

            if show_utopia:
                utopia = np.array([1.0])
                color, markersize = 'red', 7
                ax.plot(utopia, utopia, '+', zdir='y', zs=ylim[0], color=color,
                        markersize=markersize, markeredgewidth=2)
                ax.plot(utopia, utopia, '+', zdir='x', zs=xlim[0], color=color,
                        markersize=markersize, markeredgewidth=2)
                ax.plot(utopia, utopia, '+', zdir='z', zs=zlim[0], color=color,
                        markersize=markersize, markeredgewidth=2)
        # end [step]

        # [step] set axes, axis ticks, axis labels
        lim_lo, lim_hi = lim_visible - 0.1, 1.05
        
#        if xlim: ax.set_xlim(xlim[0], xlim[1])
#        else: ax.set_xlim([lim_lo, lim_hi])
#        
#        if ylim: ax.set_ylim(ylim[0], ylim[1])
#        else: ax.set_ylim([lim_lo, lim_hi])
#        
#        if zlim: ax.set_zlim(zlim[0], zlim[1])
#        else: ax.set_zlim([lim_lo, lim_hi])

        # set axes ticks
        ax.xaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, grid_dist[0]))
        ax.yaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, grid_dist[1]))
        ax.zaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, grid_dist[2]))

        ax.tick_params(axis='both', which='major', labelsize=13)

        # add axes labels
        ax.set_xlabel(axis_labels[0], fontsize=axis_labelfontsize)
        ax.set_ylabel(axis_labels[1], fontsize=axis_labelfontsize)
        ax.set_zlabel(axis_labels[2], fontsize=axis_labelfontsize)

        ax.xaxis.labelpad = axis_labelpad
        ax.yaxis.labelpad = axis_labelpad
        ax.zaxis.labelpad = axis_labelpad
        # end [step]

        # [step] include 4th objective: draw the colour bar
#        from mpl_toolkits.axes_grid1 import make_axes_locatable
#        divider = make_axes_locatable(ax)
#        cax = divider.append_axes('right', size='5%', pad=0.01)
#

        cbar = plt.colorbar(p, ticks=np.arange(lim_lo, 1.01, 0.1), pad=0.08,
                            fraction=0.02, aspect=30)
        cbar.ax.tick_params(labelsize=12)
        cbar.outline.set_linewidth(0.6)
        cbar.ax.get_yaxis().labelpad = 5
        cbar.ax.get_yaxis().set_ticks_position('left')

        cbar.ax.set_ylabel(axis_labels[3], rotation=90,
                           fontsize=axis_labelfontsize, labelpad=5)

        # add the optimal (utopia) point and the chosen best point
        if show_utopia:
            ax.scatter(1, 1, 1, marker='o', edgecolor='face', c='r', zorder=-1,
                       s=40)
        # end [step]

        # [step] mark behavioral solutions
        color_behvsol = color_behavioral_solution
        ii = np.where((fx >= behavioral_lim).all(axis=1))
        x, y, z = fx[ii][:,0], fx[ii][:,1], fx[ii][:,2]

        ax.scatter(x, y, z, marker='o', edgecolor=color_behvsol, color=(0, 0, 0, 0), s=60,
                   zorder=-1, linewidths=1.1)

        if add_2d_projection:
            markersize = 4
            ax.plot(x, z, '+', zdir='y', zs=ylim[0], color=color_behvsol, markersize=markersize,
                    linewidth=1.3)  # color='blueviolet'
            ax.plot(y, z, '+', zdir='x', zs=xlim[0], color=color_behvsol, markersize=markersize,
                    linewidth=1.3)  # color='peru'
            ax.plot(x, y, '+', zdir='z', zs=zlim[0], color=color_behvsol, markersize=markersize,
                    linewidth=1.3)  # color='magenta')
        # end [step]

        # step: add compromise solution
        if show_compromise_solution:
            color_compsol = color_compromise_solution
            i_compromise = index_compromise_solution(fx)
            x, y, z = fx[i_compromise, (0,1,2)]

            # ax.scatter([x], [y], [z], marker='*', edgecolor='red', zorder=20,
            #            color=(0, 0, 0, 0), alpha=1.0, s=60, linewidths=1.2)
            ax.plot([x], [y], [z], marker='*', zorder=5, markeredgecolor='none', #color='red',
                       color='red', alpha=1.0, markersize=10, markeredgewidth=1.5)

            if add_2d_projection:
                markersize = 11
                x, y, z = fx[i_compromise, (0,1,2)]
                ax.plot([x], [z], '+', zdir='y', zs=ylim[0], color=color_compsol,
                        markersize=markersize, markeredgewidth=1.8)
                ax.plot([y], [z], '+', zdir='x', zs=xlim[0], color=color_compsol,
                        markersize=markersize, markeredgewidth=1.8)
                ax.plot([x], [y], '+', zdir='z', zs=zlim[0], color=color_compsol,
                        markersize=markersize, markeredgewidth=1.8)
            # end [step]
        
        ax.set_xlim(xlim[0], xlim[1])
        ax.set_ylim(ylim[0], ylim[1])
        ax.set_zlim(zlim[0], zlim[1])
        
        # [step] adjust viewing angle
        ax.view_init(elev=elevation, azim=azimuth)
        # end [step]

        # [step] save figure into imagefile
        if filename_out: fig.savefig(filename_out, dpi=600)
        # end [step]

        return fig

    @staticmethod
    def draw_paretofront_3d(fx,
                            figsize=(7, 6),
                            add_2d_projection=True,
                            lim_visible=0.5,
                            lim_compromise=0.7,
                            axis_labels=[],
                            title='',
                            axis_labelfontsize=18,
                            axis_labelpad=16,
                            azimuth=30,
                            elevation=25,
                            filename_out='',
                            color='red'
    ):

        # [step] input validation
        if fx.shape[0] == 0 or fx.shape[1] != 3: return None
        if axis_labels and len(axis_labels) != fx.shape[1]: return None
        if not axis_labels:
            axis_labels += [r'$f_1$', r'$f_2$', r'$f_3$']
        # end [step]

        # [step] screen solutions
        # screen out solutions outside visible limit
        ii = np.where((fx > lim_visible).all(axis=1))
        fx = fx[ii]
        # end [step]

        # [step] create plot
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=.95,
                            wspace=None, hspace=None)
        fig.set_facecolor('white')
        if title: plt.suptitle(title, fontsize=22, style='italic')
        # end [step]

        # [step] draw point on the plot
        x = fx[:, 0]
        y = fx[:, 1]
        z = fx[:, 2]
        # plot the scatter diagram
        p = ax.scatter(x, y, z, color=color, edgecolors='face', s=20,
                       vmin=0.6, vmax=1.0, zorder=1, alpha=0.8)

        # add the optimal (utopia) point and the chosen best point
        ax.scatter(1, 1, 1, marker='o', edgecolor='face', c='r', zorder=-1,
                   s=40)

        if add_2d_projection:
            zs = lim_visible - 0.1
            color, markersize = 'grey', 7
            ax.plot(x, z, '+', zdir='y', zs=zs, color=color,
                    markersize=markersize,
                    linewidth=1.3)
            ax.plot(y, z, '+', zdir='x', zs=zs, color=color,
                    markersize=markersize,
                    linewidth=1.3)
            ax.plot(x, y, '+', zdir='z', zs=zs, color=color,
                    markersize=markersize,
                    linewidth=1.3)

            utopia = np.array([1.0])
            color, markersize = 'red', 7
            ax.plot(utopia, utopia, '+', zdir='y', zs=zs, color=color,
                    markersize=markersize, markeredgewidth=2)
            ax.plot(utopia, utopia, '+', zdir='x', zs=zs, color=color,
                    markersize=markersize, markeredgewidth=2)
            ax.plot(utopia, utopia, '+', zdir='z', zs=zs, color=color,
                    markersize=markersize, markeredgewidth=2)
        # end [step]

        # [step] set axes, axis ticks, axis labels
        lim_lo, lim_hi = lim_visible - 0.1, 1.05

        ax.set_xlim([lim_lo, lim_hi])
        ax.set_ylim([lim_lo, lim_hi])
        ax.set_zlim([lim_lo, lim_hi])

        # set axes ticks
        ax.xaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, 0.2))
        ax.yaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, 0.2))
        ax.zaxis.set_ticks(np.arange(lim_lo, lim_hi + 0.01, 0.2))

        ax.tick_params(axis='both', which='major', labelsize=13)

        # add axes labels
        ax.set_xlabel(axis_labels[0], fontsize=axis_labelfontsize)
        ax.set_ylabel(axis_labels[1], fontsize=axis_labelfontsize)
        ax.set_zlabel(axis_labels[2], fontsize=axis_labelfontsize)

        ax.xaxis.labelpad = axis_labelpad
        ax.yaxis.labelpad = axis_labelpad
        ax.zaxis.labelpad = axis_labelpad
        # end [step]

        # [step] mark compromised solutions
        ii = np.where((fx >= lim_compromise).all(axis=1))
        x, y, z = fx[ii][:, 0], fx[ii][:, 1], fx[ii][:, 2]

        ax.scatter(x, y, z, marker='o',
                   facecolors=(0,0,0,0), edgecolor='black', s=30,
                   linewidths=1.5, zorder=0)

        if add_2d_projection:
            zs = lim_visible - 0.1
            color, markersize = 'black', 4
            ax.plot(x, z, '+', zdir='y', zs=zs, color=color,
                    markersize=markersize,
                    linewidth=1.3)  # color='blueviolet'
            ax.plot(y, z, '+', zdir='x', zs=zs, color=color,
                    markersize=markersize,
                    linewidth=1.3)  # color='peru'
            ax.plot(x, y, '+', zdir='z', zs=zs, color=color,
                    markersize=markersize,
                    linewidth=1.3)  # color='magenta')
        # end [step]

        # [step] adjust viewing angle
        ax.view_init(elev=elevation, azim=azimuth)
        # end [step]

        # [step] save figure into imagefile
        if filename_out: fig.savefig(filename_out, dpi=600)
        # end [step]

        return fig