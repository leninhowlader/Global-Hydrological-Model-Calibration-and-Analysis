# Author: H.M. Mehedi Hasan
# Date: April, 2016

# The grid class provides supplementary functions for mapping WGHM 0.5-degree 
# cells to absolute geo-corrdinates, grouping WGHM cells according to 
# GRACE 1-degree cell, finding cell centroids, finding grid row and column for 
# specific cell and transforming row and columns between two spatial
# resolutions.
#
# For mapping WGHM cells to geo-coordinates of the cell centroid, mapping data 
# must be provided into 'wghm_grid.csv' file. wghm_grid.csv contains WGHM cell 
# numbers, corresponding ArcIds, and longitudes and latitudes of the centroids 
# of the corresponding WGHM cells.
#
# The grid class is static in nature and thus, all functions and variables are 
# static.
#
# In this class the geo-locations are plotted on an imaginary grid situated 
# within -180 to 180 degree longitude and within 90 to -90 degree latitude. The
# number of rows and columns of the imaginary grid depends on the
# grid-resolution. In order to find the reference cell number of a geo-location 
# within a grid with specified resolution, one has to find the corresponding 
# row and column numbers. Cell reference number within the imaginary grid is 
# different than that of WGHM grid. In the imaginary grid the cell number starts
# from zero at the left-top corner of the grid (-180 degree  longitude, 
# 90 degree latitude) and increases first from left to right and then top to 
# bottom. However, most of function works with row and column number.

__author__ = 'mhasan'

import os, numpy as np

try: import pandas as pd
except:
    # this garbage code block is necessary to load this module in absence 
    # of pandas
    class pd: 
        DataFrame = None
# end of try


