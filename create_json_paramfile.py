# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 21:10:30 2019

@author: mhasan
"""

from calibration.configuration import Configuration
import numpy as np, pandas as pd, os
from wgap.watergap import WaterGAP
from wgap.wgapoutput import WGapOutput
from utilities.globalgrid import GlobalGrid







# GANGES: Best solution
filename = 'input/configuration_gan_cal3p0_15.txt'
config = Configuration.read_configuration_file(filename)
succeed = config.is_okay()
print(succeed)

filename = 'F:/mhasan/experiments/Calibration3.0/Prediction_With_Borg_Solutions/output_GAN/borg_solutions_gan.dat'
d = pd.read_csv(filename, sep=',')


d_gan15 = d.iloc[-45:, :]
p = d_gan15.iloc[16, 2:-4].values

for i in range(len(config.parameters)): config.parameters[i].set_parameter_value(p[i])

for i in range(len(config.parameters)): print(config.parameters[i].get_parameter_value())

succeed = WaterGAP.update_parameter_file(config.parameters, 'parameters_g15_best.json')

# BRAHMAPUTRA: BEST SOLUTION
filename = 'input/configuration_brh_cal3p0_15.txt'
config = Configuration.read_configuration_file(filename)
succeed = config.is_okay()
print(succeed)

filename = 'F:/mhasan/experiments/Calibration3.0/Prediction_With_Borg_Solutions/output_BRH/borg_solutions_brh.dat'
d = pd.read_csv(filename, sep=',')
d_brh15 = d.iloc[-22:, :]
p = d_brh15.iloc[17, 2:-4].values

for i in range(len(config.parameters)): config.parameters[i].set_parameter_value(p[i])

for i in range(len(config.parameters)): print(config.parameters[i].get_parameter_value())

succeed = WaterGAP.update_parameter_file(config.parameters, 'parameters_brh15_best.json')
print(succeed)

# read model output

# GANGES BASIN
filename = 'F:/mhasan/PyScript/ganges_hardinge_bridge_upstreams.txt'
wcell_gan = np.array(GlobalGrid.read_cell_info(filename)[0])
filename = 'F:/mhasan/PyScript/ganges_hardinge_bridge_areas.txt'
area_gan = np.array(GlobalGrid.read_cell_info(filename, data_type=float)[0]).reshape(339, 1)

output_directory = 'F:/mhasan/experiments/Calibration3.0/Prediction_With_Borg_Solutions/output_gan15_best'

start_year, end_year = 1989, 2014


# et
et_gan = None
for year in range(start_year, end_year+1, 1):
    filename = os.path.join(output_directory, 'G_CELL_AET_%d.12.UNF0'%year)
    
    d = WGapOutput.read_unf(filename)
    d_gan = d[wcell_gan-1]
    
    et = d_gan * area_gan / 10**6
    et = et.sum(axis=0)
    try: et_gan = np.concatenate((et_gan, et.reshape(1,12)), axis=0)
    except: et_gan = et.reshape(1,12)

annual_et_gan = et_gan.flatten()[2:-10].reshape(end_year-start_year, 12).sum(axis=1)
for x in annual_et_gan: print(x)

# river discharge
discharge_cell = 43452
q_gan = None
for year in range(start_year, end_year+1, 1):
    filename = os.path.join(output_directory, 'G_RIVER_AVAIL_%d.12.UNF0'%year)
    
    d = WGapOutput.read_unf(filename)
    d_gan = d[discharge_cell-1]
    
#    q = d_gan * area_gan / 10**6
#    q = q.sum(axis=0).reshape(1, 12)
    q = d_gan.reshape(1,12)
    try: q_gan = np.concatenate((q_gan, q), axis=0)
    except: q_gan = q

annual_q_gan = q_gan.flatten()[2:-10].reshape(end_year-start_year, 12).sum(axis=1)
for x in annual_q_gan: print(x)

# storage variation
dtws_gan = None
for year in range(start_year, end_year+1, 1):
    filename = os.path.join(output_directory, 'G_TOTAL_STORAGES_km3_%d.12.UNF0'%year)
    
    d = WGapOutput.read_unf(filename)
    d_gan = d[wcell_gan-1]
    
    dtws = d_gan.sum(axis=0)
    try: dtws_gan = np.concatenate((dtws_gan, dtws.reshape(1,12)), axis=0)
    except: dtws_gan = dtws.reshape(1,12)

d = dtws_gan[:,1].flatten()
annual_dtws_gan = [d[i]-d[i-1] for i in range(1, len(d))]
for x in annual_dtws_gan: print(x)



# BRAHMAPUTRA
filename = 'F:/mhasan/PyScript/brahmaputra_bahadurabad_upstreams.txt'
wcell_brh = np.array(GlobalGrid.read_cell_info(filename)[0])
filename = 'F:/mhasan/PyScript/brahmaputra_bahadurabad_areas.txt'
area_brh = np.array(GlobalGrid.read_cell_info(filename, data_type=float)[0]).reshape(190, 1)

output_directory = 'F:/mhasan/experiments/Calibration3.0/Prediction_With_Borg_Solutions/output_brh15_best'

# et
et_brh = None
for year in range(start_year, end_year+1, 1):
    filename = os.path.join(output_directory, 'G_CELL_AET_%d.12.UNF0'%year)
    
    d = WGapOutput.read_unf(filename)
    d_gan = d[wcell_brh-1]
    
    et = d_gan * area_brh / 10**6
    et = et.sum(axis=0)
    try: et_brh = np.concatenate((et_brh, et.reshape(1,12)), axis=0)
    except: et_brh = et.reshape(1,12)

annual_et_brh = et_brh.flatten()[2:-10].reshape(end_year-start_year, 12).sum(axis=1)
for x in annual_et_brh: print(x)

# river discharge
discharge_cell = 42897
q_brh = None
for year in range(start_year, end_year+1, 1):
    filename = os.path.join(output_directory, 'G_RIVER_AVAIL_%d.12.UNF0'%year)
    
    d = WGapOutput.read_unf(filename)
    d_brh = d[discharge_cell-1]
    
    q = d_brh * area_brh / 10**6
    q = q.sum(axis=0).reshape(1,12)
#    q = d_brh.reshape(1,12)
    try: q_brh = np.concatenate((q_brh, q), axis=0)
    except: q_brh = q

annual_q_brh = q_brh.flatten()[2:-10].reshape(end_year-start_year, 12).sum(axis=1)
for x in annual_q_brh: print(x)


# storage variation
dtws_brh = None
for year in range(start_year, end_year+1, 1):
    filename = os.path.join(output_directory, 'G_TOTAL_STORAGES_km3_%d.12.UNF0'%year)
    
    d = WGapOutput.read_unf(filename)
    d_brh = d[wcell_brh-1]
    
    dtws = d_brh.sum(axis=0)
    try: dtws_brh = np.concatenate((dtws_brh, dtws.reshape(1,12)), axis=0)
    except: dtws_brh = dtws.reshape(1,12)

d = dtws_brh[:,1].flatten()
annual_dtws_brh = [d[i]-d[i-1] for i in range(1, len(d))]
for x in annual_dtws_brh: print(x)
