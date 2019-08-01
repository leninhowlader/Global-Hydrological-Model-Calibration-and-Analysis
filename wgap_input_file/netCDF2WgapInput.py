from netCDF4 import Dataset
import numpy as np, sys, struct, os
sys.path.append('..')
from utilities.globalgrid import GlobalGrid
from datetime import datetime, timedelta
from copy import deepcopy
from utilities.enums import FileEndian

# data filenames
filename_list = ['/media/sf_mhasan/private/temp/Temperature future tas_bced_1960_1999_miroc-esm-chem_rcp2p6_2006-2010.nc']

# variable names
varname_data = 'tasAdjust'
varname_time = 'time'
varname_longitude = 'lon'
varname_latitude = 'lat'
base_date = datetime(year=1860, month=1, day=1)

# output configuration
output_dir = '/media/sf_mhasan/private/temp/new_input_file'
ofile_prefix = 'GTEMP'       # output file prefix
file_endian = FileEndian.big_endian

# wghm grid cell count
wghm_cell_count = 66896

def main():
    global filename_list, varname_data, varname_time, varname_longitude, varname_latitude, ofile_prefix
    global file_endian, wghm_cell_count, base_date, output_dir

    # chece inputs
    print('checking inputs ... ', end='', flush=True)
    succeed = True
    if not (filename_list and varname_data and varname_time and varname_longitude and varname_latitude and ofile_prefix):
        succeed = False
    if succeed: print('[okay]')
    else:
        print('[not okay]')
        exit(os.EX_NOINPUT)

    # read wghm world grid
    print('reading wghm grid info ... ', end='', flush=True)
    GlobalGrid.read_wghm_grid_lookup_table()
    mapData = deepcopy(GlobalGrid.__wghm_grid_lookup_table)
    for i in range(len(mapData)):
        mapData[i] = GlobalGrid.find_row_column(mapData[i][3], mapData[i][2], degree_resolution=0.5)
    if not mapData or len(mapData) != wghm_cell_count: succeed = False
    if succeed: print('[done]')
    else:
        print('[failed]')
        exit(os.EX_DATAERR)

    # create output directory if necessary
    if not os.path.exists(output_dir): os.mkdir(output_dir)

    month_names = ['0th', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # extract data from datafile and export into UNF files
    for filename in filename_list:
        print('data extraction from netCDF datafile: %s' % filename)

        # open netCDF file
        nc_fid = Dataset(filename, 'r')

        # extract variables from the netCDF file
        time = nc_fid.variables[varname_time][:]
        lats = nc_fid.variables[varname_latitude][:]
        lons = nc_fid.variables[varname_longitude][:]


        # create date list from time variable
        date_list = [base_date + timedelta(days=t) for t in time]

        # based on dates, create monthly groups of date indices in date list
        date_ndx_map, temp_map = [], []
        cur_year, cur_mon = date_list[0].year, date_list[0].month
        for i in range(len(time)):
            if date_list[i].year == cur_year and date_list[i].month == cur_mon: temp_map.append(i)
            else:
                date_ndx_map.append(temp_map)
                cur_year, cur_mon = date_list[i].year, date_list[i].month
                temp_map = [i]
        date_ndx_map.append(temp_map)

        # read the data variable from netCDF
        data_var = nc_fid.variables[varname_data][:]

        # reconstruct monthly data into wghm-like grid from extracted data
        print('\tdata reconstruction for each month')
        succeed = True
        for mon_ndx in date_ndx_map:
            # retrieve monthly data
            d = date_list[mon_ndx[0]]
            print('\t%d-%s:'%(d.year, month_names[d.month]))
            print('\t\tdata construction ... ', end='', flush=True)
            month_data = np.zeros(shape=(66896, 31), dtype=np.float32)
            for i in range(len(mapData)):
                r, c = mapData[i]
                month_data[i, :len(mon_ndx)] = data_var[mon_ndx, r, c]
            print('[done]')

            # save monthly data into UNF file
            filename = ofile_prefix + '_%d_%d.31.UNF0'%(d.year, d.month)
            print('\t\toutput filename: %s' % filename)
            print('\t\twriting file ... ', end='', flush=True)
            f = None
            try:
                f = open(os.path.join(output_dir, filename), 'wb')

                fmt = 'f' * 31
                if file_endian == FileEndian.big_endian: fmt = '>' + fmt
                else: fmt = '<' + fmt

                for i in range(len(month_data)):
                    b = struct.pack(fmt, *list(month_data[i]))
                    f.write(b)
            except: succeed = False
            finally:
                try: f.close()
                except: pass
            if succeed: print('[done]')
            else: print('[failed]')

    if succeed: print('program ended successfully')
    else:
        print('program failed')
        exit(os.EX_SOFTWARE)

    exit(os.EX_OK)

if __name__ == '__main__': main()