class GlobalGrid:

    # wghm grid variables
    __wghm_version = 'wghm22d'
    __wghm_cell_areas = []
    __wghm_cell_area_file = 'data/GAREA.UNF0'
    __wghm_grid_lookup_table = np.array([])
    __wghm_grid_lookup_table_filename = 'data/grid_wghm22d.txt'
    __grid_resolution = 0.5     # grid resolution in degrees

    @staticmethod
    def get_grid_resolution(): return GlobalGrid.__grid_resolution

    @staticmethod
    def set_grid_resolution(resolution_deg): 
        GlobalGrid.__grid_resolution = resolution_deg

    @staticmethod
    def get_current_model_version():
        '''
        Returns WGHM model version name

        :return: (string) WGHM model version
        '''
        return GlobalGrid.__wghm_version

    @staticmethod
    def set_model_version(model_version):
        '''
        This method sets WGHM model version

        :param model_version: (string) WGHM version. parameter value should be 
                        either 'wghm22b' or 'wghm22d'
        :return: None
        '''

        if model_version != GlobalGrid.__wghm_version:
            GlobalGrid.__wghm_version = model_version
            GlobalGrid.__wghm_grid_lookup_table = np.array([])
            
            GlobalGrid.__wghm_grid_lookup_table_filename \
            = 'data/grid_%s.txt' % model_version
            
            GlobalGrid.read_wghm_grid_lookup_table()

    @staticmethod
    def set_wghm_grid_lookup_table_filename(filename):
        '''
        This method sets WGHM grid lookup table filename

        :param filename: (string) filename
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True

        if os.path.exists(os.path.join(os.path.dirname(__file__), filename)):
            GlobalGrid.__wghm_grid_lookup_table = np.array([])
            GlobalGrid.__wghm_grid_lookup_table_filename = filename
        else: succeed = False

        return succeed
    
    @staticmethod
    def get_wghm_cell_count():
        '''
        This method calculates total number of WGHM cells

        :return: (int) total number of WGHM cells in current model version
        '''

        if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
            GlobalGrid.read_wghm_grid_lookup_table()
        
        return len(GlobalGrid.__wghm_grid_lookup_table)
    
    @staticmethod
    def get_wghm_cell_area_file():
        '''
        This method returns cell area filename

        :return: (string) cell area filename
        '''
        return os.path.join(os.path.dirname(__file__), 
                            GlobalGrid.__wghm_cell_area_file)

    @staticmethod
    def get_wghm_grid_lookup_table_filename():
        '''
        Returns WGHM grid lookup table filename

        :return: (string) WGHM grid lookup table filename
        '''
        return os.path.join(os.path.dirname(__file__),
                            GlobalGrid.__wghm_grid_lookup_table_filename)

    @staticmethod
    def find_wghm_cellarea(row, base_resolution=0.5):
        if not GlobalGrid.__wghm_cell_areas: GlobalGrid.read_wghm_cell_area()

        if base_resolution != 0.5: 
            row = GlobalGrid.transform_row_number(row, base_resolution, 0.5)

        if GlobalGrid.__wghm_cell_areas and 0<=row<=359: 
            return GlobalGrid.__wghm_cell_areas[row]
        else: return None

    @staticmethod
    def find_wghm_cellarea_ndarray(rows:np.ndarray):
        if not GlobalGrid.__wghm_cell_areas: GlobalGrid.read_wghm_cell_area()

        return np.array(GlobalGrid.__wghm_cell_areas)[rows]
    
    @staticmethod
    def get_wghm_cell_info(*cellnums):
        '''
        This method returns information of a subset of the WGHM cells.

        :param cellnums: (int/list/numpy ndarray) cell number or cell number list
        :return: (numpy ndarray) cell information of interested WGHM cells
        '''
        if cellnums:
            ndx = np.array([cellnums], dtype=np.int32).flatten() - 1
            if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
                GlobalGrid.read_wghm_grid_lookup_table()
            return GlobalGrid.__wghm_grid_lookup_table[ndx,:]
        else: return np.array([])
        
    @staticmethod
    def get_wghm_grid_info():
        '''
        This method returns the entire (lookup) table of all cell info
        '''
        if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
            GlobalGrid.read_wghm_grid_lookup_table()
        return GlobalGrid.__wghm_grid_lookup_table.copy()

    @staticmethod
    def get_wghm_grid_rowcolumn():
        if len(GlobalGrid.__wghm_grid_lookup_table) == 0:
            GlobalGrid.read_wghm_grid_lookup_table()

        ndx = np.argsort(GlobalGrid.__wghm_grid_lookup_table[:,0])
        coords = GlobalGrid.__wghm_grid_lookup_table[ndx][:,[2,3]]

        rowcol = [GlobalGrid.find_row_column(lat, lon) for lon, lat in coords]
        return np.array(rowcol)


    @staticmethod
    def get_wghm_world_grid_centroids():
        '''
        Returns all WGHM cell centroids of the current model version.

        :return: (np.ndarray) all WGHM cell centroids. the first column 
                        contains latitudes and second contains longitude
        '''
        centriods = []

        if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
            GlobalGrid.read_wghm_grid_lookup_table()

        centriods = GlobalGrid.__wghm_grid_lookup_table[:, [3, 2]]
        # Note that the first column is latitude and the second column 
        # is longitude

        return centriods

    @staticmethod
    def read_wghm_cell_area():
        '''
        This method reads the area for each 0.5 degree WGHM grid cell from UNF 
        binary file
        
        :return: None
        '''
        GlobalGrid.__wghm_cell_areas = []

        fmt = '>f'
        d = np.array([])
        try: d = np.fromfile(GlobalGrid.get_wghm_cell_area_file(), dtype=fmt)
        except: pass

        if len(d) == 360: GlobalGrid.__wghm_cell_areas = d.tolist()

    @staticmethod
    def read_wghm_grid_lookup_table():
        '''
        This method reads lookup table from file. The lookup table contains 
        following columns: 'Cell Number', 'Arc ID', 'Longitude', 'Latitude'

        :return: None
        '''
        d = np.array([])
        try:
            filename = GlobalGrid.get_wghm_grid_lookup_table_filename()
            d = np.loadtxt(filename, delimiter=',', skiprows=1)
        except: pass

        GlobalGrid.__wghm_grid_lookup_table = d

    @staticmethod
    def get_wghm_cell_number(row, col, base_resolution=0.5):
        '''
        The method find WGHM cell number for a given cell

        :param row: (int) row index
        :param col: (int) column index
        :param base_resolution: (float, optional, default = 0.5) resolution of the grid
        :return: (int) WGHM cell number
        '''
        if len(GlobalGrid.__wghm_grid_lookup_table) == 0: GlobalGrid.read_wghm_grid_lookup_table()

        #if row and col is based on other than 0.5-degree grid, transform row and col in 0.5-degree grid row and col
        if base_resolution != 0.5:
            row, col = GlobalGrid.transform_row_column(row, col, base_resolution, 0.5)

        #calculate the cen centroid
        y, x = GlobalGrid.find_centroid(row, col, 0.5)

        #find wghm cell number using geo-coordinates of the centriod
        d = GlobalGrid.__wghm_grid_lookup_table

        ndx = np.where((d[:,2]==x)&(d[:,3]==y))[0]

        return int(d[ndx, 0][0])

    @staticmethod
    def lonlat_to_wghm_cellnumber(lonlat:np.ndarray):
        if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
            GlobalGrid.read_wghm_grid_lookup_table()
            
        d = GlobalGrid.__wghm_grid_lookup_table

        ndx = [np.where((x[0]==d[:,2]) & (x[1]==d[:,3]))[0][0] for x in lonlat]

        return GlobalGrid.__wghm_grid_lookup_table[ndx, 0]
    
    @staticmethod
    def wghm_cellnumber_to_centroid_lonlat(cellnum:np.ndarray):
        if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
            GlobalGrid.read_wghm_grid_lookup_table()
        
        d = GlobalGrid.__wghm_grid_lookup_table

        ndx = [np.where(d[:,0]==x)[0][0] for x in cellnum]
        
        lonlat = d[np.array(ndx)][:, [2, 3]]
                
        return lonlat
    
    @staticmethod
    def get_wghm_centroid(cell_number:int):
        '''
        This function maps WGHM cell centroid using WGHM cell number.

        :param cell_number: (int) WGHM cell number
        :return: (tuple of float) Geo-coordinate of corresponding WGHM cell.
        '''
        if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
            GlobalGrid.read_wghm_grid_lookup_table()

        d = GlobalGrid.__wghm_grid_lookup_table
        ndx = np.where(d[:,0] == cell_number)[0]

        lon, lat = d[ndx, [2,3]].astype(np.float32)

        return lat, lon

    @staticmethod
    def nearest_centroid_longitude(longitude:float, degree_resolution:float=0.5):
        '''
        This method finds longitude of the nearest cell centroid.

        :param longitude: (float) longitude
        :param degree_resolution: (float, optional, default = 0.5) resolution of the grid in decimal degrees
        :return: (float) longitude of the nearest centroid
        '''

        lon = ((180 + longitude) // degree_resolution) * degree_resolution + float(degree_resolution) / 2 - 180

        if lon > 180: return (lon - 360)
        else: return lon

    @staticmethod
    def nearest_centroid_latitude(latitude:float, degree_resolution:float=0.5):
        '''
        This method finds latitude of the nearest cell centroid.

        :param latitude: (float) latitude
        :param degree_resolution: (float, optional, default = 0.5) resolution of the grid in decimal degrees
        :return: (float) latitude of the nearest centroid
        '''

        lat = ((90 + latitude) // degree_resolution) * degree_resolution + float(degree_resolution) / 2 - 90

        if lat > 90: return lat - degree_resolution
        else: return lat

    @staticmethod
    def nearest_centroid(latitude:float, longitude:float, degree_resolution:float=0.5):
        '''
        This method finds the nearest cell centroid.

        :param latitude: (float) latitude
        :param longitude: (float) longitude
        :param degree_resolution:  (float, optional, default = 0.5) resolution of the grid in decimal degrees
        :return: (tuple of float) nearest cell centroid as latitude, longitude pair
        '''
        lat, lon = None, None

        if -180 <= longitude <= 180 and -90 <= latitude <= 90:
            lat = GlobalGrid.nearest_centroid_latitude(latitude, degree_resolution)
            lon = GlobalGrid.nearest_centroid_longitude(longitude, degree_resolution)

        return lat, lon

    @staticmethod
    def nearest_centroid_ndarray(
            lonlat:np.ndarray,
            degree_resolution:float=0.5):
        lon, lat = lonlat[:, 0], lonlat[:, 1]
        lon = (((180 + lon) // degree_resolution) * degree_resolution
               + float(degree_resolution) / 2 - 180)
        ii = np.where(lon > 180)
        lon[ii] = lon[ii] - 360

        lat = (((90 + lat) // degree_resolution) * degree_resolution
               + float(degree_resolution) / 2 - 90)
        ii = np.where(lat > 90)
        lat[ii] = lat[ii] - degree_resolution

        return np.concatenate((lon.reshape(-1, 1), lat.reshape(-1, 1)), axis=1)

    @staticmethod
    def find_column_number(longitude, degree_resolution=0.5):
        '''
        This method finds column number of a given longitude in a specified global grid.

        Parameters:
        :param longtude: (float) longitude of given location
        :param degree_resolution:  (float; optional; default value = 0.05) resolution (in degree) of the global grid.

        Returns:
        :return: (integer) column number in a specified global grid if input longitude is within possible range;
                           None otherwise

        Examples:
        >>> GlobalGrid.find_column_number(90.5)
        541
        >>> GlobalGrid.find_column_number(90.493)
        540
        >>> GlobalGrid.find_column_number(90.5, degree_resolution=1.0)
        270
        >>> GlobalGrid.find_column_number(90.5, degree_resolution=2.0)
        135

        '''

        if -180<=longitude<=180:
            if longitude == 180: return int(((longitude+180)//degree_resolution)-1)
            else: return int((longitude+180)//degree_resolution)
        else: return None

    @staticmethod
    def find_row_number(latitude, degree_resolution=0.5):
        '''
        This method finds row number of a given location in a specified global grid.

        Parameters:
        :param latitude: (float) latitude of given location
        :param degree_resolution:  (float; optional; default value = 0.05) resolution of the grid in decimal degrees.

        Returns:
        :return: (integer) row number in the specified global grid if input latitude is within possible range;
                           None otherwise.

        Examples:
        >>> GlobalGrid.find_row_number(28.35)
        123
        >>> GlobalGrid.find_row_number(28.2435)
        123
        >>> GlobalGrid.find_row_number(28.2435, degree_resolution=0.25)
        247
        >>> GlobalGrid.find_row_number(28.24, degree_resolution=2.0)
        30
        >>> GlobalGrid.find_row_number(28.24, degree_resolution=5.0)
        12

        '''

        if -90 <= latitude <= 90:
            if latitude == -90: return int((abs(latitude-90) // degree_resolution) - 1)
            else: return int(abs(latitude - 90) // degree_resolution)
        else: return None

    @staticmethod
    def find_row_column(latitude:float, longitude:float, degree_resolution:float=0.5):
        '''
        The method finds row and column number of a given location in a specified global grid

        Parameters:
        :param latitude: (float) latitude of given location
        :param longitude: (float) longitude of given location
        :param degree_resolution:  (float; optional; default value = 0.05) resolution of the grid in decimal degrees.

        Returns:
        :return: (int, int) a tuple of row and column number

        Examples:
        >>> GlobalGrid.find_row_column(28.35, 50.49)
        (123, 460)
        >>> GlobalGrid.find_row_column(28.35, 50.49, degree_resolution=1.0)
        (61, 230)
        '''

        return GlobalGrid.find_row_number(latitude, degree_resolution), GlobalGrid.find_column_number(longitude, degree_resolution)

    @staticmethod
    def find_rowcol_ndarray(lons, lats, resolution_deg=0.5):
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
    def transform_column_number(column_number:int, resolution_from:float, resolution_to:float):
        '''
        This method transforms column number (or index) of a cell from source grid to column index in target grid (with
        different resolution)

        :param column_number: (int) column number (i.e., index) of a target cell
        :param resolution_from: (float) resolution of the source grid in decimal degrees
        :param resolution_to: (float) resolution of the target grid in decimal degrees
        :return: (int) column index of the given cell in target grid

        '''
        try:
            if column_number >= 0 and resolution_from >= 0 and resolution_to >= 0:
                return GlobalGrid.find_column_number(column_number * resolution_from - 180, resolution_to)
            else: return None
        except: return None

    @staticmethod
    def transform_row_number(row_number, resolution_from, resolution_to):
        '''
        This method transforms row number (or index) of a cell from source grid to row index in target grid (with
        different resolution)

        :param row_number: (int) row number (i.e., index) of a given cell
        :param resolution_from: (float) resolution of the source grid in decimal degrees
        :param resolution_to: (float) resolution of the target grid in decimal degrees
        :return: (int) row index of the given cell in target grid
        '''
        try:
            if row_number >= 0 and resolution_from >= 0 and resolution_to >= 0:
                return GlobalGrid.find_row_number(-(row_number * resolution_from) + 90, resolution_to)
            else: return None
        except: return None

    @staticmethod
    def transform_row_column(row, column, base_resolution, target_resolution):
        '''
        This method transforms row and column index of a cell in source/original grid to row and column index in another
        grid with different resolution

        Parameters:
        :param row: (int) row index of a given cell
        :param column: (int) column index of a given cell
        :param base_resolution: (float) resolution of the source grid in decimal degrees
        :param target_resolution: (float) resolution of the target grid in decimal degrees

        Returns:
        :return: (int, int) row and column index in the new gird
        '''

        return GlobalGrid.transform_row_number(row, base_resolution, target_resolution), GlobalGrid.transform_column_number(column, base_resolution, target_resolution)

    @staticmethod
    def find_centroid(row, column, deg_resolution=0.5):
        '''
        This method finds geo-coordinates of a given cell centroid

        Parameters:
        :param row: (int) row number of a given cell
        :param column: (int) column number of the given cell
        :param deg_resolution: (float; optional; default value = 0.05) resolution (in degree) of the global grid.

        Returns
        :return: (float, float) a tuple of latitude and longitude of cell centroid

        Examples:
        >>> GlobalGrid.find_centroid(20, 130)
        (79.75, -114.75)
        >>> GlobalGrid.find_centroid(20, 130, 1.0)
        (69.5, -49.5)
        >>> GlobalGrid.find_centroid(20, 130, 2.0)
        (49.0, 81.0)
        '''

        longitude = (column * deg_resolution) - 180 + (deg_resolution / 2)
        latitude = -(row * deg_resolution) + 90 - (deg_resolution / 2)

        if -90 <= latitude <= 90 and -180 <= longitude <= 180: return latitude, longitude
        else: return None, None

    # method for grouping grid cells based on a different resolution grid
    @staticmethod
    def cell_grouping(cell_list, base_resolution=0.5, target_resolution=1.0):
        if target_resolution > base_resolution and target_resolution%base_resolution==0.0:
            cell_count = len(cell_list)
            truth = [False]*cell_count

            transformed_cells= []
            for cell in cell_list: transformed_cells.append(GlobalGrid.transform_row_column(cell[0], cell[1], base_resolution, target_resolution))

            result = []
            i = 0
            max_child_cells = int((target_resolution//base_resolution)**2)
            while i < (cell_count - 1):
                temp = []

                if truth[i]:
                    for j in range(i+1, cell_count):
                        if not truth[j]:
                            i = j
                            temp.append(cell_list[i])
                            truth[i] = True
                            break
                else:
                    temp.append(cell_list[i])
                    truth[i] = True

                if temp:
                    for j in range(i+1, cell_count):
                        if transformed_cells[i] == transformed_cells[j]:
                            temp.append(cell_list[j])
                            truth[j] = True
                        if len(temp) == max_child_cells: break

                    result.append(temp)

                i += 1

            return result
        else: return None

    @staticmethod
    def write_cell_info(filename, array, mode='w', format_str=''):
        '''
        Writes cell info (i.e., cell number or cell area) into output file.

        :param filename: (string) output filename
        :param array: (list of list) input information array
        :param mode: (string) fileopen mode, e.g., 'w', 'a' etc
        :param format_str: (string) format to be used during string convertion.
                            if format string is not provided, str() function 
                            will be used for string convertion. if wrong format
                            is provided, '{:.15f}' will be used as format
        :return: True on success, False otherwise
        '''

        f = None
        try:
            f = open(filename, mode)
            str_list = []
            if not format_str:
                for item in array: str_list.append('[' + ','.join(str(x) 
                                                    for x in item) + ']')
            else:
                # [check] whether or not format string can correctly produce a string
                succeed = False
                try:
                    if float(format_str.format(1)) == 1: succeed = True
                except: pass
                
                if not succeed: format_str = '{:.15f}'
                # end [check]
                
                for item in array: str_list.append(
                    '[' + ','.join(format_str.format(x) for x in item) + ']')
                
            f.write(', '.join(str_list))
        except: return False
        finally:
            try: f.close()
            except: pass

        return True

    @staticmethod
    def read_cell_info(filename, data_type=int):
        '''
        Reads cell information from file.

        :param filename: (string) Name of the file
        :param data_type: (data type) Data type e.g., int or float.
        :return: (list of list) cell information array
        '''

        records = []    #array of arrays (list of groups)

        f = None
        try:
            line_txt = ''
            f = open(filename, 'r')
            for line in f.readlines(): line_txt += line
            temp = line_txt.split(']')

            for i in range(len(temp)):
                temp[i] = temp[i].strip().strip(',').strip().strip('[')
                if temp[i]:
                    group_items = temp[i].split(',')

                    if data_type == int:
                        for j in reversed(range(len(group_items))):
                            try: group_items[j] = int(group_items[j])
                            except: group_items.pop(j)
                    else:
                        for j in reversed(range(len(group_items))):
                            try: group_items[j] = float(group_items[j])
                            except: group_items.pop(j)
                    if group_items: records.append(group_items)
        except: return []
        finally:
            try: f.close()
            except: pass

        return records

    @staticmethod
    def cell_vertices(centroids, degree_resolution=0.5):
        '''
        This method finds the vertices of a given cell. Cell vertices are used 
        for drawing the cell.

        Parameters:
        :param centroids: (list of tuples of latitude and longitude) cell 
                        centroids of target cells
        :param degree_resolution: (float; optional; default value = 0.05) 
                        resolution (in degree) of the global grid.

        Returns:
        :return: (list of list) list of cell vertices of each input cell.

        Examples:
        >>> GlobalGrid.cell_vertices([(49.0, 81.0)])
        [[[80.75, 48.75], [80.75, 49.25], [81.25, 49.25], [81.25, 48.75], 
        [80.75, 48.75]]]
        >>> GlobalGrid.cell_vertices(centroids=[(49.0, 81.0)], 
                                    degree_resolution=2.0)
        [[[80.0, 48.0], [80.0, 50.0], [82.0, 50.0], [82.0, 48.0], [80.0, 48.0]]]
        '''

        points = []

        try:
            dist = degree_resolution/2
            for centroid in centroids:
                y1, y2 = (centroid[0] - dist), (centroid[0] + dist)
                x1, x2 = (centroid[1] - dist), (centroid[1] + dist)
                points.append([[x1, y1], [x1, y2], [x2, y2], [x2, y1], [x1, y1]])
        except: return None

        return points
    
    @staticmethod
    def compute_vertices_ndarray(lons:np.ndarray, 
                              lats:np.ndarray, 
                              resolution_deg=0.5):
        
        # step: check inputs
        if lons.shape[0] == 0 or lons.shape[0] != lats.shape[0]:
            return np.empty(0)
        if resolution_deg <= 0: return np.empty(0)
        # end of step
        
        # step: compute lat and lon of vertices
        dist = resolution_deg/2
        
        x1 = (lons - dist).reshape(-1, 1, 1)
        x2 = (lons + dist).reshape(-1, 1, 1)
        
        y1 = (lats - dist).reshape(-1, 1, 1)
        y2 = (lats + dist).reshape(-1, 1, 1)
        # end of step
        
        # step: create vertices
        vertex1 = np.concatenate((x1, y1), axis=2)
        vertex2 = np.concatenate((x1, y2), axis=2)
        vertex3 = np.concatenate((x2, y2), axis=2)
        vertex4 = np.concatenate((x2, y1), axis=2)
        vertex5 = np.concatenate((x1, y1), axis=2)
        
        vertices = np.concatenate((vertex1, vertex2, vertex3, vertex4, vertex5),
                                  axis=1)
        # end of step
        
        return vertices
    
    @staticmethod
    def create_shapefile_df(dataframe:pd.DataFrame, 
                            filename:str,
                            resolution_deg:float=0.5,
                            fields:list=[],
                            prj_string:str=''):
        
        # inner function to generate fields
        def generate_field_info(df:pd.DataFrame):
            fields = []
            
            for i in range(df.shape[1]):
                f = [df.columns[i]]
                
                onevalue = df.iloc[0, i]
                
                if type(onevalue) in [np.int, np.int32, int]:
                    f += ['N', 15]
                elif type(onevalue) in [np.int64]:
                    f += ['N', 30]
                elif type(onevalue) is np.float64:
                    f += ['N', 50, 15]
                elif type(onevalue) in [np.float, np.float32, float]:
                    f += ['N', 22, 8]
                #elif type(onevalue) is np.datetime64:
                #    f += ['N', 22, 8]
                else: f += ['C', 50]
                
                fields.append(f)
            
            return fields
        # end of inner function
        
        
        # step: find longitude and latitude information
        columns = list(dataframe.columns)
        for i in range(len(columns)): columns[i] = columns[i].lower()
        
        lons, lats = None, None
        if 'lon' in columns:
            ic = columns.index('lon')
            lons = dataframe.iloc[:,ic].values
        elif 'longitude' in columns: 
            ic = columns.index('longitude')
            lons = dataframe.iloc[:,ic].values
        else: return False
            
        if 'lat' in columns:
            ic = columns.index('lat')
            lats = dataframe.iloc[:,ic].values
        elif 'latitude' in columns:
            ic = columns.index('latitude')
            lats = dataframe.iloc[:,ic].values
        else: return False
        # end of step
        
        # step: import shapefile library
        try:
            import shapefile as shp
            version = int(shp.__version__[0])
        except: return False
        # end of steps
        
        # step: compute cell vertices
        vertices = GlobalGrid.compute_vertices_ndarray(
                                    lons=lons, 
                                    lats=lats,
                                    resolution_deg=resolution_deg)
        
        if vertices.shape[0] == 0: return False
        # end of step
        
        # step: open shape or create shape
        sf = None
        if version == 1: sf = shp.Writer(shp.POLYGON)
        elif version == 2: sf = shp.Writer(filename, shapeType=shp.POLYGON)
        else: return False
        sf.autoBalance = True
        # end of step
        
        # step: add shape fields
        if not fields: fields = generate_field_info(dataframe)
        
        for i in range(len(fields)): sf.field(*fields[i])
        # end of step
        
        # step: create shape polygons
        try:
            for i in range(vertices.shape[0]):
                v = vertices[i]
                r = dataframe.iloc[i, :].values
                
                sf.poly([v])
                sf.record(*r)
        except: return False
        # end of step
        
        # step: close or save shape object
        if version == 1: sf.save(filename)
        else: sf.close()
        # end of step
        
        # step: create projection string
        filename = filename[:-4] + '.prj'
        try:
            f = open(filename, 'w')
            if not prj_string:
                prj_string = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",' +
                              'SPHEROID["WGS_1984",6378137.0,298.257223563]],' +
                              'PRIMEM["Greenwich",0.0],UNIT["Degree",' +
                              '0.0174532925199433]]')
            f.write(prj_string)
            f.close()
        except: pass
        # end of step    
    
        return True
        
    @staticmethod
    def create_shapefile_ndarray(data:np.ndarray, 
                                 filename:str,
                                 columns:list,
                                 resolution_deg:float=0.5,
                                 fields:list=[],
                                 prj_string:str=''):
        
        # inner function to generate fields
        def generate_field_info(d:np.ndarray, columns:list):
            fields = []
            
            for i in range(d.shape[1]):
                f = [columns[i]]
                
                onevalue = d[0, i]
                
                if type(onevalue) in [np.int, np.int32, int]:
                    f += ['N', 15]
                elif type(onevalue) in [np.int64]:
                    f += ['N', 30]
                elif type(onevalue) is np.float64:
                    f += ['N', 50, 15]
                elif type(onevalue) in [np.float, np.float32, float]:
                    f += ['N', 22, 8]
                #elif type(onevalue) is np.datetime64:
                #    f += ['N', 22, 8]
                else: f += ['C', 50]
                
                fields.append(f)
            
            return fields
        # end of inner function
        
        
        # step: check input data
        if data.ndim != 2: return False
        if data.shape[0] == 0: return False
        if data.shape[1] == 0 or data.shape[1] != len(columns): return False            
        # end of step
        
        # step: find longitude and latitude information
        for i in range(len(columns)): columns[i] = columns[i].lower()
        
        lons, lats = None, None
        if 'lon' in columns:
            ic = columns.index('lon')
            lons = data[:,ic]
        elif 'longitude' in columns: 
            ic = columns.index('longitude')
            lons = data[:,ic]
        else: return False
            
        if 'lat' in columns:
            ic = columns.index('lat')
            lats = data[:,ic]
        elif 'latitude' in columns:
            ic = columns.index('latitude')
            lats = data[:,ic]
        else: return False
        # end of step
        
        # step: import shapefile library
        try:
            import shapefile as shp
            version = int(shp.__version__[0])
        except: return False
        # end of steps
        
        # step: compute cell vertices
        vertices = GlobalGrid.compute_vertices_ndarray(
                                    lons=lons, 
                                    lats=lats,
                                    resolution_deg=resolution_deg)
        
        if vertices.shape[0] == 0: return False
        # end of step
        
        # step: open shape or create shape
        sf = None
        if version == 1: sf = shp.Writer(shp.POLYGON)
        elif version == 2: sf = shp.Writer(filename, shapeType=shp.POLYGON)
        else: return False
        sf.autoBalance = True
        # end of step
        
        # step: add shape fields
        if not fields: fields = generate_field_info(data, columns)
        
        for i in range(len(fields)): sf.field(*fields[i])
        # end of step
        
        # step: create shape polygons
        try:
            if version == 1:
                for i in range(vertices.shape[0]):
                    v = vertices[i].tolist()
                    r = data[i, :]
                    
                    sf.poly([v], shapeType=shp.POLYGON)
                    sf.record(*r)
            else:
                for i in range(vertices.shape[0]):
                    v = vertices[i]
                    r = data[i, :]
                    
                    sf.poly([v])
                    sf.record(*r)
        except Exception as ex:
            print(str(ex))
            return False
        # end of step
        
        # step: close or save shape object
        if version == 1: sf.save(filename)
        else: sf.close()
        # end of step
        
        # step: create projection string
        filename = filename[:-4] + '.prj'
        try:
            f = open(filename, 'w')
            if not prj_string:
                prj_string = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",' +
                              'SPHEROID["WGS_1984",6378137.0,298.257223563]],' +
                              'PRIMEM["Greenwich",0.0],UNIT["Degree",' +
                              '0.0174532925199433]]')
            f.write(prj_string)
            f.close()
        except: pass
        # end of step    
    
        return True
        
    @staticmethod
    def create_wghm_grid_shape(
            filename:str='', 
            cell_info:np.ndarray=np.array([]), 
            data:np.ndarray=np.array([])):
        '''
        This method create shape a shape file with all WGHM cells. Additional
        data can be added in standard shape.

        :param filename: (string, optional, default = '') output shape filename
        :param cell_info: (np.ndarray, optional, default = empty array) WGHM 
                        cell information. cell info must have four columns 
                        (i.e., WGHM Cell Num, Arc ID, Longitude, Latitude) as 
                        in the lookup table. If this parameter is omitted, 
                        output shapefile will include all WGHM cells
        :param data: (np.ndarray, optional, default = empty array) additional 
                        data to be added
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True
        try: import shapefile as shp
        except: succeed = False
        
        version = int(shp.__version__[0])
        
        d = np.array([])
        if succeed:
            if len(GlobalGrid.__wghm_grid_lookup_table) == 0: 
                GlobalGrid.read_wghm_grid_lookup_table()
            
            d = GlobalGrid.__wghm_grid_lookup_table

            if len(cell_info) > 0:
                if not cell_info.shape[1] == 4: succeed = False
                else: d = cell_info


            if succeed and len(data) > 0:
                if len(data) == len(d): d = np.concatenate((d, data))
                else: succeed = False

        if succeed:
            if not filename: filename = 'grid_%s.shp' % GlobalGrid.__wghm_version
            elif filename[:-4].lower() != '.shp': filename += '.shp'

            if version == 1: g = shp.Writer(shp.POLYGON)
            elif version == 2: g = shp.Writer(filename, shp.POLYGON)
            else: return False
            
            g.autoBalance = 1

            g.field('ArcID', 'N', 8)
            g.field('CellNum', 'N', 8)
            g.field('Lon', 'N', decimal=10)
            g.field('Lat', 'N', decimal=10)

            if len(data) > 0:
                nfield = data.shape[1]
                for i in range(nfield): g.field('VALUE%d'%i, 'N', decimal=10)

            if version == 1:
                try:
                    for row in d:
                        x, y = row[2], row[3]
                        v = GlobalGrid.cell_vertices([(y, x)])
                        g.poly(v, shapeType=shp.POLYGON)
                        g.record(*row)
                except: succeed = False
            else:
                try:
                    for row in d.tolist():
                        cnum_i, arc_i = int(row[0]), int(row[1])
                        x, y = row[2], row[3]
                        v = GlobalGrid.cell_vertices([(y, x)])
                        g.poly(v)
                        
                        records = [arc_i, cnum_i, x, y] + row[4:]
                        g.record(*records)
                except: succeed = False
            
            try:
                if version == 1: g.save(filename)
                else: g.close()
                
                filename = filename[:-4] + '.prj'
                f = open(filename, 'w')
                prj_string = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",' + 
                              'SPHEROID["WGS_1984",6378137.0,298.257223563]],' +
                              'PRIMEM["Greenwich",0.0],UNIT["Degree",' + 
                              '0.0174532925199433]]')
                f.write(prj_string)
                f.close()
            except: succeed = False

        return succeed

    @staticmethod
    def find_group_geo_extent(centroids, degree_resolution=0.5):
        vertices = []
        d = degree_resolution/2

        temp = {}
        for centroid in centroids:
            try: temp[centroid[0]].append(centroid[1])
            except: temp[centroid[0]] = [centroid[1]]

        for k, v in temp.items(): # python2x: month_data.items() python3x: month_data.items()
            mn, mx = min(v), max(v)
            vl = [(k-d, mn-d), (k+d, mn-d), (k-d, mx+d), (k+d, mx+d)]
            for v in vl:
                if v not in vertices: vertices.append(v)

        temp = {}
        for centroid in centroids:
            try: temp[centroid[1]].append(centroid[0])
            except: temp[centroid[1]] = [centroid[0]]

        for k, v in temp.items(): # python2x: month_data.items() python3x: month_data.items()
            mn, mx = min(v), max(v)
            vl = [(mn-d, k-d), (mn-d, k+d), (mx+d, k-d), (mx+d, k+d)]
            for v in vl:
                if v not in vertices: vertices.append(v)

        # sorting vertices
        temp = {}
        for v in vertices:
            try: temp[v[1]].append(v[0])
            except: temp[v[1]] = [v[0]]
        vertices.clear()

        for k in temp.keys(): temp[k].sort()
        longitudes = list(temp.keys())
        longitudes.sort()

        ndx_lng = 0
        cur_lat = temp[longitudes[ndx_lng]].pop(0)
        vertices.append((cur_lat, longitudes[ndx_lng]))
        while temp:
            # North-South traverse
            try:
                latitudes = temp[longitudes[ndx_lng]]
                ndx_tmp = -1
                while True:
                    try:
                        ndx_tmp = latitudes.index(cur_lat+degree_resolution)
                        cur_lat = latitudes.pop(ndx_tmp)
                    except: break

                while True:
                    try:
                        ndx_tmp = latitudes.index(cur_lat-degree_resolution)
                        cur_lat = latitudes.pop(ndx_tmp)
                    except: break
                if ndx_tmp >= 0: vertices.append((cur_lat, longitudes[ndx_lng]))

                # while latitudes and abs(latitudes[0]-cur_lat) == degree_resolution: cur_lat = latitudes.pop(0)
                # #if len(latitudes) < ini_len: vertices.append((cur_lat, longitudes[ndx_lng]))
                #
                # #ini_len = len(latitudes)
                # while latitudes and abs(latitudes[-1]-cur_lat) == degree_resolution: cur_lat = latitudes.pop(-1)
                # if len(latitudes) < ini_len: vertices.append((cur_lat, longitudes[ndx_lng]))

                # East-West traverse
                ndx_tmp = -1
                while True:
                    try:
                        ndx_tmp = temp[longitudes[ndx_lng - 1]].index(cur_lat)
                        ndx_lng -= 1
                        cur_lat = temp[longitudes[ndx_lng]].pop(ndx_tmp)
                    except: break
                #if ndx_tmp >= 0: vertices.append((cur_lat, longitudes[ndx_lng]))

                #ndx_tmp = -1
                while True:
                    try:
                        ndx_tmp = temp[longitudes[ndx_lng + 1]].index(cur_lat)
                        ndx_lng += 1
                        cur_lat = temp[longitudes[ndx_lng]].pop(ndx_tmp)
                    except: break
                if ndx_tmp >= 0: vertices.append((cur_lat, longitudes[ndx_lng]))

                rem = []
                for k in temp.keys():
                    if not temp[k]: rem.append(k)
                for k in rem: temp.pop(k)

                print(len(vertices))
            except:
                print(temp)
                break


        #grid.bubble_sort(vertices)

        return vertices

    @staticmethod
    def __point_towards(source, direction, deg_resolution=0.5):
        direction = direction.lower()
        if direction in ['left', 'l', 'west', 'w']: return (source[0], source[1]-deg_resolution)
        elif direction in ['right', 'r', 'east', 'e']: return (source[0], source[1]+deg_resolution)
        elif direction in ['up', 'u', 'north', 'n']: return (source[0]+deg_resolution, source[1])
        elif direction in ['down', 'd', 'south', 's']: return (source[0]-deg_resolution, source[1])
        else: return ()

    @staticmethod
    def __neighbouring_points(source, directions=['n', 'e', 's', 'w'], deg_resolution=0.5):
        points = []
        for d in directions: points.append(GlobalGrid.__point_towards(source, d, deg_resolution))
        return points

    @staticmethod
    def __opposite_direction(direction):
        if direction in ['left', 'l', 'west', 'w']: return 'e'
        elif direction in ['right', 'r', 'east', 'e']: return 'w'
        elif direction in ['up', 'u', 'north', 'n']: return 's'
        elif direction in ['down', 'd', 'south', 's']: return 'n'
        else: return None

    @staticmethod
    def traverse(source, destination, direction, points, deg_resolution=0.5):
        output = []

        directions = list({'n', 'e', 's', 'w'} - {GlobalGrid.__opposite_direction(direction)})
        neighbours = []

        for i in reversed(range(len(directions))):
            next_destination = GlobalGrid.__point_towards(source, directions[i], deg_resolution=deg_resolution)

            if next_destination not in points: directions.pop(i)
            else: neighbours.append(next_destination)
        neighbours.reverse()

        if len(neighbours) == 1:
            if neighbours[0] != destination:
                output.append(neighbours[0])
                output += GlobalGrid.traverse(neighbours[0], destination, directions[0], points, deg_resolution=deg_resolution)
        elif len(neighbours) > 1:
            temp = []
            for i in range(len(neighbours)):
                temp.append(GlobalGrid.traverse(neighbours[i], destination, directions[i], points, deg_resolution=deg_resolution))
            ndx, cur_max = -1, 0
            for i in range(len(temp)):
                if len(temp[i]) > cur_max: ndx = i
            output += temp[i]

        return output

    @staticmethod
    def bubble_sort(geo_points):
        print(len(geo_points))
        while True:
            counter = 0
            for i in range(1, len(geo_points)):
                if GlobalGrid.compare(geo_points[i - 1], geo_points[i]) == 1:
                    temp = geo_points[i-1]
                    geo_points[i-1] = geo_points[i]
                    geo_points[i] = temp
                    counter += 1
            print(counter)
            if counter == 0 or counter == len(geo_points)-1: break

    @staticmethod
    def compare(p1, p2):
        if p1[1] == p2[1]:
            if p1[0] == p2[0]: return 0
            elif p1[0] > p1[0]: return 1
            else: return -1
        elif p1[1] > p2[1]:
            if p1[0] >= p2[0]: return 1
            else: return - 1
        else:
            if p1[0] >= p2[0]: return -1
            else: return 1

    @staticmethod
    def swap(p1, p2):
        t = p1
        p1 = p2
        p2 = t

    @staticmethod
    def combine_grid_cells(centroids, deg_resolution=0.5):
        d = deg_resolution/2

        # grouping the centroids' longitudes for latitudes
        latgroup = {}
        for c in centroids:
            try: latgroup[c[0]].append(c[1])
            except: latgroup[c[0]] = [c[1]]

        # making sub-groups of longitudes within each logitude group. Connected cells will be assigned to a sub-group.
        # and then finding the boundary longitude for each cell in each sub-group cells. sub-groups must be sorted
        for key in latgroup.keys():
            # sorting longitudes
            lnt_group = latgroup[key]
            lnt_group.sort()

            # making sub-groups
            sub_groups = []
            temp = [lnt_group[0]]
            for i in range(1, len(lnt_group)):
                if (lnt_group[i]-lnt_group[i-1]) == deg_resolution: temp.append(lnt_group[i])
                else:
                    sub_groups.append(temp)
                    temp = [lnt_group[i]]
            sub_groups.append(temp)         #adding the last group

            # calculating cell-boundary-longitudes
            for i in range(len(sub_groups)):
                temp = []
                for item in sub_groups[i]:
                    if item-d not in temp: temp.append(item-d)
                    if item+d not in temp: temp.append(item+d)
                # month_data.sort()
                sub_groups[i] = temp

            # assign sub-groups to latitude dictionary
            latgroup[key] = sub_groups

        key_list = list(latgroup.keys())
        key_list.sort()
        lines = []
        for key in key_list:
            sub_groups = latgroup[key]

            for grp in sub_groups:
                # create line and join the line with previous lines
                line = [(key-d, grp[-1]), (key+d, grp[-1]), (key+d, grp[0]), (key-d, grp[0])]
                for i in range(len(lines)):
                    join = False
                    if lines[i][2][0] == key-d:
                        if not (lines[i][2][1] > grp[-1] or lines[i][0][1] < grp[0]):
                            join = True
                    if join:
                        line = line + lines[i][2:] + lines[i][:2]
                        lines[i] = []

                # clean list of lines
                for i in reversed(range(len(lines))):
                    if not lines[i]: lines.pop(i)

                # insert line to lines in correct position
                ndx = 0
                for i in range(len(lines)):
                    if lines[i][0][1] > grp[-1]:
                        ndx = i
                        break
                else: ndx = len(lines)

                if ndx == len(lines): lines.append(line)
                else: lines = lines[:ndx] + [line] + lines[ndx:]

        if len(lines) > 1:
            for i in reversed(range(len(lines))):
                # check the bottom line or the south-most line (in terms of latitude and min-max longitude) of the i-th multi-line
                lat_min = 90
                for point in lines[i]:
                    if point[0] < lat_min: lat_min = point[0]

                temp = []
                for point in lines[i]:
                    if point[0] == lat_min: temp.append(point[1])
                long_min, long_max = min(temp), max(temp)

                for j in range(len(lines)):
                    if i != j:
                        temp = []
                        for k in range(len(lines[j])):
                            if lines[j][k][0] == lat_min:
                                ndx = -1
                                if k == 0: ndx = len(lines[j])-1
                                else: ndx = k-1
                                if lines[j][k][0] == lines[j][ndx][0]:
                                    temp.append([lines[j][k][1], lines[j][ndx][1]])

                        if temp:
                            k = -1
                            for k in range(len(temp)): temp[k].sort()

                            merge = False
                            for k in range(len(temp)):
                                if not (long_min > temp[k][1] or long_max < temp[k][0]):
                                    merge = True
                                    break

                            if merge:
                                ndx_iLine = lines[i].index((lat_min, long_max))
                                ndx_jLine = lines[j].index((lat_min, temp[k][1]))
                                ndx_jLine += 1
                                lines[j] = lines[j][:ndx_jLine] + lines[i][ndx_iLine:] + lines[i][:ndx_iLine] + lines[j][ndx_jLine:]
                                lines.pop(i)

        return lines
