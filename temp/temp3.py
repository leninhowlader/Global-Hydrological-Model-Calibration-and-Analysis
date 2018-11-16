import sys, os, numpy as np
sys.path.append('..')
from utilities.grid import grid
from utilities.fileio import write_flat_file, read_flat_file
from utilities.upstream import Upstream

succeed = False
if succeed:
    grid.read_wghm_cell_map()
    dt = grid.wghm_grid_mapping_data

    headers = ['cell_num', 'arc_id', 'longitude', 'latitude', 'cell_area']
    for d in dt:
        row  = grid.find_row_number(d[-1])
        d.append(grid.find_wghm_cellarea(row))
    succeed = write_flat_file('wghm_grid.csv', dt, data_headers=headers, separator=',')
    print(succeed)
    #66896	66042	147.75	-38.25 'cell_num', 'arc_id', 'longitude', 'latitude'


succeed = False
if succeed:
    cell = (90.75, 22.75)
    row, col = grid.find_row_column(cell[1], cell[0], degree_resolution=0.5)
    station = [(row, col)]


    filename = 'entire_ganges_brahmaputra.shp'
    succeed = Upstream.create_basin_shape(filename, station, add_wghm_cnum=True)
    print(succeed)

succeed = False
if succeed:
    filename = '../observationprocessing/input/meghna_brahmaputra_upstream.txt'
    basin = grid.read_groupfile(filename, data_type=int)[0]
    areas = []
    for cnum in basin:
        lat, lon = grid.map_centroid_from_wghm_cell_number(cnum)
        row = grid.find_row_number(lat)
        areas.append(grid.find_wghm_cellarea(row))
    filename = '../observationprocessing/input/meghna_brahmaputra_upstream_area.txt'
    succeed = grid.write_groupfile(filename, [areas])
    print(succeed)


succeed = False
if succeed:
    filename = 'F:/mhasan/private/TestGISGeoDB/salameh_etal_2017_ganges_basin_properties.txt'
    headers, data = read_flat_file(filename, separator=',', header=True)
    # headers = ['FID', 'longitude', 'latitude', 'cell_num', 'cell_area', 'gpcp_cid']
    data = np.array(data)

    exclude_cells = [44868, 44869, 44870, 44871] # ganges: [44868, 44869, 44870, 44871] # brahmaputra: [44303, 44304]
    cells = data[:,3].astype('int32').tolist()

    exclude_cellndx_list = []
    for cell in exclude_cells: exclude_cellndx_list.append(cells.index(cell))

    exclude_cellndx_list.sort(reverse=True)
    for ndx in exclude_cellndx_list: cells.pop(ndx)

    filename = '../observationprocessing/input/ganges_salameh2017_upstream.txt'
    succeed = grid.write_groupfile(filename, [cells])


    areas = data[:,4].astype('float').tolist()
    for ndx in exclude_cellndx_list: areas.pop(ndx)
    filename = '../observationprocessing/input/ganges_salameh2017_upstream_area.txt'
    succeed = grid.write_groupfile(filename, [areas])
    print(succeed)

succeed = False
if succeed:
    filename = 'F:/mhasan/experiments/Calibration2.0/temp/observations/ganges_hardinge_bridge_mean_SWS_Papa2017.csv'
    headers, data = read_flat_file(filename, separator=',', header=True)
    mean = 0
    for d in data: mean += d[3]
    mean /= len(data)

    for d in data: d[3] -= mean
    filename = 'F:/mhasan/experiments/Calibration2.0/temp/observations/ganges_hardinge_bridge_mean_sws_variation_Papa2017.csv'
    headers[3] = 'sws_variation_km3'
    succeed = write_flat_file(filename, data, data_headers=headers, separator=',')
    print(succeed)

succeed = False
if succeed:
    filename = 'F:/mhasan/experiments/Calibration2.0/temp/observations/ganges_hardinge_bridge_discharge_km3pmon.csv'
    headers, data = read_flat_file(filename, separator=',', header=True)
    succeed = write_flat_file(filename, data, data_headers=headers, separator=',')

