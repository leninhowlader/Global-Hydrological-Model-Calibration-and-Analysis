import os, sys, numpy as np, pandas as pd
from datetime import datetime
from calendar import monthrange
from collections import OrderedDict
from matplotlib import pyplot as plt, patches

from wgap.wgapio import WaterGapIO as wio


class ParetoSolutionEvaluation:
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
        __self = ParetoSolutionEvaluation

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
        storage_sum = np.empty(0)
        for i in range(nvars):
            d = np.empty(0)

            ## read unf file
            f = os.path.join(directory_sim, filenames_storage[i])
            if not os.path.exists(f): return False

            d = wio.read_unf(f)
            if d.shape[0] == 0: return False
            ##

            ## sort indices
            ##ii = np.lexsort((d[:, 2], d[:, 1], d[:, 0]))
            ##d = d[ii]
            ##

            if storage_sum.shape[0] == 0: storage_sum = d
            else:
                if storage_sum.shape != d.shape: return False
                if np.abs(storage_sum[:, :3] - d[:, :3]).sum() != 0: return False
                storage_sum[:, 3:] += d[:, 3:]

        # export storage sum into file
        filename_out = os.path.join(directory_sim, filename_out)

        return wio.write_unf(filename_out, data=storage_sum)

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

        self = ParetoSolutionEvaluation

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
                pred = ParetoSolutionEvaluation.prediction_time_series(sim_data,
                                                                       sid)
                if compute_anomaly:
                    pred.prediction -= pred.prediction.mean()

                s, o = ParetoSolutionEvaluation.couple_prediction_observation(
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

        self = ParetoSolutionEvaluation

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
                pred = ParetoSolutionEvaluation.prediction_time_series(sim_data,
                                                                       sid)
                if compute_anomaly:
                    pred.prediction -= pred.prediction.mean()

                s, o = ParetoSolutionEvaluation.couple_prediction_observation(
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
            observation_errors=np.empty(0),
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
        self = ParetoSolutionEvaluation

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

            if len(observation_errors) == 1:

                error_lb = obs.observation.values * (1 - observation_errors[0])
                error_ub = obs.observation.values * (1 + observation_errors[0])
                data_plot['low_bound'] = {'data': error_lb,
                                          'linestyle': (1, (2, 2)),
                                          'color': 'orange'}
                data_plot['upper_bound'] = {'data': error_ub,
                                          'linestyle': (1, (2, 2)),
                                          'color': 'orange'}

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
    def plot_predictions_with_solutions_modified(
            prediction_dumpfile,
            solution_ids,
            observation_filename='',
            standard_model_dumpfile='',
            compute_anomaly=False,
            solution_fx:np.ndarray=np.empty(0),
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
            rotate_xticklabel=False,
            behavioral_threshold=0.7
    ):
        self = ParetoSolutionEvaluation

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

        # inner function
        def index_compromise_solution(fx):
            return np.argmin(np.sum((1-fx)**2, axis=1))
        # end of inner function

        # inner function
        def index_behavioral_solution(fx, threshold):
            return np.where((fx>=threshold).all(axis=1))[0]
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

        # predictions with all Pareto solutions
        y = extract_predictions_multiple(solution_ids, show_month_averages)
        data_plot['Pareto solutions'] = {'data': y,
                                         'linestyle': linestyle_allsolution,
                                             'color': color_allsolution,
                                             'zorder': 0}


        # predictions of behavioral solutions
        ii = index_behavioral_solution(solution_fx, behavioral_threshold)
        data_plot['Behavioral solutions'] = {'data': y[:,ii].copy(),
                                                    'linestyle': linestyle_topsolution,
                                                    'color': color_topsolution,
                                                    'zorder': 1}
        # predictions of compromise solutions
        i = index_compromise_solution(solution_fx)
        data_plot['Compromise solution'] = {'data': y[:,i].copy(),
                                                    'linestyle': (1, (3,3)),
                                                    'color': 'black',
                                                    'zorder': 2}
        # observations
        if observation_filename:
            obs = pd.DataFrame()
            if obs.shape[0] == 0:
                obs = self.observation_time_series(
                                                observation_filename)
            obs = yrmon.merge(right=obs, how='left', on=['year', 'month'])

            if compute_anomaly: obs.observation -= obs.observation.mean()
            if show_month_averages:
                obs = obs.iloc[:, -2:].groupby(by='month').mean()
            data_plot['Observations'] = {'data': obs.observation.values,
                                         'linestyle': linestyle_observation,
                                         'color': color_observation,
                                         'zorder': 3}

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
                                              'linestyle': (1, ()),
                                              'color': color_stdpmodel,
                                              'zorder': 4}
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
        orders = ['Observations', 'Standard WGHM', 'Compromise solution', 'Behavioral solutions',
                  'Pareto solutions']

        for key in orders:
            value = data_plot[key]
        #for key, value in data_plot.items():
            ax.plot(x, value['data'], color=value['color'],
                    linestyle=value['linestyle'], label=key, zorder=value['zorder'])
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
        ax.legend(by_label.values(), by_label.keys(), frameon=True,
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
        __self = ParetoSolutionEvaluation
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
