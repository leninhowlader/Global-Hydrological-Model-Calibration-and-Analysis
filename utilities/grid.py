# Author: H.M. Mehedi Hasan
# Date: April, 2016

# The grid class provides supplementary functions for mapping WGHM 0.5-degree cells to absolute
# geo-corrdinates, grouping WGHM cells according to GRACE 1-degree cell, finding cell centroids, finding grid row and
# column for specific cell and transforming row and columns between two spatial resolutions.
#
# For mapping WGHM cells to geo-coordinates of the cell centroid, mapping data must be provided into 'wghm_grid.csv'
# file. wghm_grid.csv contains WGHM cell numbers, corresponding ArcIds, and longitudes and latitudes of the centroids of the
# corresponding WGHM cells.
#
# The grid class is static in nature and thus, all functions and variables are static.
#
# In this class the geo-locations are plotted on an imaginary grid situated within -180 to 180 degree longitude and
# within 90 to -90 degree latitude. The number of rows and columns of the imaginary grid depends on the grid-resolution.
# In order to find the reference cell number of a geo-location within a grid with specified resolution, one has to find
# the corresponding row and column numbers. Cell reference number within the imaginary grid is different than that
# of WGHM grid. In the imaginary grid the cell number starts from zero at the left-top corner of the grid (-180 degree
# longitude, 90 degree latitude) and increases first from left to right and then top to bottom. However, most of
# function works with row and column number.


#---------------------------:) DO NOT CHANGE ANYTHING BELOW IF YOU ARE NOT CONFIDENT :)----------------------------------#

import sys, os
sys.path.append('..')
from utilities.fileio import read_flat_file, read_binary_file

