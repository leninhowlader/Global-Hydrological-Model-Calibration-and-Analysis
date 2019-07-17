upstream_filename = 'input/brahmaputra_upstreams_bahadurabad.txt'
station_filename = ''
data_filename = 'F:/mhasan/private/ET_Mueller2013/LandFluxEVAL.merged.89-05.monthly.all.nc'
output_filename = 'output/brahmaputra_bahadurabad_ET_Mueller2013_iqr_mm_daily.csv'
# stat name should be one of the followings:
# 'ET_mean', 'ET_median', 'ET_IQR', 'ET_25', 'ET_75', 'ET_min', 'ET_max', 'ET_sd'
stat_name = 'ET_mean'

from netCDF4 import Dataset
import numpy as np, sys, os
sys.path.append('..')
from utilities.upstream import Upstream
from utilities.station import Station
from utilities.globalgrid import GlobalGrid
from utilities.fileio import write_flat_file

def ncdump(nc_fid, verb=True):
    '''
    ncdump outputs dimensions, variables and their attribute information.
    The information is similar to that of NCAR's ncdump utility.
    ncdump requires a valid instance of Dataset.

    Parameters
    ----------
    nc_fid : netCDF4.Dataset
        A netCDF4 dateset object
    verb : Boolean
        whether or not nc_attrs, nc_dims, and nc_vars are printed

    Returns
    -------
    nc_attrs : list
        A Python list of the NetCDF file global attributes
    nc_dims : list
        A Python list of the NetCDF file dimensions
    nc_vars : list
        A Python list of the NetCDF file variables
    '''


    def print_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        try:
            print ("\t\ttype:", repr(nc_fid.variables[key].dtype))
            for ncattr in nc_fid.variables[key].ncattrs():
                print ('\t\t%s:' % ncattr, repr(nc_fid.variables[key].getncattr(ncattr)))
        except KeyError:
            print ("\t\tWARNING: %s does not contain variable attributes" % key)


    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        print("NetCDF Global Attributes:")
        for nc_attr in nc_attrs:
            print('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        print("NetCDF dimension information:")
        for dim in nc_dims:
            print("\tName:", dim)
            print("\t\tsize:", len(nc_fid.dimensions[dim]))
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        print("NetCDF variable information:")
        for var in nc_vars:
            if var not in nc_dims:
                print('\tName:', var)
                print("\t\tdimensions:", nc_fid.variables[var].dimensions)
                print("\t\tsize:", nc_fid.variables[var].size)
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars


def main():
    global station_filename, upstream_filename, data_filename, output_filename, stat_name

    # step-01: input check
    print('checking input ...', end='', flush=True)
    if not (upstream_filename or station_filename) or not data_filename or not output_filename:
        print('[Not Okay]')
        exit(-1)
    else: print('[Okay]')

    # step-02: find the 0.5 deg cells for each basin
    basins_0p5deg = []
    basin_count = 0

    if upstream_filename:
        temp = GlobalGrid.read_cell_info(upstream_filename, data_type=int)
        for cell_group in temp:
            cells = []
            for cell in cell_group:
                lat, lon = GlobalGrid.get_wghm_centroid(cell)
                cells.append(GlobalGrid.find_row_column(lat, lon, degree_resolution=0.5))
            basins_0p5deg.append(cells)
        basin_count = len(temp)
        temp, cells = None, None
    else:
        stations = Station.read_stations(filename=station_filename)

        for station in stations:
            row, col = GlobalGrid.find_row_column(station[2], station[1], degree_resolution=0.5)
            cells = Upstream.get_upstream_cells(row, col)
            basins_0p5deg.append(cells)
        basin_count = len(stations)
        cells = None

    # step-03: find area of each 0.5 deg cells and find the corresponding 1.0 def? of each 0.5 deg cell
    basins_1deg = []
    barea_0p5deg = []

    if len(basins_0p5deg) == basin_count:
        for i in range(basin_count):
            basin = basins_0p5deg[i]
            temp, barea = [], []
            for j in range(len(basin)):
                temp.append(GlobalGrid.transform_row_column(basin[j][0], basin[j][1], 0.5, 1.0))
                barea.append(GlobalGrid.find_wghm_cellarea(basin[j][0]))
            basins_1deg.append(temp)
            barea_0p5deg.append(barea)

    # step-04: for each basin, find the unique 1.0 deg cells and area contribution of each unique 1.0 deg cell
    barea_1deg_contrib = []
    if len(basins_1deg) == len(barea_0p5deg):
        for i in range(len(basins_1deg)):
            basin = basins_1deg[i]
            area_0p5deg = barea_0p5deg[i]

            unique_1deg, area_1deg = [], []
            area_total = 0

            if len(basin) == len(area_0p5deg):
                for j in range(len(basin)):
                    cell = basin[j]
                    cell_area = area_0p5deg[j]
                    try: area_1deg[unique_1deg.index(cell)] += cell_area
                    except:
                        unique_1deg.append(cell)
                        area_1deg.append(cell_area)
                    area_total += cell_area
                for j in range(len(area_1deg)): area_1deg[j] = area_1deg[j]/area_total

            basins_1deg[i] = unique_1deg
            barea_1deg_contrib.append(area_1deg)
            print('Total area of basin no. %d: %f' % (i+1, area_total))

    # step-05: find latitude and longitude of each 1.0 deg unique cells
    for i in range(len(basins_1deg)):
        basin = basins_1deg[i]
        for j in range(len(basin)):
            row, col = basin[j][0], basin[j][1]
            basin[j] = GlobalGrid.find_centroid(row, col, deg_resolution=1.0)

    # step-06: open the NetCDF file, load necessary data into variables, and close file
    nc_fid = Dataset(data_filename, 'r')
    #a, b,c = ncdump(nc_fid)
    time = nc_fid.variables['time'][:]
    lats = nc_fid.variables['lat'][:]
    lons = nc_fid.variables['lon'][:]

    et_stat = nc_fid.variables[stat_name][:]

    nc_fid.close()

    # step-07: collect time series data for each basin
    for i in range(len(basins_1deg)):
        basin = basins_1deg[i]
        area_contrib = barea_1deg_contrib[i]    # fraction of total area

        et_data = None
        for j in range(len(basin)):
            cell = basin[j]
            afraction = area_contrib[j]         # afraction = area fraction
            ndx_lat = np.where(lats==cell[0])
            ndx_long = np.where(lons==cell[1])
            d = et_stat[:, ndx_lat[0], ndx_long[0]] * afraction
            try:
                et_data = np.vstack((et_data, d.data.flatten()))
            except:
                et_data = np.array(d.data.flatten())

        month_sum = np.sum(et_data, axis=0)
        if len(month_sum) == len(time):
            basin_id = i + 1
            data = []
            for j in range(len(time)):
                year = time[j] // 100
                month = time[j] % 100
                data.append([basin_id, year, month, month_sum[j]])
            write_flat_file(output_filename, data, separator=',', append=True)

if __name__ == '__main__': main()
