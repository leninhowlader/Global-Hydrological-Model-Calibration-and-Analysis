import os, sys, numpy as np
from netCDF4 import Dataset

from utilities.globalgrid import GlobalGrid
# from wgap.wgapio import WaterGapIO

class EvapoTranspiration:
    @staticmethod
    def read_LandFluxEVAL_dataset(
            data_filename:str,
            waterGap_cells:np.ndarray,
            output_filename: str='',
            stat_name:str='ET_mean',
            compute_basin_average:bool=True,
            compute_monthly_ET:bool=True):
        '''
        This method reads LandFluxEVAL merged ET data product (Mueller et al.,
        2013) for given WaterGAP cells.

        :param data_filename: (string) filename of LandFluxEVAL data product
        :param waterGap_cells: (numpy 1-d array or 1-d list) List of WaterGAP
                        cell numbers [within a single basin]
        :param output_filename: (string; optional) output filename
        :param stat_name: (string) name of the statistics to be used from the
                        data product. data contains mean as 'ET_mean', median as
                        'ET_median', inter quartile range as 'ET_IQR', first
                        quartile as 'ET_25', third quartile as 'ET_75', minimum
                        as 'ET_min', maximum as 'ET_max' and standard deviation
                        as 'ET_sd' of available ET products for a given 1-deg
                        cell. (optional; default is 'ET_mean')
        :param compute_basin_average: (bool; optional; default = True) flag that
                        determines whether or not the basin average needs to be
                        computed
        :return: (bool) 'True' on success; 'False' otherwise.
        '''
        
        
        # step: check inputs
        if not (data_filename and os.path.exists(data_filename) and
                len(waterGap_cells)):
            return np.empty(0)

        if stat_name not in ['ET_mean', 'ET_median', 'ET_IQR', 'ET_25',
                             'ET_75', 'ET_min', 'ET_max', 'ET_sd']:
            return np.empty(0)
        # end of step

        # step: read ET data from NetCDF data file
        cellnum = np.array(waterGap_cells)
        lonlat = GlobalGrid.wghm_cellnumber_to_centroid_lonlat(cellnum)
        lonlat_1deg = GlobalGrid.nearest_centroid_ndarray(
                                    lonlat,
                                    degree_resolution=1.0)
        
        lonlat_1deg_unique = np.unique(lonlat_1deg, axis=0)
        
#        d = WaterGapIO.read_netcdf(
#                filename=data_filename,
#                cells_xy=lonlat_1deg_unique,
#                varname_data=stat_name,
#                dimname_lon='lon',
#                dimname_lat='lat',
#                dimname_time='time')
#        
        fid = Dataset(data_filename, 'r')
        time = fid.variables['time'][:]
        lats = fid.variables['lat'][:]
        lons = fid.variables['lon'][:]
        et = fid.variables[stat_name][:]
        
        d = np.empty(0)
        for i in range(len(lonlat_1deg_unique)):
            ndx_long = np.where(lons==lonlat_1deg_unique[i][0])
            ndx_lat = np.where(lats==lonlat_1deg_unique[i][1])
            temp =np.array(et[:, ndx_lat[0], ndx_long[0]])
            try: d = np.concatenate((d, temp), axis=1)
            except: d = temp
        fid.close()
        
        # map 1 deg cell to 0.5 deg WaterGAP cell
        ll = lonlat_1deg_unique
        ii = [np.where((ll[:,0]==x[0]) & (ll[:,1]==x[1]))[0][0] 
              for x in lonlat_1deg]
        d = d[:, ii]
        
        # remove null values [if exists]
        ii = np.where(d==-9999)
        d[ii] = 0
        # end of step
        
        # step: read time from NetCDF data file
        fid = Dataset(data_filename, 'r')
        time = fid.variables['time'][:]
        fid.close()
        # end of step
        
        # step: compute basin average
        if compute_basin_average:
            rc = GlobalGrid.find_rowcol_ndarray(lonlat[:,0], lonlat[:,1])
            a = GlobalGrid.find_wghm_cellarea_ndarray(rc[:,0])
            d = ((d * a).sum(axis=1)/a.sum()).reshape(-1, 1)
            
        # end of step
        
        # step: identify year and month info
        yr = np.array(time//100, dtype=int).reshape(-1, 1)
        mn = np.array(time%100, dtype=int).reshape(-1, 1)
        
        d = np.concatenate((yr, mn, d), axis=1)
        # end of step
        
        # step: compute monthly ET
        if compute_monthly_ET:
            from calendar import monthrange
            
            def days_in_month(yr, mn):
                days = [monthrange(yr[i], mn[i])[1] for i in range(len(yr))]
                return np.array(days)
            
            days = days_in_month(yr.flatten(), mn.flatten()).reshape(-1, 1)
            d[:,2:] = d[:, 2:] * days
        # end of step
        
        # step: save records into file
        if output_filename: 
            fmt = '%d,%d,' + '%f' * (d.shape[1] - 2)
            np.savetxt(output_filename, d, fmt=fmt)
        # end of step
        
        return d

