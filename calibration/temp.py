import os, sys
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.wgapoutput import WGapOutput
import numpy as np

os.chdir(os.path.join(os.getcwd(), 'calibration'))

filename = 'input/configuration_eet_x.txt'
os.path.exists(filename)
config = Configuration.read_configuration_file(filename)


wghm_output_dir = '../../test'

var = config.sim_variables[0]
filename = os.path.join(wghm_output_dir, var.data_source.filename.replace('[YEAR]', '1989'))


data = WGapOutput.read_unf(filename)
basin = np.array(var.cell_groups[0]) - 1
dt = data[basin]

basin_avg = np.mean(dt, axis=0)

filename = 'test.bin'

fid = open(filename, 'ab')
fid.write(basin_avg.astype('>f').tobytes())
fid.close()

basin_avg.astype('float32').tofile(filename)

dt = np.fromfile(filename, '>f')
dt_a = dt.reshape(dt.size//14, 14)

def create_monthly_time_series(start_year, end_year):
    var = config.sim_variables[0]

