import os, sys
sys.path.append('..')
from calibration.configuration import Configuration
from wgap.wgapoutput import WGapOutput
from wgap.watergap import WaterGAP
import numpy as np

# os.chdir(os.path.join(os.getcwd(), 'calibration'))

filename = 'input/configuration_eet_x.txt'
os.path.exists(filename)
config = Configuration.read_configuration_file(filename)


wghm_output_dir = '../../test'
dumping_directory = os.path.join(wghm_output_dir, 'output')
# var = SimVariable()
var = config.sim_variables[0]
var.data_source.file_endian = WaterGAP.output_endian_type
var.group_stats = False

succeed = var.data_collection(1989, 2000, prediction_directory=wghm_output_dir)
print(succeed)

succeed = var.dump_time_series_from_model_prediction(1989, 2000, [12], dumping_directory=dumping_directory,
                                                     prediction_directory=wghm_output_dir)
print(succeed)

succeed = False
if succeed:
    filename = os.path.join(wghm_output_dir, 'output', 'ETSoilBRH_mm.15.unf0')
    data = WGapOutput.read_unf(filename)

    basin = np.array(var.cell_groups[0]) - 1
    dt = data[basin]

    basin_avg = np.mean(dt, axis=0)

    filename = 'test.bin'

    fid = open(filename, 'ab')
    fid.write(basin_avg.astype('>f').tobytes())
    fid.close()

    basin_avg.astype('float32').tofile(filename)

    dt = np.fromfile(filename, '<f')
    dt_a = dt.reshape(dt.size//14, 14)

    filename = os.path.join(wghm_output_dir, 'G_AET_1989.12.UNF0')
    dt = np.fromfile(filename, '>f')
    dt = dt.reshape(66896, 12)
    basin = var.cell_groups[0]
    d = dt[basin]

