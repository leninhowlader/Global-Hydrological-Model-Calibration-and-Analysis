import sys, numpy as np
sys.path.append('..')
from utilities.fileio import read_flat_file, write_flat_file
from utilities.station import Station
from utilities.grid import grid
from utilities.upstream import Upstream

filename_data = '/media/sf_mhasan/private/temp/new_papa_dataset/surface_water_volume_change_global_1993_2007_from_aster_GB.dat'
filename_grid_intersect = '/media/sf_mhasan/private/temp/new_papa_dataset/EAG_WGHMG_INTERSECT.CSV'
filename_station = 'STATIONS.DAT'
filename_output = '/media/sf_mhasan/private/temp/new_papa_dataset/brahmaputra_sws_2017_aster.csv'

station_file_text = """
2646200 88.75 24.25 -99 -99 -99
2651100 89.75 25.25 -99 -99 -99
"""

data_area_frc = {}  # {wcnum: {ecnum: af, ecnum: af, ...}, ...}
data_sws = {}       # {ecnum: [m1d, m2d, ...], ..}
flag_header = True

def read_area_fraction_dataset():
    succeed = True

    global filename_grid_intersect, data_area_frc

    data_area_frc = {}

    header, data = read_flat_file(filename_grid_intersect, separator=',', header=True)

    ndx_wcn, ndx_ecn, ndx_af = 4, 3, 7  # ndx_wcn = index for wghm cell num; ndx_ecn = index for EAG cell num, ndx_af = index for area fraction

    for d in data:
        try: data_area_frc[d[ndx_wcn]][d[ndx_ecn]] = d[ndx_af]
        except: data_area_frc[d[ndx_wcn]] = {d[ndx_ecn]: d[ndx_af]}

    if not data_area_frc: succeed = False

    return succeed

def read_basin_cells():
    global filename_station

    basins = []

    stations = Station.read_stations(filename_station)

    for station in stations:
        row, col = grid.find_row_column(station[2], station[1], degree_resolution=0.5)
        temp = Upstream.get_upstream_cells(row, col)
        temp = [(row, col)] + temp
        for i in range(len(temp)): temp[i] = grid.map_wghm_cell_number(temp[i][0], temp[i][1], base_resolution=0.5)
        basins.append(temp)

    return basins

def read_SWS_data():
    succeed = True

    global filename_data, data_sws

    data_sws = {}
    h, data = read_flat_file(filename_data, separator=' ')

    for d in data: data_sws[d[0]] = d[5:]

    if not data_sws: succeed = False

    return succeed

def save_basin_total(basin_id, basin_totals):
    global filename_output, flag_header

    headers = ['basin_id', 'year', 'month', 'sws_km3']
    data = []

    year = 1993
    month = 1
    for t in basin_totals:
        data.append([basin_id, year, month, t])
        month += 1
        if month == 13:
            year += 1
            month = 1
    if flag_header:
        succeed = write_flat_file(filename_output, data, data_headers=headers, separator=',', append=True)
        flag_header = False
    else: succeed = write_flat_file(filename_output, data, separator=',', append=True)

    return succeed

def main():
    succeed = True

    global data_area_frc, data_sws

    # read area fraction dataset
    print('reading grids-intersection area fraction data ... ', end='', flush=True)
    succeed = read_area_fraction_dataset()
    if succeed: print('[done]')
    else:
        print('[failed]')
        exit('\nThe program is being terminated')

    # read SWS datafile
    print('reading SWS data ... ', end='', flush=True)
    succeed = read_SWS_data()
    if succeed: print('[done]')
    else:
        print('[failed]')
        exit('\nThe program is being terminated')

    # read basin cells from station file
    print('reading basin cells of targeted stations ...', end='', flush=True)
    basins = read_basin_cells()
    if basins: print('[done]')
    else:
        print('[failed]')
        exit('\nThe program is being terminated')

    # calculate basin totals
    print('calculating basin totals: total basins %d'%len(basins))
    for i in range(len(basins)):
        basin_id = i + 1
        print('\tdata processing for basin no. %d .... '%(basin_id), end='', flush=True)
        basin = basins[i]
        basin_tsws = np.zeros(180)
        for wcnum in basin:
            try: area_frc = data_area_frc[wcnum]
            except: area_frc = {}

            for enum, af in area_frc.items():
                basin_tsws += np.array(data_sws[enum]) * af
        print('[done]')

        # save the basin total into output file
        print('\tprinting basin total into output file .... ', end='', flush=True)
        succeed = save_basin_total(basin_id, basin_tsws.tolist())
        if succeed: print('[done]')
        else: print('[failed]')

    # print(data_area_frc[basins[0][0]])

if __name__ == '__main__': main()