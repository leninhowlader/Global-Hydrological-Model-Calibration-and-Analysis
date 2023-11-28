#!/usr/bin/python

__author__ = 'mhasan'

import sys, os, math, numpy as np
from collections import OrderedDict

from utilities.globalgrid import GlobalGrid
from utilities.enums import FileEndian


class Upstream:
    # default flow-direction file
    flow_direction_file = 'data/flow-direction_wghm2.2b.asc'          # flow-direction file

    # static variables
    flow_direction_data = np.array([])
    directions = [1, 2, 4, 8, 16, 32, 64, 128]

    @staticmethod
    def get_flow_direction_datafile():
        '''
        Returns the absolute path of flow-direction data file

        :return: (string) full path of the flow-direction data file
        '''
        if os.path.isabs(Upstream.flow_direction_file): return Upstream.flow_direction_file
        else: return os.path.join(os.path.dirname(__file__), Upstream.flow_direction_file)

    @staticmethod
    def set_flow_direction_file(filename):
        '''
        Sets filename of flow direction data file.

        :param filename: (string) name of the data file
        :return: None
        '''

        if os.path.isabs(filename): Upstream.flow_direction_file = filename
        Upstream.flow_direction_data.clear()
        Upstream.read_flow_data(filename)

    @staticmethod
    def read_flow_data(direction_datafile='', unf_input=True, model_version='wghm2.2d'):
        '''
        The method reads flow-direction data from file

        Parameters:
        :param direction_datafile: (string; optional; default = '') name of flow-direction map file
        :param model_version: (string; optional; default = 'wghm2.2d') model version
        :return: None
        '''
        succeed = True
        
        if GlobalGrid.get_current_model_version() != model_version:
            GlobalGrid.set_model_version(model_version)
        
        if not direction_datafile:
            if unf_input: 
                direction_datafile = 'data/flow_direction_%s.unf2' % model_version
            else: direction_datafile = 'data/flow_direction%s.asc' % model_version

        if (Upstream.flow_direction_file == direction_datafile and
            Upstream.flow_direction_data.shape == (360, 720)): return succeed
        else: Upstream.flow_direction_file = direction_datafile

        datafile_fullpath = Upstream.get_flow_direction_datafile()
        
        if not os.path.exists(datafile_fullpath): succeed = False
        else:
            Upstream.flow_direction_data = np.array([])
            
            if unf_input: 
                succeed = Upstream.construct_flow_data_from_unf(datafile_fullpath)
            else: succeed = Upstream.read_flow_data_from_ascii(datafile_fullpath)
            
            if not (succeed and Upstream.flow_direction_data.shape == (360, 720)): 
                succeed = False

        return succeed

    @staticmethod
    def read_flow_data_from_ascii(filename, skiprows=6):
        '''
        Reads flow-direction from ascii or text file.

        :param filename: (string) name of the datafile
        :param skiprows: (int) number of lines to be skipped
        :return: (bool) True on success, False otherwise
        '''

        succeed = True
        d = np.loadtxt(filename, skiprows=skiprows)
        if d.shape == (360, 720): Upstream.flow_direction_data = d
        else: succeed = False

        return succeed

    @staticmethod
    def construct_flow_data_from_unf(filename):
        '''
        The method generates flow-direction map (data) from WGHM flow direction file (i.e., G_FLOWDIR.UNF2) and stores
        or replace flow direction map into class variable

        :param filename: (string) full path of WGHM binary flow direction file
        :return: (boolean) True on success, False otherwise

        NB: WGHM flow direction map must be in UNF2 format. Number of cell must be in agreement with number of WGHM grid
            cells (as in GlobalGrid class)
        '''

        # remove existing flow direction data
        Upstream.flow_direction_data = np.array([])

        # find number of WGHM grid cell accounted in the current mode version
        ncell = GlobalGrid.get_wghm_cell_count()

        # read WGHM flow direction file (UNF2)
        d = np.array([])
        try: d = np.fromfile(filename, dtype='>h')
        except: return False

        # If number of cells both in WGHM flow direction file and current WGHM model grid, construct flow-direction
        # grid for the entire globe
        if len(d) == ncell:
            # define a global grid and initialize with none values (i.e., -9999)
            grid_globe = np.zeros((360, 720), dtype=int)        # 0.5 degree world grid
            grid_globe[:,:] = -9999

            # read row-column index of WGHM cells
            grid_wghm = GlobalGrid.get_wghm_grid_rowcolumn()   # WGHM grid (only land)

            # assign flow direction value to appropriate cells
            for i in range(ncell):
                row, col = grid_wghm[i]
                grid_globe[row, col] = d[i]
        else: return False # Otherwise, report failure

        # store newly constructed flow-direction map (into class variable)
        Upstream.flow_direction_data = grid_globe

        return True

    @staticmethod
    def get_flow_direction(row, col):
        '''
        The method extracts flow direction of a cell specified by its row and column number. If the flow direction is
        'zero' the cell flows into an inland sink or in the ocean. The directions are as follow:

        1: East, 2: South East, 4: South, 8: South West, 16: West, 32: North West, 64: North, 128: North East
        0: No direction (flows in inland sink or in the ocean), -9999: No value

        Parameters:
        :param row: (int) row number of the given cell
        :param col: (int) column number of the given cell

        Returns:
        :return: (int) the direction of outflow from given cell
        '''

        if len(Upstream.flow_direction_data) == 0: Upstream.read_flow_data()

        return Upstream.flow_direction_data[row][col]

    @staticmethod
    def is_upstream(row, col, direction):
        '''
        The method find whether or not a given cell belongs to the upstream of a reference cell. The reference
        cell is located in the direction specified by 'direction' input

        :param row: (int) row index of a given cell
        :param col: (int) column index of the given cell
        :param direction: (int) the direction at which the reference cell is located
        :return: (boolean) True if the given cell is immediate upstream cell of the reference cell,
                           False otherwise.
        '''

        val = Upstream.get_flow_direction(row, col)
        if val == direction: return True
        else: return False

    @staticmethod
    def get_neighbour_cell_backward_direction(row, col, direction):
        '''
        Finds the cell (as its row and column index) from which the given cell (i.e., the current cell) locates in a
        given direction. For example: from which cell the current cell is in the east?

        :param row: (int) row index of the current cell
        :param col: (int) column index of the current cell
        :param direction: (int) direction from the resultant cell to the current cell
        :return: (tuple of int) row and column index of a cell
        '''
        if direction == 1:row, col = row, col - 1
        elif direction == 2:row, col = row - 1, col - 1
        elif direction == 4:row, col = row - 1, col
        elif direction == 8:row, col = row - 1, col + 1
        elif direction == 16:row, col = row, col + 1
        elif direction == 32:row, col = row + 1, col + 1
        elif direction == 64:row, col = row + 1, col
        else: row, col = row+1, col-1

        if row == -1: row = 359
        elif row == 360: row = 0

        if col == -1: col = 719
        elif col == 720: col = 0

        return row, col

    @staticmethod
    def get_neighbour_cell_forward_direction(row, col, direction):
        '''
        Finds the cell that is in a given direction from the current cell. For example: what cell is in the east of
        current cell

        :param row: (int) row index of the current cell
        :param col: (int) column index of the current cell
        :param direction: (int) direction from the current cell towards the resultant cell
        :return: (tuple of int) row and column index of the result cell
        '''
        if direction == 1: row, col = row, col+1
        elif direction == 2: row, col = row+1, col+1
        elif direction == 4: row, col = row+1, col
        elif direction == 8: row, col = row+1, col-1
        elif direction == 16: row, col = row, col-1
        elif direction == 32: row, col = row-1, col-1
        elif direction == 64: row, col = row-1, col
        else: row, col = row-1, col+1

        if row == -1: row = 359
        elif row == 360: row = 0

        if col == -1: col = 719
        elif col == 720: col = 0

        return row, col

    @staticmethod
    def get_neighbouring_cells(row, col, inverse=True):
        '''
        The method finds all neighbouring cells of a given cell. Note that direction of a neighbouring cell can be
        either from the current cell towards the neighbour cell (forward direction) or from the neighbour cell towards
        the current cell (backward direction) depending on the value of the inverse flag. If the flag is set 'true',
        all directions are considered as backward directions i.e., direction from a neighbour cell to the current
        cell.

        :param row: (int) row index of the current cell
        :param col: (int) column index of the current cell
        :param inverse: (boolean; optional; default = True) direction flag. if the falg value is true, all directions
                        are from the neighbours toward the current cell
        :return:(list of tuples of integers) row and col index of all neighbour cells
        '''

        if inverse:  fun = Upstream.get_neighbour_cell_backward_direction
        else: fun = Upstream.get_neighbour_cell_forward_direction

        neighbouring_cells = []
        for d in Upstream.directions:
            cell = fun(row, col, d)
            neighbouring_cells.append(cell)

        return neighbouring_cells

    @staticmethod
    def get_upstream_cells(row, col):
        '''
        The method finds all upstream cells of a given cell. Note that the given cell is not part of the return cell.

        Parameters:
        :param row: (int) row index of a given cell
        :param col: (int) column index of a given cell

        Retruns:
        :return: (list of tuples of int) row and column index of all upstream cells from the given cell
        '''
        list_out = []

        # find neighbour cells of the given cell
        adj_cells = Upstream.get_neighbouring_cells(row, col)
        for i in range(len(adj_cells)):
            row = adj_cells[i][0]
            col = adj_cells[i][1]
            direction = Upstream.directions[i]

            # if the neighbour cell is a upstream cell of the current cell, include the neighbour cell as part of the
            # upstream basin. find the upstream cell from that neighbour cell and include those upstream cells as part
            # of current basin
            if Upstream.is_upstream(row, col, direction):
                list_out.append((row, col))

                # find the upstream from the neighbour cell
                temp = Upstream.get_upstream_cells(row, col)

                # include the upstream cells of the neighbour in the current basin
                if temp: list_out = list_out + temp

        return list_out

    @staticmethod
    def find_entire_basin(row:int, col:int):
        '''
        This method find the entire basin from any given cell of a basin

        :param row: (int) row index of a given cell
        :param col: (int) column index of a given cell
        :return: (list of tuples of int) tuples of row and column index of basin cells


        Algorithm:
        step-1: find the most downstream cell in the basin
        step-2: find upstream basin from the most dwonstream point
        '''

        # step: find the most downstream cell in the basin
        row, col = Upstream.most_downstream_cell(row, col)

        # step: find upstream basin from the most dwonstream point
        return [(row, col)] + Upstream.get_upstream_cells(row, col)

    @staticmethod
    def most_downstream_cell(row:int, col:int):
        '''
        Given any location of a basin, this method finds most downstream cell of the basin

        :param row: (int) row index of a given cell
        :param col: (int) column index of a given cell
        :return: (tuple of int of size 2) row index and column index of the most down cell in the basin
        '''

        # step: get the flow direction from the target cell
        direction = Upstream.get_flow_direction(row, col)

        # step: return current cell as the most downstream cell if flow direction from this cell goes into ocean or
        #       inland sink
        if direction == 0 or direction == -1: return row, col

        # step: move to the next cell in the (forward) direction of flow
        row, col = Upstream.get_neighbour_cell_forward_direction(row, col, direction)

        # step: from the new cell, recursively repeat the steps until most down point is reached
        return Upstream.most_downstream_cell(row, col)

    @staticmethod
    def next_downstream_cell(row, col):
        '''
        Finds the next downstream cell towards flow direction from given cell. If the reference cell flows into an inland
        sink or ocean, the reference cell is returned as the next cell.

        :param row: (int) row index of the reference cell
        :param col: (int) column index of the reference cell
        :return: (tuple of int) row and column index of the next cell towards flow direction.
        '''
        # step: get the flow direction from the target cell
        direction = Upstream.get_flow_direction(row, col)

        # step: return current cell as the most downstream cell if flow direction from this cell goes into ocean or
        #       inland sink
        if direction == 0 or direction == -1: return row, col

        # step: move to the next cell in the (forward) direction of flow
        row, col = Upstream.get_neighbour_cell_forward_direction(row, col, direction)

        return row, col

    @staticmethod
    def find_world_basins():
        '''
        Calculates all basins of the world.

        :return: (list of list (of tuples of int)) all basins and their cells
        '''
        world_basins = []

        # world grid row-column indices
        wg = GlobalGrid.get_wghm_grid_rowcolumn()

        nrow = wg.shape[0]
        cell_flags = np.ones(nrow, dtype=bool)

        index_new_basin = 0
        while index_new_basin < nrow:
            # find a cell of the new basin
            row, col = wg[index_new_basin]

            # find entire basin and add the basin to the world basin list
            b = Upstream.find_entire_basin(row, col)
            world_basins.append(b)

            # update cell flags
            ndx = [np.where((wg[:, 0] == x[0]) & (wg[:, 1] == x[1]))[0][0] for x in b]
            cell_flags[ndx] = False

            # update cell index for the next basin
            for i in range(index_new_basin, nrow):
                if cell_flags[i]:
                    index_new_basin = i
                    break
            else: index_new_basin = nrow

        return world_basins

    @staticmethod
    def find_independent_basin_groups(basin_outlets):
        '''
        find each level of independent basins from basin cascades

        :param basin_outlets: (list of tuples of row and column)
                              basin outlets
        :return: list of list of tuples of row and column
        '''
        basin_outlets = set(basin_outlets)

        supbasins = set(Upstream.find_super_basin(basin_outlets).keys())
        indbasins = (basin_outlets - supbasins)

        if len(indbasins) == len(basin_outlets): return [list(indbasins)]
        else:
            depbasin = basin_outlets - indbasins
            return ([list(indbasins)] +
                    Upstream.find_independent_basin_groups(depbasin))

    @staticmethod
    def find_super_basin(basin_outlets):
        '''
        Finds super basins and their sub-basins for given basin outlet cells.

        :param basin_outlets: (list of tuples/list or 2-d numpy array) basin outlets as their row and column index pairs
        :return: (dictionary) super-basins as the key of the output dictionary
                              and list of sub-basins of each super-
                              basin as the value of the key
                              e.g., {super-basin1: [subbasin1, subbasin2,..],
                                     super-basin2: [...], ...}

        NB: Note that output includes only those super basins that have at least one sub-basins
        '''
        # group basin outlets by their most downstream cell. [if two sub-basin outlet flows in the same sink (either
        # inland or ocean), the sub-basins are part of a common super basin]
        most_downstream_cells = {}
        for cell in basin_outlets:
            row, col = cell

            temp = Upstream.most_downstream_cell(row, col)
            try: most_downstream_cells[temp].append((row, col))
            except: most_downstream_cells[temp] = [(row, col)]

        # find super-basin for those sub-basins that flow to common sink
        super_basin = {}
        for key in most_downstream_cells.keys():
            outlets = most_downstream_cells[key]

            # if a downstream sink an only one outlet (somewhere in the upstreams), the upstream basin from the outlet
            # has no super basin
            if len(outlets) > 1:
                for i in range(len(outlets)):
                    outlet_curr = outlets[i]
                    outlet_others = outlets[:i] + outlets[i + 1:]

                    # from a basin outlet find the next cell towards flow direction, if the next cell is one of the
                    # remaining basin outlets, assign the cell as the outlet of super basin. Otherwise, continue
                    # searching though the stream flow until the sink is reached
                    curr_cell = outlet_curr
                    while True:
                        next_cell = Upstream.next_downstream_cell(curr_cell[0], curr_cell[1])

                        if next_cell == curr_cell: break

                        if next_cell in outlet_others:
                            try: super_basin[next_cell].append(outlet_curr)
                            except: super_basin[next_cell] = [outlet_curr]
                            break

                        curr_cell = next_cell
        return super_basin

    @staticmethod
    def compute_basin_extent(basin_outlets):
        '''
        This method find the upstream basin coverage (i.e., cells) from each given outlet points. The outlet points are
        given as tuples of row and column index of a grid cell

        :param basin_outlets: (list of tuples/list or 2-d numpy array) basin outlets as their row and column index pairs
        :return: (OrderedDict) basin coverage in terms of occupied cells belonging to the upstream of given outlet
                               points. The output is an ordered dictionary, the keys of the dictionary refer to the
                               basin outlet and the value contains the list of basin cell
                               example of data structure:
                               {outlet as tuple of row and column index: [basin cells ...], outlet2: [cells ..], ..}

        NB: The output data structure is required for calculating disjoint basin coverage specially for super basin and
        to identify the discharge cells for super basins.
        '''
        basins = OrderedDict()
        for cell in basin_outlets:
            cell = tuple(cell)
            upstream_basin = [cell] + Upstream.get_upstream_cells(cell[0], cell[1])
            basins[cell] = upstream_basin
        return basins

    @staticmethod
    def compute_nonoverlapping_basin_extent(basins:OrderedDict, super_basin:dict):
        '''
        The method computes non-overlapping basin coverage i.e., the area 
        between two station outlets
        
        Parameters:
        basins: OrderedDict
            all basins and their upstream basin coverage [see more in the 
            documentation of compute_basin_coverage method]
        super_basin: dict
            super basins as keys and their sub-basins as value [see more in the 
            description of find_super_basin method]
        
        Returns: 
        OrderedDict 
            non-overlapping basin coverage. the output data structure is similar
            to the input parameter 'basins'
        '''
        # copy basin information into a new variable
        nonoverlapping_basins = basins.copy()

        for key in super_basin.keys():
            # find sub-basins of a super-basin
            outlets_subbasin = super_basin[key]

            # exclude sub-basin cells from super-basin coverage, for each sub-basin
            temp = set(nonoverlapping_basins[key])
            for cell in outlets_subbasin: temp = temp - set(basins[cell])

            # set non-overlapping cells as the coverage of the super basin
            nonoverlapping_basins[key] = list(temp)

        return nonoverlapping_basins

    @staticmethod
    def find_basin_discharge_cell(basins:OrderedDict, super_basin:dict):
        '''
        Finds list of basin discharge cells specially for super basin. In order
        to compute the discharge from a super-basin, in addition to discharge
        from the super-basin outlet cells we need discharges from all sub-basin
        discharge. That is,

                    super basin discharge = discharge from super basin outlet - sum of all sub-basin discharge

        Thus, sub-basins outlet cells are important. The method outputs a list of outlet cells that is required for
        calculating discharge. In case of a super-basin, the outlet cell list consists more than one cells where the
        first cell is the outlet cell of the super basin. Thus, to compute the super-basin discharge, one must deduct
        discharges in other outlet cell from the discharge at the first outlet cell.

        :param basins: (OrderedDict) all basins and their upstream basin coverage [see more in the documentation of
                                     compute_basin_coverage method]
        :param super_basin: (dict)   super basins as keys and their sub-basins as value [see more in the description of
                                     find_super_basin method]
        :return: (list of list (of tuples of int)) list of discharge cells for each basin and/or super-basin. For super
                                     -basins a list element contains more than one entry. Otherwise, each list element
                                     should contain only one outlet cell

        NB: the mothod is written only for facilitating discharge calculation for disjoint super basins
        '''
        discharge_cell = []

        # copy basin list into a temporary variable
        temp = basins.copy()

        # for each basin, set the primary outlet cell which is exactly the same as the basin identifier (i.e., the keys)
        for key in temp.keys(): temp[key] = [key]

        # in case of super-basins, include the sub-basin outlets in the outlet cell list
        for key, value in super_basin.items(): temp[key] += value

        # store the discharge cell list into output data structure
        for key, value in temp.items(): discharge_cell.append(value)

        return discharge_cell

    @staticmethod
    def get_direction_line(centroid, degree_resolution=0.5):
        direction_line, arrows = [], []

        # inner function ...
        def theta_degree(direction):
            try: return -math.log2(direction) * 45
            except: return None
        # ...end of function

        # inner function ...
        def theta_radian(direction):
            try: return -math.log2(direction) * math.radians(45)
            except: return None
        # ... end of function

        # inner function ...
        def origin_to_destination_point(x, y, length_of_line, theta_radian):
            x2 = x + length_of_line * math.cos(theta_radian)
            y2 = y + length_of_line * math.sin(theta_radian)
            return x2, y2
        # ... end of function

        # inner function
        def arrow_pointers(x_head, y_head, baseline_rotation, pointer_len, array_angle_degree=30):
            points = []
            try:
                theta = math.degrees(baseline_rotation)
                theta1 = math.radians(180 + theta - array_angle_degree)
                theta2 = math.radians(180 + theta + array_angle_degree)

                x_p1 = x_head + pointer_len * math.cos(theta1)
                y_p1 = y_head + pointer_len * math.sin(theta1)

                x_p2 = x_head + pointer_len * math.cos(theta2)
                y_p2 = y_head + pointer_len * math.sin(theta2)
                points = [[x_p1, y_p1], [x_head, y_head], [x_p2, y_p2]]
            except: return None

            return points
        # ... end of function

        direction_line, arrows = [], []
        try:
            row, col = GlobalGrid.find_row_column(centroid[0], centroid[1], degree_resolution=degree_resolution)
            direction = Upstream.get_flow_direction(row, col)

            direction_line.append([centroid[1], centroid[0]])

            if direction > 0:
                theta = theta_radian(direction)
                if math.log2(direction)%2 == 0:
                    dest = origin_to_destination_point(centroid[1], centroid[0], degree_resolution * 0.5 * 1.5, theta)
                else: dest = origin_to_destination_point(centroid[1], centroid[0], degree_resolution * 1.06066, theta)
            else:
                theta = math.radians(-90)
                dest = [centroid[1], centroid[0] - 0.1]

            direction_line.append([dest[0], dest[1]])
            arrows = arrow_pointers(dest[0], dest[1], theta, degree_resolution / 6, array_angle_degree=30)
        except: pass

        return direction_line, arrows

    @staticmethod
    def compute_entire_upstream_area(cell_number:int):
        """
        This function computes the area of the entire upstram from a grid cell.

        Parameters:
        cell_number: (int)
            the cell number according to WaterGAP GCRC number system.

        Returns:
        (float)
            the area of the entire upstream region from the given cell
        """
        lat, lon = GlobalGrid.get_wghm_centroid(cell_number)
        outlet = GlobalGrid.find_row_column(latitude=lat, longitude=lon)
        upstreams = Upstream.compute_basin_extent([outlet])

        area = 0
        for row, _ in upstreams[outlet]: 
            area += GlobalGrid.find_wghm_cellarea(row)

        return area
    
    @staticmethod
    def create_basin_shape(
            filename,
            basin_outlets,
            basin_ids=[],
            add_wghm_cnum=False,
            draw_flow_direction=False,
            base_resolution=0.5,
            disjoint_basin=True
        ):
        '''
        The method creates a shape file of upstream basins from given basin outlets. The method will also draw the flow
        direction into another shape file if requested.

        :param filename: (string) output filename for the shapefile
        :param basin_outlets: (list of tuples/list or 2-d numpy array) row and column index of basin outlet cells
        :param basin_ids: (list of int) basin IDs. No. of IDs must be equal to no. of basin outlets
        :param add_wghm_cnum: (boolean) flag for acquiring WGHM cell number and including them in the output shape
        :param draw_flow_direction: (boolean) flag determining whether or not flow direction arrow will be produced
        :param base_resolution: (float; optional; default = 0.5) resolution of the grid in degree
        :param disjoint_basin: (boolean) flag determining whether or not sub-basin cells would be removed from super
                             basins to create non-overlapping basin
        :return: (boolean) True on success, Otherwise False
        '''
        succeed = True

        # step-1: check inputs
        if not basin_outlets: succeed = False
        elif not filename: succeed = False
        elif basin_ids and len(basin_ids) != len(basin_outlets): succeed = False
        else:
            for s in basin_outlets:
                if len(s) != 2:
                    succeed = False
                    break
        # ... end [step]

        if succeed:
            # step-2: compute upstream basins for given basin outlets
            list_of_basins = []

            if disjoint_basin:
                basins = Upstream.compute_basin_extent(basin_outlets)
                super_basins = Upstream.find_super_basin(basin_outlets)
                disjoint_basins = Upstream.compute_nonoverlapping_basin_extent(
                    basins, 
                    super_basins
                )
                for key, value in disjoint_basins.items(): 
                    list_of_basins.append(value)

                basins, super_basins, disjoint_basins = None, None, None
            else:
                for s in basin_outlets:
                    row, col = s[0], s[1]
                    if base_resolution != 0.5: row, col = GlobalGrid.transform_row_column(row, col, base_resolution, target_resolution=0.5)
                    temp = Upstream.get_upstream_cells(row, col)
                    if temp: list_of_basins.append([(row, col)]+temp)
                    else: list_of_basins.append([(row, col)])
            # ... end [step]

            # step-3: find geo-coordinates of each vertex of each cell of each basin
            geopoints = []
            for basin in list_of_basins:
                centroids = []
                for cell in basin: centroids.append(GlobalGrid.find_centroid(cell[0], cell[1], deg_resolution=0.5))
                geopoints.append(GlobalGrid.cell_vertices(centroids, degree_resolution=0.5))
            # ... end [step]

            # step-4: create shapefile and export the file
            import shapefile as shp
            version = int(shp.__version__[0])
            
            try:
                # create shape object
                if version == 1: shp_basin = shp.Writer(shp.POLYGON)
                elif version == 2: shp_basin = shp.Writer(filename, shp.POLYGON)
                else: return False
            
                shp_basin.autoBalance = 1

                # add shape attributes
                shp_basin.field('BASIN_ID', 'C', 40)
                if add_wghm_cnum: shp_basin.field('CNUM', 'N', 8)

                # generate basin IDs, if not given
                if not basin_ids: basin_ids = list(range(len(list_of_basins)))

                # create shape for each basin
                if version == 1:
                    for i in range(len(list_of_basins)):
                        basin = list_of_basins[i]
                        points = geopoints[i]
    
                        basin_id = basin_ids[i]
    
                        # add cells and their attributes to basin shape
                        if add_wghm_cnum:
                            for j in range(len(basin)):
                                cnum = GlobalGrid.get_wghm_cell_number(basin[j][0],
                                                                       basin[j][1],
                                                                       base_resolution=0.5)
                                shp_basin.poly(parts=[points[j]], shapeType=shp.POLYGON)
                                shp_basin.record(str(basin_id), cnum)
                        else:
                            for j in range(len(basin)):
                                shp_basin.poly(parts=[points[j]], shapeType=shp.POLYGON)
                                shp_basin.record(str(basin_id))
                else: # version == 2
                    for i in range(len(list_of_basins)):
                        basin = list_of_basins[i]
                        points = geopoints[i]
    
                        basin_id = basin_ids[i]
    
                        # add cells and their attributes to basin shape
                        if add_wghm_cnum:
                            for j in range(len(basin)):
                                cnum = GlobalGrid.get_wghm_cell_number(basin[j][0], 
                                                                       basin[j][1], 
                                                                       base_resolution=0.5)
                                shp_basin.poly([points[j]])
                                shp_basin.record(basin_id, cnum)
                        else:
                            for j in range(len(basin)):
                                shp_basin.poly([points[j]])
                                shp_basin.record(basin_id)

                # save shapefile
                if version == 1: shp_basin.save(filename)
                else: shp_basin.close()

                # create a projection file
                ndx = filename.lower().find('.shp')
                if ndx >= 0: filename = filename[:ndx]
                filename += '.prj'
                f = open(filename, 'w')
                prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                f.write(prj_string)
                f.close()
            except: succeed = False
            # ... end [step-4]

            # step-5: create flow direction shapefile
            if succeed and draw_flow_direction:
                try:
                    # generate arrow filename
                    ndx = filename.lower().find('.prj')
                    if ndx >= 0:
                        filename = filename[:ndx]
                    else:
                        ndx = filename.lower().find('.shp')
                        if ndx >= 0: filename = filename[:ndx]
                    filename = filename + '_arrows'

                    # create shape object
                    if version == 1:
                        shp_arrow = shp.Writer(shp.POLYLINE)
                    elif version == 2:
                        shp_arrow = shp.Writer(filename + '.shp', shp.POLYLINE)
                    else: return False

                    shp_arrow.field('ARROW', 'N', 8)

                    # draw arrows in each cell
                    arrow_id = 1
                    for basin in list_of_basins:
                        for cell in basin:
                            centroid = GlobalGrid.find_centroid(cell[0], cell[1], deg_resolution=0.5)
                            arrow, pointer = Upstream.get_direction_line(centroid)
                            if version == 1:
                                shp_arrow.line(parts=[arrow, pointer], shapeType=shp.POLYLINEM)
                            else: shp_arrow.line([arrow, pointer])
                            shp_arrow.record(arrow_id)
                            # shp_arrow.line(parts=[pointer], shapeType=shp.POLYLINE)
                            # shp_arrow.record(arrow_id)
                            arrow_id += 1

                    # save direction shapefile
                    if version == 1: shp_arrow.save(filename + '.shp')
                    else: shp_arrow.close()

                    # create projection file for direction shapefile
                    f = open(filename + '.prj', 'w')
                    prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                    f.write(prj_string)
                    f.close()
                except: succeed = False
            # ... end [step-5]
        return succeed

    @staticmethod
    def create_shape_with_predictions(filename_output_shape, filename_station, filename_wghm_prediction,
                                      model_version='wghm2.2d', basin_ids=[], prediction_file_endian=FileEndian.big_endian,
                                      add_wghm_cnum=True, model_grid_resolution=0.5):

        # step: check input parameters
        if not (filename_output_shape or filename_station or filename_wghm_prediction): return False
        if not(os.path.exists(filename_station) and os.path.exists(filename_wghm_prediction)): return False
        if not model_version.lower() in ['wghm2.2b', 'wghm2.2d']: return False

        # step: read stations from [station] file
        from utilities.station import Station
        stations = Station.read_stations(filename_station)
        if not stations: return False
        if basin_ids:
            if len(basin_ids) != len(stations): return False
            for bid in basin_ids:
                if type(bid) is not int: return False
        else:
            for i in range(len(stations)): basin_ids.append(i+1)

        # step: set model version
        GlobalGrid.set_model_version(model_version)

        # step: find upstream basin for each stations
        upstream_basins = []
        for s in stations:
            lat, lon = s[2], s[1]
            row, col = GlobalGrid.find_row_column(lat, lon, model_grid_resolution)

            temp = Upstream.get_upstream_cells(row, col)
            if temp: upstream_basins.append([(row, col)] + temp)
            else: upstream_basins.append([(row, col)])
        if not upstream_basins: return False

        # step: find cell centroid for each cell in each basin
        geopoints = []
        for basin in upstream_basins:
            centroids = []
            for cell in basin: centroids.append(GlobalGrid.find_centroid(cell[0], cell[1], deg_resolution=model_grid_resolution))
            geopoints.append(GlobalGrid.cell_vertices(centroids, degree_resolution=model_grid_resolution))
        if not geopoints: return False

        # step: find wghm cell number
        wghm_upstreams_cnum = []
        for basin in upstream_basins:
            temp = []
            for cell in basin: temp.append(GlobalGrid.get_wghm_cell_number(cell[0], cell[1], base_resolution=model_grid_resolution))
            wghm_upstreams_cnum.append(temp)
        if not wghm_upstreams_cnum: return False

        # step: read wghm predictions
        from wgap.wgapio import WaterGapIO
        import numpy as np

        d = WaterGapIO.read_unf(filename_wghm_prediction, file_endian=prediction_file_endian)
        if type(d) is not np.ndarray: return False

        data = []
        for basin in wghm_upstreams_cnum:
            basin = np.array(basin) - 1
            data.append(d[basin])

        ncol = d.shape[1]
        d = None
        if not data: return False

        # step: add attributes for each column in data
        attrib_list = []
        if ncol == 12: attrib_list = ['jan', 'feb', 'mar', 'arp', 'may', 'jun',
                                      'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        else:
            for i in range(ncol): attrib_list.append('value%d'%(i+1))
        if not attrib_list: return False

        try:
            # step: create shape
            import shapefile as shp
            shp_basin = shp.Writer(shp.POLYGON)
            shp_basin.autoBalance = 1

            # add fields
            shp_basin.field('BASIN', 'N', 8)
            shp_basin.field('CNUM', 'N', 8)
            for attrib in attrib_list: shp_basin.field(attrib, 'N', decimal=10)

            for i in range(len(upstream_basins)):
                bid = basin_ids[i]

                basin_cnum = wghm_upstreams_cnum[i]
                records = data[i]
                points = geopoints[i]
                for j in range(len(basin_cnum)):
                    record_row = [bid, basin_cnum[j]] + records[j].flatten().tolist()
                    shp_basin.poly(parts=[points[j]], shapeType=shp.POLYGON)
                    shp_basin.record(*record_row)


            # step: save shape into shape file and add projection file
            shp_basin.save(filename_output_shape)
            ndx = filename_output_shape.lower().find('.shp')
            if ndx >= 0: filename_output_shape = filename_output_shape[:ndx]
            filename_output_shape += '.prj'
            f = open(filename_output_shape, 'w')
            prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
            f.write(prj_string)
            f.close()
        except: return False

        return True

    @staticmethod
    def create_shape_with_data(
        filename_output_shape, 
        basin_id, 
        data, 
        wghm_cnum_list, 
        model_grid_resolution=0.5
    ):

        # step: check input parameters
        if not filename_output_shape: return False
        if not (len(wghm_cnum_list) == len(data)): return False
        if basin_id <= 0: return False

        # step: find cell centroid for each cell in each basin
        geopoints, centroids = [], []
        for cnum in wghm_cnum_list:
            centroids.append(GlobalGrid.get_wghm_centroid(cnum))
        geopoints = GlobalGrid.cell_vertices(centroids, degree_resolution=model_grid_resolution)
        if not geopoints: return False

        if True:
        # try:
            # step: create shape
            import shapefile as shp
            version = int(shp.__version__[0])
            
            # create shape object
            if version == 1: shp_basin = shp.Writer(shp.POLYGON)
            elif version == 2: 
                shp_basin = shp.Writer(filename_output_shape, shp.POLYGON)
            else: return False
            
            shp_basin.autoBalance = 1

            # add fields
            shp_basin.field('BASIN', 'N', 8)
            shp_basin.field('CNUM', 'N', 8)
            shp_basin.field('Value', 'N', decimal=10)

            # create shape for each basin
            if version == 1:
                for j in range(len(wghm_cnum_list)):
                    record_row = [basin_id, wghm_cnum_list[j], data[j]]
                    shp_basin.poly(parts=[geopoints[j]], shapeType=shp.POLYGON)
                    shp_basin.record(*record_row)
                
            else: # version == 2
                for j in range(len(wghm_cnum_list)):
                    record_row = [basin_id, wghm_cnum_list[j], data[j]]
                    shp_basin.poly([geopoints[j]])
                    shp_basin.record(*record_row)

            # step: save shapefile
            if version == 1: shp_basin.save(filename_output_shape)
            else: shp_basin.close()
            # end [step]

            # step: create projection file
            ndx = filename_output_shape.lower().find('.shp')
            if ndx >= 0: filename_output_shape = filename_output_shape[:ndx]
            filename_output_shape += '.prj'
            f = open(filename_output_shape, 'w')
            prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
            f.write(prj_string)
            f.close()
            # end [step]
        # except:
        #     return False

        return True
