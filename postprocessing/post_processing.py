
config_filename = 'ganges_configuration_km3.txt'
borg_output_filename = 'results.txt'
filename_postfix = 'ganges_optimum'

import sys
sys.path.append('..')
from postprocessing.borgoutput import BorgOutput
from calibration.configuration import Configuration
from wgap.watergap import WaterGAP


def main():
    global config_filename, borg_output_filename, filename_postfix

    succeed = False

    # read the configuration file
    config = Configuration.read_configuration_file(config_filename)
    if config.is_okay() and WaterGAP.is_okay(): succeed = True

    # read pareto-optimal parameter sets from borg-output file
    pset = []
    if succeed:
        nobj = config.get_objective_count()
        results = BorgOutput.read_borg_output(borg_output_filename)
        selected_best = 9
        # pset, ndx = BorgOutput.find_best_parameterset(results, nobj)
        pset = results[selected_best][:-nobj]

        if not pset: succeed = False

    if succeed and pset:
        # update values of the parameters in config object
        params = config.parameters
        if pset and len(pset)==config.get_parameter_count():
            for i in range(config.get_parameter_count()):
                params[i].set_parameter_value(pset[i])

        # update the model parameter file
        parameter_filename = 'parameters_' + filename_postfix + '.json'
        succeed = WaterGAP.update_parameter_file(params, parameter_filename)

        # run the model
        dir_file = 'data_' + filename_postfix + '.dir'
        if succeed:
            output_dir = 'output_' + filename_postfix
            succeed = WaterGAP.update_directory_info(output_dir, dir_file)

        if succeed:
            arguments = {}
            arguments['p'] = parameter_filename
            arguments['d'] = dir_file

            succeed = WaterGAP.execute_model(arguments)

    if succeed: print('succeeded')
    else: print('not succeeded')

if __name__ == '__main__':
    main()