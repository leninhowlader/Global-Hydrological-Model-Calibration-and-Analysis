basin_cell_file = 'input/ganges_upstreams_hardinge_bridge.txt' # 'brahmaputra_upstreams_bahadurabad.txt'
basin_area_file = 'input/ganges_areas_hardinge_bridge.txt' # 'brahmaputra_areas_bahadurabad.txt'
data_filename = 'Z:/USER/Andreas_Guentner/GRACE/ITSG-Grace2016_monthly_land_DDK2.nc'
correction_factor_filename =  'F:/mhasan/private/GRACE/LND_1x1_scalingFactor_DDK2.txt'
output_file = 'output/ganges_ITSG_RAW_DDK2_with_scaling.csv'
unit_conversion_factor = 10**-6



from netCDF4 import Dataset
import numpy as np, sys, os
sys.path.append('..')
from utilities.grid import grid
from utilities.fileio import write_flat_file

from datetime import datetime, timedelta


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

def find_grace1deg_cells(wgmh_cell_list):
    grace1deg_cells = []

    for cnum in wgmh_cell_list:
        centroid_lat, centroid_lng = grid.map_centroid_from_wghm_cell_number(cnum)
        grace_row, grace_col = grid.find_row_column(centroid_lat, centroid_lng, 1.0)
        centroid_lat, centroid_lng = grid.find_centroid(grace_row, grace_col, 1.0)
        grace1deg_cells.append((centroid_lat, centroid_lng))

    return grace1deg_cells

def find_year_month(base_date, days=0):
    base_date += timedelta(days=days)
    return base_date.year, base_date.month


def main():
    basin_cells = grid.read_groupfile(basin_cell_file, data_type=int)[0]
    cell_count = len(basin_cells)

    basin_areas = grid.read_groupfile(basin_area_file, data_type=float)[0]

    grace_1deg_cells = find_grace1deg_cells(basin_cells)

    scaling_factors = np.ones(cell_count)
    if correction_factor_filename:
        sf = np.loadtxt(correction_factor_filename, skiprows=6)

        for i in range(cell_count):
            lat, lon = grace_1deg_cells[i]
            sf_ndx = np.where((sf[:, 0] == lon) & (sf[:, 1] == lat))
            scaling_factors[i] = sf[sf_ndx][0, 2]


    nc_fid = Dataset(data_filename, 'r')
    # ncdump(nc_fid)

    time = nc_fid.variables['time'][:]
    lats = nc_fid.variables['lat'][:]
    lons = nc_fid.variables['lon'][:]

    base_date = datetime(1858, 11, 17)
    twsa = nc_fid.variables['twsa'][:]
    nc_fid.close()

    basin_twsa = None
    for i in range(len(basin_cells)):
        lat, lon = grace_1deg_cells[i]
        lat_ndx, lon_ndx = np.where(lats==lat), np.where(lons==lon)

        d = twsa[:, lat_ndx, lon_ndx] * basin_areas[i] * scaling_factors[i]

        try: basin_twsa = np.vstack((basin_twsa, d.data.flatten()))
        except: basin_twsa = np.array(d.data.flatten())

    # basin average
    sums = np.sum(basin_twsa, axis=0)
    sums = sums * unit_conversion_factor
    sums = sums.reshape((161, 1))

    year_month = np.array([find_year_month(base_date, x) for x in time])
    dt = np.concatenate((year_month, sums), axis=1)

    write_flat_file(output_file, dt, data_headers=['year', 'month', 'twsa'])

if __name__ == '__main__': main()