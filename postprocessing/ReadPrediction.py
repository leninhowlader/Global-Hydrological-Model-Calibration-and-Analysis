import sys
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP
from calibration.variable import SimVariable, DerivedVariable


config_filename = 'input/config_BRH_ReadPredictions.txt'
output_directory = 'B2C03'


def main():
    global  config_filename, output_directory

    succeed = False; config = None; vars = None

    if config_filename:
        print('reading configuration file ..', end='', flush=True)
        config = Configuration.read_configuration_file(config_filename)
        if config:
            succeed = True
            print('[done]')
        else: print('[failed]')

    if succeed and config.sim_variables:
        vars = config.sim_variables

        # read predictions
        print('reading model predictions ..', end='', flush=True)
        succeed = WaterGAP.read_predictions(vars, output_directory_name=output_directory)
        if succeed: print('[done]')
        else: print('[failed]')


        filename = 'output/' + output_directory + '_'
        for var in vars:
            print('saving "%s" data ..'%var.varname, end='', flush=True)
            var.compute_anomalies()
            fname = filename + var.varname + '.csv'
            var.data_cloud.sort()
            succeed = var.data_cloud.print_data(fname, append=True, separator=',')
            if succeed: print('[done]')
            else: print('[failed]')

    if succeed and config.derived_variables:
        vars = config.derived_variables

        filename = 'output/' + output_directory + '_'
        for var in vars:
            print('saving "%s" data ..' % var.varname, end='', flush=True)
            var.derive_data(simvars=config.sim_variables)
            fname = filename + var.varname + '.csv'
            var.data_cloud.sort()
            succeed = var.data_cloud.print_data(fname, append=True, separator=',')
            if succeed: print('[done]')
            else: print('[failed]')


    if succeed: print('Mission Accomplished :)')
    else: print('Mission Failed!!')


if __name__ == '__main__': main()