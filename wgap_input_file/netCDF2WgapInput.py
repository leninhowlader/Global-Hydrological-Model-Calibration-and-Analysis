from netCDF4 import Dataset
import numpy as np, sys
sys.path.append('..')
from utilities.fileio import write_UNF_file
from utilities.grid import grid
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

filename = '/media/sf_mhasan/private/temp/Longwave future rlds_bced_1960_1999_miroc-esm-chem_rcp2p6_2006-2010.nc'

'''
NetCDF Global Attributes:
	project_id: 'isimip-ft'
	product_id: 'input'
	model_id: 'miroc-esm-chem'
	institute_id: 'PIK'
	experiment_id: 'rcp26'
	ensemble_id: 'r1i1p1'
	time_frequency: 'daily'
	creator: 'isimip@pik-potsdam.de'
	description: 'MIROC-ESM-CHEM bias corrected impact model input prepared for ISIMIP Fast Track Phase.\n  ISIMIP Terms of Use: https://esg.pik-potsdam.de/projects/esgf-pik/tou ,\n  Bias Correction: https://www.pik-potsdam.de/research/climate-impacts-and-vulnerabilities/research/rd2-cross-cutting-activities/isi-mip/for-modellers/technical-support'
	doi: '10.5880/PIK.2016.001'
NetCDF dimension information:
	Name: lon
		size: 720
		type: dtype('float64')
		standard_name: 'longitude'
		long_name: 'longitude'
		units: 'degrees_east'
		axis: 'X'
	Name: lat
		size: 360
		type: dtype('float64')
		standard_name: 'latitude'
		long_name: 'latitude'
		units: 'degrees_north'
		axis: 'Y'
	Name: time
		size: 1826
		type: dtype('float64')
		standard_name: 'time'
		units: 'days since 1860-1-1 00:00:00'
		calendar: 'standard'
		axis: 'T'
NetCDF variable information:
	Name: rldsAdjust
		dimensions: ('time', 'lat', 'lon')
		size: 473299200
		type: dtype('float32')
		_FillValue: 1e+20
		missing_value: 1e+20
		long_name: 'Bias-Corrected Surface Downwelling Longwave Radiation'
		units: 'W m-2'
		standard_name: 'surface_downwelling_longwave_flux_in_air'
'''
a = datetime.now()

nc_fid = Dataset(filename, 'r')
# a, b,c = ncdump(nc_fid)

time = nc_fid.variables['time'][:]
lats = nc_fid.variables['lat'][:]
lons = nc_fid.variables['lon'][:]

longWL = nc_fid.variables['rldsAdjust'][:]
print(longWL.ndim)
r,c = grid.find_row_column(25.25, 89.75)
d = longWL[0:5,r, c]
for itm in d: print(itm)
base_date = datetime(year=1860, month=1, day=1)
print([base_date+timedelta(days=t) for t in time[:10]])
print(datetime.now()-a)
