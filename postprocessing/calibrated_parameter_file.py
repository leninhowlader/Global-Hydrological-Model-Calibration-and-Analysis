
postfix = 'B2C18'
config_filename = 'input/configuration_BRH_' + postfix + '.txt'
result_filename = 'input/results/results_' + postfix + '.csv'


import sys, os
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP
from calibration.parameter import Parameter
from postprocessing.borgoutput import BorgOutput




def main():
    global config_filename, result_filename
    succeed = False
    pfile_count = 0


    config = None
    if config_filename: config = Configuration.read_configuration_file(config_filename)

    result = None
    if result_filename: result = BorgOutput.read_borg_output(result_filename)

    if config.parameters and WaterGAP.is_okay() and result:
        nobj = len(config.obs_variables)
        nparam = len(config.parameters)
        nsln = len(result)
        for i in range(nsln):
            r = result[i][:-nobj]
            if len(r) == nparam:
                for j in range(nparam):
                    param = config.parameters[j]
                    param.set_parameter_value(r[j])

            filename = ''
            if nsln > 1: filename = WaterGAP.json_parameter_file[:-5] + '_' + config_filename[-9:][:-4] + '_' + str(i+1).rjust(3, '0') + '.json'
            else: filename = WaterGAP.json_parameter_file[:-5] + '_' + config_filename[-9:][:-4] + '.json'

            succeed = WaterGAP.update_parameter_file(config.parameters, filename)
            if succeed: pfile_count += 1

    # if pfile_count > 0 : succeed = True
    # #WaterGAP.update_parameter_file()
    # print(len(config.parameters))
    # print(WaterGAP.json_parameter_file)
    print(pfile_count)

if __name__ == '__main__': main()