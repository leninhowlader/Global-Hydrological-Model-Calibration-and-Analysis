import os, sys, numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from netCDF4 import Dataset

from utilities.globalgrid import GlobalGrid as gg
from wgap.wgapoutput import WGapOutput

class WaterGapInput:
    @staticmethod
    def model_cell_within_bbox(lon_min, lat_min, lon_max, lat_max):
        '''
        This method selects model cells within a boundary box specified by the min and max coordinates.

        :param lon_min: (float) left limit of boundary box
        :param lat_min: (float) bottom limit of boundary box
        :param lon_max: (float) right limit of boundary box
        :param lat_max: (float) top limit of boundary box
        :return: (numpy 2-d array) centroid-coordinates of selected model cells
        '''
        model_cells = gg.get_wghm_world_grid_centroids()[:,[1,0]]
        
        ndx = np.where((model_cells[:,0]>=lon_min) & (model_cells[:,0]<=lon_max) & (model_cells[:,1]>=lat_min) & 
                       (model_cells[:,1]<=lat_max))
        
        return model_cells[ndx]
    
    @staticmethod
    def netcdf_to_unf(netcdf_filename, output_filename_prefix, output_directory, base_date, varname_data, 
                      varname_time='time', varname_lon='lon', varname_lat='lat', cells_xy=np.array([]),
                      verbose=True):
        '''
        This method reads netCDF file and export data into model readable UNF files.

        :param netcdf_filename: (string) netCDF filename
        :param output_filename_prefix: (string) Prefix of output file(s)
        :param output_directory: (string) Output directory
        :param base_date: (datetime) Start date
        :param varname_data: (string) Name of data field (variable) in netCDF dataset
        :param varname_time: (string) Name of time variable in netCDF dataset
        :param varname_lon: (string) Name of longitude variable in netCDF dataset
        :param varname_lat: (string) Name of latitude variable in netCDF dataset
        :param cells_xy: (numpy 2-d array; optional, default empty array) Model cell coordinates. If cells are not
                        provide, data for all cells will be exported
        :param verbose: (boolean) Flag to print additional information
        :return: (boolean) True on success, False otherwise
        '''

        succeed = True
        
        # inner function
        def degree_east_to_signed_degree(lons: np.ndarray):
            ndx = np.where(lons >= 180)
            lons[ndx] -= 360
            return lons
        # end of inner function

        # inner function
        def nearest_centroid_latitude(lats: np.ndarray, grid_resolution=0.5):
            lats = ((90 + lats) // grid_resolution) * grid_resolution + float(grid_resolution) / 2 - 90

            ndx = np.where(lats > 90)
            lats[ndx] = lats[ndx] - grid_resolution

            return lats
        # end of inner function

        # inner function
        def nearest_centroid_longitude(lons:np.ndarray, grid_resolution=0.5):
            lons = ((180 + lons) // grid_resolution) * grid_resolution + float(grid_resolution) / 2 - 180

            ndx = np.where(lons > 180)
            lons[ndx] = lons[ndx] - 360

            return lons
        # end of inner function

        fid = Dataset(netcdf_filename, 'r')

        # step: read dimensions
        # time = fid.variables[varname_time][:]
        lons = fid.variables[varname_lon][:]
        lats = fid.variables[varname_lat][:]

        # calculate cell centroids
        lats = nearest_centroid_latitude(lats)
        lons = nearest_centroid_longitude(lons)

        # step: get WGHM cell coordinates
        if len(cells_xy) == 0: cells_xy = gg.get_wghm_world_grid_centroids()[:,[1,0]]

        # step: find latitude and longitude index in NetCDF dataset for WGHM cells
        lati, loni = [], []
        try:
            lati = [np.where(lats==x)[0][0] for x in cells_xy[:,1]]
            loni = [np.where(lons==x)[0][0] for x in cells_xy[:,0]]
        except: succeed = False
        
        
        # step: check order of dimensions of the data variable
        dim = fid.variables[varname_data].dimensions
        if dim != (varname_time, varname_lat, varname_lon): succeed = False
                
        # step: extract data from NetCDF dataset and export data into UNF files
        if succeed:
            date_curr = base_date
            
            timei_str, timei_end = 0, 0
            timei_max = len(time)
            while timei_str < timei_max:
                wn, no_of_days = monthrange(date_curr.year, date_curr.month)
                timei_end = timei_end + no_of_days
                
                t = None
                if verbose: 
                    t = datetime.now()
                    print('Extracting data for year-%d month-%d .... '%(date_curr.year, date_curr.month), end='', flush=True)
                data = np.zeros((gg.get_wghm_cell_count(), 31), dtype=np.float32)
                for i in range(len(lati)):
                    d = fid.variables[varname_data][timei_str:timei_end, lati[i], loni[i]]
                    d.fill_value = 0
                    data[i, :no_of_days] = d.filled().astype(np.float32)
                    
                if verbose:
                    t = datetime.now()-t
                    print('success [time required]' + str(t))
                
                # write data into UNF file
                filename_out = '%s_%d_%d.31.UNF0' % (output_filename_prefix, date_curr.year, date_curr.month)
                filename_out = os.path.join(output_directory, filename_out)
                succeed = WGapOutput.write_unf(filename_out, data)
                
                if not succeed: break
                
                timei_str = timei_end
                date_curr = date_curr + relativedelta(months=1)
        
        return succeed