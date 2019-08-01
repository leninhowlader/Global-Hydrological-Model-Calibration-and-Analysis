import sys
sys.path.append('..')
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP

config_filename = 'input/configuration_GAN.txt'
output_directory = '/media/sf_private/FINAL_CALIBRATION/predictions/G6C04/'


def main():
    global  config_filename, output_directory

    succeed = False; config = None; vars = None

    if config_filename:
        print('reading configuration file ..', end='', flush=True)
        config = Configuration.read_configuration_file(config_filename)
        if config.is_okay():
            succeed = True
            print('[done]')
        else: print('[failed]')

    if succeed and config.sim_variables:
        # read predictions
        print('reading model predictions ..', end='', flush=True)
        succeed = WaterGAP.read_predictions(config.sim_variables, output_directory_name=output_directory)
        if succeed: print('[done]')
        else: print('[failed]')


        #succeed = False
        if succeed:
            filename = '/media/sf_private/FINAL_CALIBRATION/predictions/CSV/G6C04_'
            for var in config.sim_variables:
                print('saving "%s" data ..'%var.varname, end='', flush=True)
                var.compute_anomalies()
                fname = filename + var.varname + '.csv'
                var.data_cloud.sort()
                succeed = var.data_cloud.print_data(fname, append=True, separator=',')
                if succeed: print('[done]')
                else: print('[failed]')

            if config.derived_variables:
                vars = config.derived_variables

                #filename = 'output/' + output_directory + '_'
                for var in vars:
                    print('saving "%s" data ..' % var.varname, end='', flush=True)
                    var.derive_data(simvars=config.sim_variables)
                    fname = filename + var.varname + '.csv'
                    var.data_cloud.sort()
                    succeed = var.data_cloud.print_data(fname, append=True, separator=',')
                    if succeed: print('[done]')
                    else: print('[failed]')

        results = WaterGAP.prediction_efficiency(sim_vars=config.sim_variables+config.derived_variables, obs_vars=config.obs_variables)

        for i in range(len(results)): print(results[i])

    if succeed: print('Mission Accomplished :)')
    else: print('Mission Failed!!')


if __name__ == '__main__': main()