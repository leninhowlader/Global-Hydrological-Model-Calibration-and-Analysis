from datetime import datetime
from wgap.wgapinput import WaterGapInput
from utilities.globalgrid import GlobalGrid

# set mode version
GlobalGrid.set_model_version('wghm22d')

# define boundary box of the target zone
lon_min, lon_max = -12.5, 19.0
lat_min, lat_max = 46, 66
model_cells = WaterGapInput.model_cell_within_bbox(lon_min=lon_min, lat_min=lat_min, lon_max=lon_max, lat_max=lat_max)

# define netCDF filename, output directory, start data etc.....
filename = 'Z:/USER/Mehedi_Hasan/bias_adjust_EURO_CORDEX/prAdjust_EUR-11_ICHEC-EC-EARTH_historical_r12i1p1_SMHI-RCA4_v1-JRC-SBC-EOBS10-1981-2010_day_19810101-20101231_regrid.nc'
output_directory = 'F:/mhasan/private/temp/forcing_data_unf'
output_fileprefix = 'GPREC'
base_date = datetime(year=1981, month=1, day=1)
varname_data = 'tasAdjust'

# optional variables
varname_time='time'
varname_lon='lon'
varname_lat='lat'
verbose = True

succeed = WaterGapInput.netcdf_to_unf(netcdf_filename=filename, output_directory=output_directory,
                                      output_filename_prefix=output_fileprefix, base_date=base_date,
                                      varname_data=varname_data, cells_xy=model_cells, varname_time=varname_time,
                                      varname_lat=varname_lat, varname_lon=varname_lon, verbose=verbose)