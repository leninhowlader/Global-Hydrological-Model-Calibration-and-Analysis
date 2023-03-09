
import sys, os, pandas as pd, numpy as np

from core.configuration import  Configuration
from core.stats import stats
from wgap.watergap import WaterGAP


def load_watergap_simulation(config, watergap_output_directory):
    watergap_output_directory = os.path.join(WaterGAP.home_directory,
                                             watergap_output_directory)
    if not os.path.exists(watergap_output_directory): return False

    succeed = True
    for var in config.sim_variables:
        succeed = var.cell_level_predicted_time_series(
            start_year=WaterGAP.start_year,
            end_year=WaterGAP.end_year,
            prediction_directory=watergap_output_directory
        )

        # compute spatial scale summary
        succeed &= var.aggregate_prediction_at_spatial_scale()

        # compute anomaly
        succeed &= var.do_anomaly_computation()

    return succeed

def load_observations(config):
    succeed = True
    for var in config.obs_variables:
        df = pd.read_csv(var.data_source.filename)
        if df.shape[0] == 0: succeed = False

        data = df.iloc[:,-1].values.reshape(-1, 1)
        indices = df.loc[:, ['year', 'month']].values

        var.data_cloud.data = data
        var.data_cloud.data_indices = indices

    return succeed

def compute_objective(config):
    objectives = []

    for obs_var in config.obs_variables:
        for sim_var in config.sim_variables:
            if obs_var.counter_variable == sim_var.varname:
                fun = obs_var.function

                obs = np.concatenate((obs_var.data_cloud.data_indices,
                                      obs_var.data_cloud.data), axis=1)
                obs = pd.DataFrame(data=obs, columns=['year', 'month', 'obs'])

                sim = np.concatenate((sim_var.data_cloud.data_indices,
                                      sim_var.data_cloud.data), axis=1)
                sim = pd.DataFrame(data=sim,
                                   columns=['year', 'month', 'sim'])

                data = sim.merge(obs, how='inner', on=['year', 'month'])
                sim = data.sim.values.flatten()
                obs = data.obs.values.flatten()

                objectives.append(stats.objective_function(fun, sim, obs))

                break

    return objectives

def main(argv):
    # step: acquire system arguments
    filename_config, watergap_output_directory, filename_output = '', '', ''
    iterid_str = ''

    if (len(argv) < 4):
        message = (('Usages:\n%s <configuration filename> <iteration id> ' +
                   '<output directory> <output file>')
                   % os.path.split(argv[0])[-1])
        print(message)
        exit(-100)
    else:
        filename_config = argv[1]
        iterid_str = argv[2]
        watergap_output_directory = argv[3]

        if len(argv) > 4: filename_output = argv[4]
        if not os.path.exists(filename_config): exit(-101)
    # end of step

    # step: read configuration file
    config = Configuration.read_configuration_file(filename_config)
    if config:
        config.mode = 'calibration'
        if not config.is_okay():
            print('\nConfiguration file could not be read properly.')
            exit(-200)

        if not WaterGAP.is_okay():
            print('WaterGAP options in configuration file not sufficient!')
            exit(-201)
    # end of step

    # step: read simulation and observations
    succeed = load_watergap_simulation(config, watergap_output_directory)
    if not succeed:
        print('WaterGAP simulation could not loaded successfully!')
        exit(-301)

    succeed = load_observations(config)
    if not succeed:
        print('Observations was not successfully loaded')
        exit(-302)
    # end of step

    # step: compute objectives
    objectives = compute_objective(config)
    if len(objectives) == 0 or len(objectives) != len(config.obs_variables):
        print('Objective computation failed')
        exit(-400)
    # end of step

    # step: write on output file
    if filename_output:
        succeed = True
        f = None
        try:
            f = open(filename_output, 'a')
            f.write('%s\n' % ','.join([iterid_str] + [str(x) for x in objectives]))
        except:
            succeed = False
        finally:
            try: f.close()
            except: pass

        if not succeed:
            print('Objectives could not be written on the output file')
            exit(-500)
    # end of step

    return 0

if __name__ == '__main__': main(sys.argv)