class grid:
    wghm_cellareas = []
    wghm_cellarea_file = 'data/GAREA.UNF0'
    wghm_grid_mapping_data = []
    wghm_grid_mapping_file = 'data/wghm_grid.csv'

    @staticmethod
    def get_wghm_cell_area_file(): return os.path.join(os.path.dirname(__file__), grid.wghm_cellarea_file)

    @staticmethod
    def get_wghm_grid_mapfile(): return os.path.join(os.path.dirname(__file__), grid.wghm_grid_mapping_file)

    @staticmethod
    def find_wghm_cellarea(row, base_resolution=0.5):
        if not grid.wghm_cellareas: grid.read_wghm_cellarea_file()

        if base_resolution != 0.5: row = grid.transform_row_number(row, base_resolution, 0.5)

        if grid.wghm_cellareas and 0<=row<=359: return grid.wghm_cellareas[row]
        else: return None

    @staticmethod
    def get_wghm_world_grid_centroids():
        centriods = []

        if not grid.wghm_grid_mapping_data: grid.read_wghm_cell_map()

        if grid.wghm_grid_mapping_data:
            for gmd in grid.wghm_grid_mapping_data:
                centriods.append((gmd[3], gmd[2]))

        return centriods

    #method of reading wghm cell area from file
    @staticmethod
    def read_wghm_cellarea_file():
        temp = read_binary_file(grid.get_wghm_cell_area_file(), 4, '>f')
        if temp and len(temp) == 360:
            for i in range(len(temp)): grid.wghm_cellareas.append(temp[i][0])

    #function for reading mapping data from mapping file
    @staticmethod
    def read_wghm_cell_map():
        headers, grid.wghm_grid_mapping_data = read_flat_file(grid.get_wghm_grid_mapfile(), separator=',', header=True)

    #function for finding WGHM cell number for a geo-location using grid-row number and grid-column number
    @staticmethod
    def map_wghm_cell_number(row, col, base_resolution=0.5):
        if not grid.wghm_grid_mapping_data: grid.read_wghm_cell_map()

        #if row and col is based on other than 0.5-degree grid, transform row and col in 0.5-degree grid row and col
        if base_resolution != 0.5:
            row, col = grid.transform_row_column(row, col, base_resolution, 0.5)

        #calculate the cen centroid
        y, x = grid.find_centroid(row, col, 0.5)

        #find wghm cell number using geo-coordinates of the centriod
        for md in grid.wghm_grid_mapping_data:
            if md[2] == x and md[3] == y: return md[0]

        return None

    #method for finding the cell centroid of a specified wghm cell
    @staticmethod
    def map_centroid_from_wghm_cell_number(cell_number):
        if not grid.wghm_grid_mapping_data: grid.read_wghm_cell_map()

        longitude, latitude = None, None

        for md in grid.wghm_grid_mapping_data:
            if md[0] == cell_number:
                latitude = md[3]
                longitude = md[2]
                break

        return latitude, longitude

    #method for finding nearest meridian line through centroid from another meridian line
    @staticmethod
    def nearest_centroid_longitude(longitude, degree_resolution=0.5):
        long = ((180+longitude)//degree_resolution)*degree_resolution+float(degree_resolution)/2-180
        if long > 180: return (long - 360)
        else: return long

    #method for finding nearest parallel line through centroid from another parallel line
    @staticmethod
    def nearest_centroid_latitude(latitude, degree_resolution=0.5):
        lat = ((90+latitude)//degree_resolution)*degree_resolution+float(degree_resolution)/2-90
        if lat > 90: return lat - degree_resolution
        else: return lat

    #method for finding the nearest cell centroid of a geo-location
    @staticmethod
    def nearest_centroid(latitude, longitude, degree_resolution=0.5):
        if -180<=longitude<=180 and -90<=latitude<=90:
            return grid.nearest_centroid_latitude(latitude, degree_resolution), grid.nearest_centroid_longitude(longitude, degree_resolution)
        else: return None, None

    #method for finding column number of a grid for a given longitude
    @staticmethod
    def find_column_number(longitude, degree_resolution=0.5):
        if -180<=longitude<=180:
            if longitude == 180: return int(((longitude+180)//degree_resolution)-1)
            else: return int((longitude+180)//degree_resolution)
        else: return None

    #method for finding row number of a grid for a given latitude
    @staticmethod
    def find_row_number(latitude, degree_resolution=0.5):
        if -90<=latitude<=90:
            if latitude == -90: return int((abs(latitude-90)//degree_resolution)-1)
            else: return int(abs(latitude-90)//degree_resolution)
        else: return None

    #method for finding row and column numbers of a grid for a given geo-location
    @staticmethod
    def find_row_column(latitude, longitude, degree_resolution=0.5):
        return grid.find_row_number(latitude, degree_resolution), grid.find_column_number(longitude, degree_resolution)

    #method for transforming a column number into column number of a different grid
    @staticmethod
    def transform_column_number(column_number, resolution_from, resolution_to):
        try:
            if column_number >= 0 and resolution_from >= 0 and resolution_to >= 0:
                return grid.find_column_number(column_number*resolution_from-180, resolution_to)
            else: return None
        except: return None

    #method for transforming a row number into row number of a different grid
    @staticmethod
    def transform_row_number(row_number, resolution_from, resolution_to):
        try:
            if row_number >= 0 and resolution_from >= 0 and resolution_to >= 0:
                return grid.find_row_number(-(row_number*resolution_from)+90, resolution_to)
            else: return None
        except: return None

    #method for transforming row and column number into row and column of a different grid
    @staticmethod
    def transform_row_column(row, column, base_resolution, target_resolution):
        return grid.transform_row_number(row, base_resolution, target_resolution), grid.transform_column_number(column, base_resolution, target_resolution)

    #method for finding geo-coordinates of a cell centroid of a given cell
    @staticmethod
    def find_centroid(row, column, deg_resolution=0.5):
        longitude = (column*deg_resolution)-180+(deg_resolution/2)
        latitude = -(row*deg_resolution)+90-(deg_resolution/2)
        if -90<=latitude<=90 and -180<=longitude<=180: return latitude, longitude
        else: return None, None

    #method for grouping grid cells based on a lower (numerically higher) resolution gird
    @staticmethod
    def cell_grouping(cell_list, base_resolution=0.5, target_resolution=1.0):
        if target_resolution > base_resolution and target_resolution%base_resolution==0.0:
            cell_count = len(cell_list)
            truth = [False]*cell_count

            transformed_cells= []
            for cell in cell_list: transformed_cells.append(grid.transform_row_column(cell[0], cell[1], base_resolution, target_resolution))

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

    #write grouped cells into flat file
    @staticmethod
    def write_groupfile(filename, array, mode='w'):
        f = None
        try:
            f = open(filename, mode)
            str_list = []
            for item in array: str_list.append('[' + ','.join(str(x) for x in item) + ']')
            f.write(', '.join(str_list))
        except: return False
        finally:
            try: f.close()
            except: pass

        return True

    #read cell groups from a flat file
    @staticmethod
    def read_groupfile(filename, data_type='int'):
        records = []    #array of arrays (list of groups)

        f = None
        try:
            f = open(filename, 'r')
            for line in f.readlines():
                temp = line.split(']')

                for i in range(len(temp)):
                    temp[i] = temp[i].strip().strip(',').strip().strip('[')
                    if temp[i]:
                        group_items = temp[i].split(',')

                        if data_type == 'int':
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
        # centroids must be a list of list

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
    def find_group_geo_extent(centroids, degree_resolution=0.5):
        vertices = []
        d = degree_resolution/2

        temp = {}
        for centroid in centroids:
            try: temp[centroid[0]].append(centroid[1])
            except: temp[centroid[0]] = [centroid[1]]

        for k, v in temp.items(): # python2x: temp.items() python3x: temp.items()
            mn, mx = min(v), max(v)
            vl = [(k-d, mn-d), (k+d, mn-d), (k-d, mx+d), (k+d, mx+d)]
            for v in vl:
                if v not in vertices: vertices.append(v)

        temp = {}
        for centroid in centroids:
            try: temp[centroid[1]].append(centroid[0])
            except: temp[centroid[1]] = [centroid[0]]

        for k, v in temp.items(): # python2x: temp.items() python3x: temp.items()
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
        for d in directions: points.append(grid.__point_towards(source, d, deg_resolution))
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

        directions = list({'n', 'e', 's', 'w'} - {grid.__opposite_direction(direction)})
        neighbours = []

        for i in reversed(range(len(directions))):
            next_destination = grid.__point_towards(source, directions[i], deg_resolution=deg_resolution)

            if next_destination not in points: directions.pop(i)
            else: neighbours.append(next_destination)
        neighbours.reverse()

        if len(neighbours) == 1:
            if neighbours[0] != destination:
                output.append(neighbours[0])
                output += grid.traverse(neighbours[0], destination, directions[0], points, deg_resolution=deg_resolution)
        elif len(neighbours) > 1:
            temp = []
            for i in range(len(neighbours)):
                temp.append(grid.traverse(neighbours[i], destination, directions[i], points, deg_resolution=deg_resolution))
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
                if grid.compare(geo_points[i-1], geo_points[i]) == 1:
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
                # temp.sort()
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
