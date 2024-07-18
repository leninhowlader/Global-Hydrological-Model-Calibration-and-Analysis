import os, sys, numpy as np, pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange


try: from netCDF4 import Dataset
except:
    class Dataset:
        def __init__(self): pass

from utilities.globalgrid import GlobalGrid as gg
from utilities.enums import FileEndian

class WaterGapIO:
    __model_homedirectory = 'D:/mhasan/Code&Script/WaterGapGHM/WaterGap_home'
    __model_input_data_directory = os.path.join(__model_homedirectory, 'INPUT')
    
    @staticmethod
    def set_model_home_directory(home_directory): 
        WaterGapIO.__model_homedirectory = home_directory
    
    @staticmethod
    def get_model_home_directory(): return WaterGapIO.__model_homedirectory
    
    @staticmethod
    def set_model_input_data_directory(input_directory):
        WaterGapIO.__model_input_data_directory = input_directory
        
    @staticmethod
    def get_model_input_data_directory(): return WaterGapIO.__model_input_data_directory
    
    @staticmethod
    def read_unf(filename, file_endian=FileEndian.big_endian, ncol=-1):
        '''
        This function read the WaterGAP binary output and returns data into numpy array.

        Parameters:
        :param filename: (string) WaterGAP binary output filename. Filename must follow the WaterGAP standard i.e
                         it should have UNF extension with a digit at the end. The digit could be either
                         one of the followings:
                                0     (indicating that the file contains 4-byte float values)
                                1     (indicating that the file contains 1-byte integer values)
                                2     (indicating that the file contains 2-byte integer values)
                            or  4     (indicating that the file contains 4-byte integer values)
        :param file_endian: (FileEndian Enum) The endianness of the binary file. Value could be 1 i.e. small endian (windows
                         system) or 2 for big endianness (UNIX system)
        :param ncol: (Integer) No of columns each rows must have. Only if ncol > 1, extracted data will be
                         divided into rows and columns; otherwise the fucntion will return 1-d array. If
                         ncol is not provided, the function will try to read the ncol from the filename.
                         ncol is specified by a number appearing in the filename before the file extension
                         with a preceding dot (.) and followed by another usual dot (for extension).
                         Example of WaterGAP file: ground_water_2018.12.UNF0; the file contains ground water
                         information of 2018. Each row contains 12 values (i.e., ncol = 12; it also mean that
                         the file contains monthly values). The values are 4-byte floating point numbers.
        :return: (2-d or 1-d) array depending on ncol value on success;
                  otherwise, an empty array

        Example:
        >>> filename = os.path.join(wgap_output_directory, 'G_TOTAL_STORAGES_km3_2003.12.UNF0')
        >>> tws_2003 = WaterGapIO.read_unf(filename, FileEndian.big_endian, 12)
        >>> tws_2003.shape
        (66740, 12)
        >>> tws_2003 = WaterGapIO.read_unf(filename, ncol=12)
        >>> tws_2003.shape
        (66740, 12)
        >>> tws_2003 = WaterGapIO.read_unf(filename, file_endian=FileEndian.big_endian)
        >>> tws_2003.shape
        (66740, 12)
        >>> tws_2003 = WaterGapIO.read_unf(filename)
        >>> tws_2003.shape
        (66740, 12)
        '''
        d = np.array([])

        # step: check if file exists
        if not os.path.exists(filename): return d

        # step: find the data type in output file mentioned in as the extension of filename
        unf_type = -1
        try: unf_type = int(filename[-1])
        except: pass

        if unf_type not in [0, 1, 2, 4]: return d
        dtype = '>'
        if file_endian == FileEndian.little_endian: dtype = '<'

        if unf_type == 0: dtype += 'f'
        elif unf_type == 1: dtype += 'b'
        elif unf_type == 2: dtype += 'h'
        elif unf_type == 4: dtype += 'i'
        else: return None

        # step: find no. of columns as to data will be reshaped. If ncol is not provided,
        # try to find the ncol from the filename
        if ncol < 1:
            temp = os.path.split(filename)[-1]
            if temp.count('.') >= 2:
                try:
                    ndx1 = temp.find('.') + 1
                    ndx2 = temp[ndx1:].find('.')
                    ncol = int(temp[ndx1:ndx1 + ndx2])
                except: pass
            if ncol < 1: ncol = 1

        # step: read model output file
        d = np.fromfile(filename, dtype=dtype)
        # d = d.byteswap().newbyteorder()              # not working in the new
                                                       # numpy 2.0 version
        
        # step: reshape data if ncol is larger than 1
        if ncol > 1:
            nrow = d.size//ncol
            d = d.reshape(nrow, ncol)

        return d

    @staticmethod
    def write_unf(filename:str, data:np.ndarray, unf_type=0, file_endian:FileEndian=FileEndian.big_endian,
                  append=False):
        '''
        This method writes data into UNF file format.

        :param filename: (string) name of the output file
        :param data: (numpy n-d array) data
        :param unf_type: (int) Integer code for UNF data type. Following data types are valid:
                                0: for 4-byte float
                                1: for 1-byte integer
                                2: for 2-byte integer
                                4: for 4-byte integer
        :param file_endian: (int/FileEndian) File endianness
        :return: (bool) True on success, False otherwise
        '''

        succeed = True

        if unf_type not in [0, 1, 2, 4]:
            try: unf_type = int(filename[-1])
            except: pass

        if unf_type == 0: format_str = 'f'
        elif unf_type == 1: format_str = 'b'
        elif unf_type == 2: format_str = 'h'
        elif unf_type == 4: format_str = 'i'
        else: return False

        if file_endian == FileEndian.little_endian: format_str = '<%s'%format_str
        else: format_str = '>%s'%format_str

        try:
            if append: f = open(filename, 'ab')
            else: f = open(filename, 'wb')
            f.write(data.astype(format_str))
        except: succeed = False

        return succeed

    @staticmethod
    def summarize(data, basin=[], weights=[]):
        if basin and weights and len(weights) != len(basin): return []

        data = np.array(data, dtype=np.float64)

        if basin:
            basin = np.array(basin)-1
            data = data[basin]
            data = np.nan_to_num(data)

        if weights:
            weights = np.array(weights)
            if data.ndim == 1: data = data * weights
            else: data = data * weights[:, None]

            data = np.sum(data, axis=0) / np.sum(weights)
        else: data = np.sum(data, axis=0)

        return data.tolist()

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
        time = fid.variables[varname_time][:]
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
        
        # step: find wghm cell number
        wghm_cnum = []
        for i in range(len(cells_xy)):
            r, c = gg.find_row_column(latitude=cells_xy[i, 1], longitude=cells_xy[i, 0])
            wghm_cnum.append(gg.get_wghm_cell_number(row=r, col=c))
        wghm_cnum = np.array(wghm_cnum, dtype=int) - 1

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

                    cnum = wghm_cnum[i]
                    data[cnum, :no_of_days] = d.filled().astype(np.float32)
                    
                if verbose:
                    t = datetime.now()-t
                    print('success [time required: %s]' % str(t))
                
                # write data into UNF file
                filename_out = '%s_%d_%d.31.UNF0' % (output_filename_prefix, date_curr.year, date_curr.month)
                filename_out = os.path.join(output_directory, filename_out)
                succeed = WaterGapIO.write_unf(filename_out, data)
                
                if not succeed: break
                
                timei_str = timei_end
                date_curr = date_curr + relativedelta(months=1)
        
        return succeed


    @staticmethod
    def read_netcdf(
        filename:str, 
        cells_xy:np.ndarray, 
        varname_data:str, 
        dimname_lon:str= 'lon', 
        dimname_lat:str= 'lat',
        dimname_time='time'
    ):

        d = np.array([])
        if not os.path.exists(filename): return d

        # open dataset
        ds = Dataset(filename, 'r')

        # read data for all dimensions
        times, lats, lons = None, None, None
        try:
            times = ds.variables[dimname_time][:]
            lons = ds.variables[dimname_lon][:]
            lats = ds.variables[dimname_lat][:]
        except: return d

        # create nd-index-array
        xx, yy = np.meshgrid(lons, lats)
        points = np.vstack((xx.flatten(), yy.flatten())).T

        jj = [np.where((x == points).all(axis=1))[0] for x in cells_xy]
        jj = np.array(jj).flatten()
        if len(jj) != len(cells_xy): return d

        nlat, nlon = len(lats), len(lons)

        ii = np.zeros((nlat * nlon), dtype=bool)
        ii[jj] = 1
        ii = ii.reshape(nlat, nlon)

        # extract data
        d = ds.variables[varname_data][:][:, ii]

        return d.data

    @staticmethod
    def generate_lookup_table_GC_GR(outfile, gcfile='GC.UNF2', grfile='GR.UNF2',
                                    inputdirectory='', resolution_deg=0.5):
        if inputdirectory:
            grfile = os.path.join(inputdirectory, grfile)
            gcfile = os.path.join(inputdirectory, gcfile)

        if not (os.path.exists(grfile) and os.path.exists(gcfile)):
            return False

        try:
            cc = WaterGapIO.read_unf(gcfile)
            rr = WaterGapIO.read_unf(grfile)

            if not (cc.shape[0] > 0 and cc.shape == rr.shape): return False
        except: return False

        cc = cc - 1           # 1-based column number to 0-based column index
        rr = rr - 1           # 1-based row number to 0-based row index

        nrow, ncol = int(180 / resolution_deg), int(360 / resolution_deg)
        if cc.max() > ncol - 1: return False
        if rr.max() > nrow - 1: return False

        lons = (cc * resolution_deg) - 180 + (resolution_deg / 2)
        lats = -(rr * resolution_deg) + 90 - (resolution_deg / 2)

        if lons.max() > 180 or lons.min() < -180: return False
        if lats.max() > 90 or lats.min() < -90: return False

        ncells = len(cc)
        cnums = np.arange(1, ncells + 1).reshape(-1, 1)
        lons = lons.reshape(-1, 1)
        lats = lats.reshape(-1, 1)

        d = np.concatenate((cnums, lons, lats), axis=1)

        np.savetxt(outfile, d, fmt='%d,%.2f,%.2f')

        return True

    @staticmethod
    def generate_lookup_table_GCRC(outfile, gcrcfile='GCRC.UNF4', inputdirectory='', resolution_deg=0.5):
        # join model input directory to GCRC filename
        if inputdirectory: gcrcfile = os.path.join(inputdirectory, gcrcfile)

        # if file does not exist, return false
        if not os.path.exists(gcrcfile): return False

        try:
            rc = WaterGapIO.read_unf(gcrcfile)
            nrow, ncol = int(180 / resolution_deg), int(360 / resolution_deg)
            if len(rc) != ncol * nrow: return False
        except: return False

        ii = np.where(rc > 0)[0]        # find indices that contains cell numbers
        oi = np.argsort(rc[ii])         # sort cell number from 1 to the largest
        cc = ii[oi]//360                # calculate column numbers
        rr = ii[oi]%360                 # calculate row numbers

        if cc.max() > ncol - 1: return False
        if rr.max() > nrow - 1: return False

        lons = (cc * resolution_deg) - 180 + (resolution_deg / 2)
        lats = -(rr * resolution_deg) + 90 - (resolution_deg / 2)

        if lons.max() > 180 or lons.min() < -180: return False
        if lats.max() > 90 or lats.min() < -90: return False

        ncells = len(cc)
        cnums = np.arange(1, ncells + 1).reshape(-1, 1)
        lons = lons.reshape(-1, 1)
        lats = lats.reshape(-1, 1)

        d = np.concatenate((cnums, lons, lats), axis=1)

        np.savetxt(outfile, d, fmt='%d,%.2f,%.2f')

        return True

    @staticmethod
    def find_cellnumber_GCRC(lons, lats, 
                             gcrcfile='GCRC.UNF4', 
                             inputdirectory='', 
                             resolution_deg=0.5):
        if lons.shape != lats.shape: return np.empty(0)
        if lons.max() > 180 or lons.min() < -180: return np.empty(0)
        if lats.max() > 90 or lats.min() < -90: return np.empty(0)

        if inputdirectory: gcrcfile = os.path.join(inputdirectory, gcrcfile)
        if not os.path.exists(gcrcfile): return np.empty(0)

        try:
            rc = WaterGapIO.read_unf(gcrcfile)

            nrow, ncol = int(180 / resolution_deg), int(360 / resolution_deg)
            if len(rc) != ncol * nrow: return np.empty(0)
        except: return np.empty(0)

        rr = (np.abs(lats - 90) // resolution_deg).astype(int)
        cc = ((lons + 180) // resolution_deg).astype(int)

        rmax = int(180//resolution_deg)
        ii = np.where(rr==rmax)
        rr[ii] -= 1

        cmax = int(360//resolution_deg)
        ii = np.where(cc==cmax)
        cc[ii] -= 1

        ii = cc * 360 + rr
        return rc[ii]
    
    @staticmethod
    def find_row_col(lons, lats, resolution_deg=0.5):
        if lons.shape != lats.shape: return np.empty(0)
        if lons.max() > 180 or lons.min() < -180: return np.empty(0)
        if lats.max() > 90 or lats.min() < -90: return np.empty(0)
        
        rr = (np.abs(lats - 90) // resolution_deg).astype(int)
        cc = ((lons + 180) // resolution_deg).astype(int)

        rmax = int(180//resolution_deg)
        ii = np.where(rr==rmax)
        rr[ii] -= 1

        cmax = int(360//resolution_deg)
        ii = np.where(cc==cmax)
        cc[ii] -= 1
        
        rr = rr.reshape(-1, 1)
        cc = cc.reshape(-1, 1)
        
        return np.concatenate((rr, cc), axis=1)
    
    @staticmethod
    def compute_land_area_fraction(start_year=-1, end_year=-1):
        '''
        This function compute the initial or year specific land area fraction of 
        total cell area (but not of continental area). If year is given, year 
        specific reservoir fraction will be used in calculation
        
        @param start_year: (int; optional) start year of computation, must be 
                                           greater than 1901
        @param end_year: (int; optional) end year of computation, must be greater
                                         than 1901 and start year. if end year
                                         is provided, land area fraction will be
                                         calculated for all years between start
                                         and end year inclusive of the start and
                                         end year.
        @return : (numpy n-d array) land area fraction between 0.0 and 1.0
        
        
        Theoritical Background:
            
        (Eq-1)
        Land Area Fraction = Continental Area Fraction - (Global Lake Fraction
                   + Global Wetland Fraction + Local Lake Fraction
                   + Local Wetland Fraction + Reservoir Fraction)
        
        (Eq-2)
        Continental Area Fraction = Land Fraction + Freshwater Fraction
        
        Input Files: 
            (Eq-1)
            Global Lake Fraction -> G_GLOLAK.UNF0
            Global Wetland Fraction -> G_GLOWET.UNF0
            Local Lake Fraction -> G_LOCLAK.UNF0
            Local Wetland Fraction -> G_LOCWET.UNF0
            Reservoir Fraction -> G_RES/G_RES_FRAC.UNF0 
                               or G_RES/G_RES_[year].UNF0 in case of variable
                               reserver fraction
            
            (Eq-2)
            Land Fraction -> GFREQ.UNF0
            Freshwater Fraction -> GFREQW.UNF0
        
        Note: all input file contains fraction amount in percentage i.e., values
        between 0 to 100
        
        '''
        
        # step-01: check input file avialability
        input_files = ['G_GLOLAK.UNF0', 'G_GLOWET.UNF0', 'G_LOCLAK.UNF0',
                       'G_LOCWET.UNF0', 'GFREQ.UNF0', 'GFREQW.UNF0']
        
        reservoir_frac_files = []
        if start_year >=1901:
            if end_year > start_year:
                for year in range(start_year, end_year + 1):
                    f = 'G_RES/G_RES_%d.UNF0'%year
                    if not os.path.exists(os.path.join(
                            WaterGapIO.__model_input_data_directory, f)):
                        f = 'G_RES/G_RES_FRAC.UNF0'
                    reservoir_frac_files.append(f)
            else:
                f = 'G_RES/G_RES_%d.UNF0' % start_year
                if not os.path.exists(os.path.join(
                        WaterGapIO.__model_input_data_directory, f)):
                    f = 'G_RES/G_RES_FRAC.UNF0'
                reservoir_frac_files.append(f)
        else: reservoir_frac_files.append('G_RES/G_RES_FRAC.UNF0')
        
        input_files += reservoir_frac_files
        
        input_directory = WaterGapIO.__model_input_data_directory
        for file in input_files: 
            if not os.path.exists(os.path.join(input_directory, file)):
                return np.empty(0)      # unsuccessful
        # end of step
        
        
        # step-02: calculate continental area fraction
        f = os.path.join(input_directory, 'GFREQ.UNF0')
        d1 = WaterGapIO.read_unf(f)          # read land fraction
        
        ncell = len(d1)
        if ncell == 0: return np.empty(0)
        
        f = os.path.join(input_directory, 'GFREQW.UNF0')
        d2 = WaterGapIO.read_unf(f)          # read freshwater fraction
        if len(d2) != ncell: return np.empty(0)
        
        continental_area_frac = d1 + d2
        
        d1, d2 = None, None
        # end of step
        
        # step-03: compute total SWS component fraction
        f = os.path.join(input_directory, 'G_LOCLAK.UNF0')
        sws_com_frac = WaterGapIO.read_unf(f)          # read local lake fraction
        if len(sws_com_frac) != ncell: return np.empty(0)
        
        f = os.path.join(input_directory, 'G_GLOLAK.UNF0')
        d = WaterGapIO.read_unf(f)          # read global lake fraction
        if len(d) != ncell: return np.empty(0)
        sws_com_frac = sws_com_frac + d
        
        f = os.path.join(input_directory, 'G_LOCWET.UNF0')
        d = WaterGapIO.read_unf(f)          # read local wetland fraction
        if len(d) != ncell: return np.empty(0)
        sws_com_frac = sws_com_frac + d
        
        f = os.path.join(input_directory, 'G_GLOWET.UNF0')
        d = WaterGapIO.read_unf(f)          # read global wetland fraction
        if len(d) != ncell: return np.empty(0)
        sws_com_frac = sws_com_frac + d
        
        sws_frac_years = None
        for f in reservoir_frac_files:
            f = os.path.join(input_directory, f)
            d = WaterGapIO.read_unf(f)          # read reservoir fraction
            if len(d) != ncell: return np.empty(0)
            
            temp = (sws_com_frac + d).reshape(-1, 1)
            
            try: sws_frac_years = np.concatenate((sws_frac_years, temp), axis=1)
            except: sws_frac_years = temp
        
        #print(reservoir_frac_files)
        # end of step
        
        # step-04: compute land area fraction
        land_area_frac_years = None
        for j in range(sws_frac_years.shape[1]):
            sws_com_frac = sws_frac_years[:,j]
            
            land_area_frac = continental_area_frac - sws_com_frac
            
            ii = np.where(land_area_frac < 0)
            land_area_frac[ii] = 0
            
            ii = np.where(land_area_frac > 100)
            land_area_frac[ii] = 100
            
            land_area_frac = land_area_frac.reshape(-1, 1)
            try: 
                land_area_frac_years = np.concatenate((land_area_frac_years, 
                                                        land_area_frac), axis=1)
            except: land_area_frac_years = land_area_frac
        # end of step
        
        return land_area_frac_years/100
    
    @staticmethod
    def compute_continental_area_fraction():
        '''
        This function computes continental areal fraction (values between 0.0 
        and 1.0) as the sum of land area fraction and freshwater area fraction.
        
        @return: (numpy 1-d array) continal area fraction
        '''
        
        # step-01: check wheather required data files exist or not
        input_path = WaterGapIO.__model_input_data_directory
        if not (os.path.exists(os.path.join(input_path, 'GFREQ.UNF0')) and 
                os.path.exists(os.path.join(input_path, 'GFREQW.UNF0'))):
            return np.empty(0)
        
        # step-02: calculate continental area fraction
        f = os.path.join(input_path, 'GFREQ.UNF0')
        d1 = WaterGapIO.read_unf(f)          # read land fraction
        
        ncell = len(d1)
        if ncell == 0: return np.empty(0)
        
        f = os.path.join(input_path, 'GFREQW.UNF0')
        d2 = WaterGapIO.read_unf(f)          # read freshwater fraction
        if len(d2) != ncell: return np.empty(0)
        
        continental_area_frac = d1 + d2
        # end of step
        
        return continental_area_frac/100

    
    
    class Precipitation:
        from collections import OrderedDict
        
        
        __forcing_data_directory = ''
        
        @staticmethod
        def set_forcing_data_directory(d):
            WaterGapIO.Precipitation.__forcing_data_directory = d
        
        @staticmethod
        def get_forcing_data_directory():
            return WaterGapIO.Precipitation.__forcing_data_directory
        
        @staticmethod
        def weighted_sum(data31, weights): 
            return (data31 * weights).sum(axis=0)
        
        @staticmethod
        def weighted_mean(data31, weights):
            return (data31 * weights).sum(axis=0) / weights.sum()
        
        @staticmethod
        def read_basin_precipitation_total(start_year:int, 
                              end_year:int, 
                              basin_info:OrderedDict,
                              filename_out=''):
            
            # step: check input
            e = np.empty(0)
            
            input_directory = WaterGapIO.Precipitation.__forcing_data_directory
            if not input_directory or not os.path.exists(input_directory):
                return e
            
            if start_year < 1901 or end_year < 1901 or start_year > end_year:
                return e
            
            if not basin_info: return e
            
            for basin in basin_info.keys():
                if 'upstream' not in basin_info[basin].keys(): return e
                if len(basin_info[basin]['upstream']) == 0: return e
                if 'area' not in basin_info[basin].keys(): return e
                if (len(basin_info[basin]['upstream']) !=
                    len(basin_info[basin]['area'])): return e
            # end of step
            
            # step: computing basin cell indices from cell numbers and reshaping
            # areas as necessary for the next step
            for basin in basin_info.keys():
                cellnum = np.array(basin_info[basin]['upstream'])
                cellindex = cellnum - 1
                
                basin_info[basin]['cellindex'] = cellindex
                area = np.array(basin_info[basin]['area']).reshape(-1, 1)
                basin_info[basin]['area'] = area
            # end of step
            
            # step: read daily precipitation data (from GPREC_YYYY_MM.31.UNF0)
            #       (each file contains 31 daily values in 31 columns for all
            #       model cells in rows. the values are precipitation amounts in
            #       mm/day)
            fun = WaterGapIO.Precipitation.weighted_sum
            
            records = {'year': [], 'month': []}
            for basin in basin_info.keys(): records[basin] = []
            
            for year in range(start_year, end_year + 1):
                records['year'] += [year] * 12
                records['month'] += list(range(1, 12+1))
                
                for month in range(1, 12 + 1):
                    f = os.path.join(input_directory,
                                     'GPREC_%d_%d.31.UNF0'%(year, month))
                    d = WaterGapIO.read_unf(f)
                    if d.shape[0] == 0: return e
                    
                    for basin in basin_info.keys():
                        cellindex = basin_info[basin]['cellindex']
                        
                        data31 = d[cellindex]
                        weights = basin_info[basin]['area']
                        
                        records[basin].append(fun(data31, weights).sum())
            # end of step
            
            # step: apply unit conversion
            unit_conversion_factor = 10**-6    # mm*km2 to km3
            
            for basin in basin_info.keys():
                d = np.array(records[basin]) * unit_conversion_factor
                records[basin] = d
            # end of step
            
            
            # step: create dataframe and save data if necessary       
            df = pd.DataFrame(records)
            if filename_out: 
                df.to_csv(filename_out, index=False)
                return None
            # end of step
            
            return df