succeed = False
if succeed:
    filename = 'F:/mhasan/experiments/Calibration2.0/output/gan_cal2p0_15/param_value_gan_cal2p0_15.csv'
    param_dt = np.loadtxt(filename, delimiter=',')

    filename = 'F:/mhasan/experiments/Calibration2.0/output/gan_cal2p0_15/function_value_gan_cal2p0_15.csv'
    fval_dt = np.loadtxt(filename, delimiter=',')

    filename = 'F:/mhasan/experiments/Calibration2.0/output/gan_cal2p0_15/results.csv'
    result_dt = np.loadtxt(filename)

    ndx = np.where(np.isnan(fval_dt[:,1]))
    nanfvals = fval_dt[ndx]

    ndx = np.in1d(param_dt[:,0], nanfvals[:,0])
    nanpvals = param_dt[ndx]

    filename = 'F:/mhasan/experiments/Calibration2.0/output/gan_cal2p0_15/nan_param_values.csv'
    write_flat_file(filename, np.round(nanpvals.astype('float'),4), separator=',')
    # np.savetxt(filename, np.round(nanpvals.astype('float'),4), delimiter=',')

    ndx = np.where(np.isnan(fval_dt[:, 1]) == False)
    nanfvals = fval_dt[ndx]

    ndx = np.in1d(param_dt[:, 0], nanfvals[:, 0])
    nanpvals = param_dt[ndx]

    filename = 'F:/mhasan/experiments/Calibration2.0/output/gan_cal2p0_15/non_nan_param_values.csv'
    write_flat_file(filename, np.round(nanpvals.astype('float'), 4), separator=',')

succeed = False
if succeed:
    from calibration.configuration import Configuration
    from calibration.parameter import Parameter
    from calibration.watergap import WaterGAP

    param = Parameter()

    filename = 'F:/mhasan/experiments/Calibration2.0/configuration_gan_cal2p0_15.txt'
    config = Configuration.read_configuration_file(filename)
    WaterGAP.is_okay()

    lo_lim, hi_lim = [], []
    for param in config.parameters:
        lo_lim.append(param.get_lower_bound())
        hi_lim.append(param.get_upper_bound())
    print(lo_lim)
    print(hi_lim)

    pvals = [3.6212,2.0589,1.3821,0.0605,-2.1947,0.9395,1.1819,1.3888,1.2805,1.9857,0.9637]
    for i in range(len(config.parameters)):
        param = config.parameters[i]
        param.set_parameter_value(pvals[i])

    for i in range(len(config.parameters)):
        print(config.parameters[i].get_parameter_value())

    filename = 'temp/parameters_noCorrFac.json'
    WaterGAP.json_parameter_file = filename
    WaterGAP.home_directory = ''
    WaterGAP.dir_info.input_directory = ''

    WaterGAP.read_json_parameter_file(filename)

    # filename = 'F:/mhasan/private/temp/parameters_t20181017_01.json'
    filename = 'temp/parameters_t20181017_01.json'
    succeed = WaterGAP.update_parameter_file(config.parameters, filename)
    print(succeed)


    paramset = WaterGAP.json_paramset
    for i in range(len(config.parameters)):
        pname = config.parameters[i].parameter_name
        values = np.array(paramset[pname])
        print(np.unique(values))


def read_watergap_binary_file(filename):
    ftype = -1
    try: ftype = int(filename[-1])
    except: pass

    dtype = '>'
    if ftype == 0: dtype += 'f'
    elif ftype == 1: dtype += 'b'
    elif ftype == 2: dtype += 'h'
    elif ftype == 4: dtype += 'i'
    else: return None

    return np.fromfile(filename, dtype=dtype)

def reshape_watergap_binary(data_arr, ncol):
    nrow = data_arr.shape[0]//ncol

    try: return data_arr.reshape((nrow, ncol))
    except: return None

succeed = False
if succeed:
    filename = 'F:/mhasan/private/temp/WGHM_TEST_OUTPUT/G_RIVER_AVAIL_1989.12.UNF0'
    discharge = read_watergap_binary_file(filename)

    ncol = 12
    discharge = reshape_watergap_binary(discharge, ncol)

    gan_downstream = 43452

succeed = False
if succeed:
    # filename = 'F:/mhasan/experiments/WaterGAP_EET_v2p0/output/efficiencies_eet_v2_x.txt'
    filename = 'F:/mhasan/Experiments/SENSITIVITY_DATASET_GB/WaterGAP_EET/output/efficiencies_eet_x.txt'
    h, data = read_flat_file(filename, separator=',', header=False)

    discharge_gan, discharge_brh = [], []
    for d in data:
        if d[1] == 'ObsDischargeGAN': discharge_gan.append([d[0]]+d[3:])
        elif d[1] == 'ObsDischargeBRH': discharge_brh.append([d[0]]+d[3:])

    dgan = np.array(discharge_gan)
    ndx = np.where(np.isnan(dgan[:,1]))
    ndx = dgan[ndx][:, 0]

    # filename = 'F:/mhasan/experiments/WaterGAP_EET_v2p0/input/wghm_eet_samples_v2_x.dat'
    filename = 'F:/mhasan/Experiments/SENSITIVITY_DATASET_GB/WaterGAP_EET/input/wghm_eet_samples_x.dat'
    x = np.loadtxt(filename, delimiter=',')

    nan_samples = x[ndx.astype('int32'),:]

    filename = 'F:/mhasan/Experiments/SENSITIVITY_DATASET_GB/WaterGAP_EET/output/nan_samples.csv'
    write_flat_file(filename, nan_samples, separator=',')