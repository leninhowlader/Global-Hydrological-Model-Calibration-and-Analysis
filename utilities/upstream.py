#!/usr/bin/python

__author__ = 'mhasan'

import sys, os, math
sys.path.append('..')
from utilities.fileio import read_flat_file
from utilities.grid import grid


class Upstream:
    # default flow-direction file
    flow_direction_file = 'data/flow-direction.asc'          # flow-direction file

    # static variables
    flow_direction_data = []
    directions = [1, 2, 4, 8, 16, 32, 64, 128]

    @staticmethod
    def get_flow_direction_datafile():
        if os.path.isabs(Upstream.flow_direction_file): return Upstream.flow_direction_file
        else: return os.path.join(os.path.dirname(__file__), Upstream.flow_direction_file)

    # method of setting flow-direction file
    @staticmethod
    def set_flow_direction_file(filename):
        if os.path.isabs(filename): Upstream.flow_direction_file = filename
        Upstream.flow_direction_data.clear()
        Upstream.read_flow_data(filename)

    # method of reading flow-direction data
    @staticmethod
    def read_flow_data(direction_datafile=''):
        if not direction_datafile: direction_datafile = Upstream.get_flow_direction_datafile()

        headers, temp = read_flat_file(direction_datafile, skiplines=6)
        if temp: Upstream.flow_direction_data = temp
        else:
            message = 'Flow direction data could not be retrieved. Either "%s" does not exists or has bad-format.' % direction_datafile
            print(message)
            exit(os.EX_NOINPUT)

    # method of finding flow-direction for a given cell
    @staticmethod
    def get_flow_direction(row, col):
        if not Upstream.flow_direction_data: Upstream.read_flow_data()

        return Upstream.flow_direction_data[row][col]

    # method of finding if a give cell is a upstream cell for another reference cell;
    # the reference cell is referred as direction from the given cell
    @staticmethod
    def is_upstream(row, col, direction):
        val = Upstream.get_flow_direction(row, col)
        if val == direction: return True
        else: return False

    # method of finding neighboring cell towards a given direction from a given cell
    @staticmethod
    def get_neighbour_cell_towards_direction(row, col, direction):
        if direction == 1: return row, col-1
        elif direction == 2: return row-1, col-1
        elif direction == 4: return row-1, col
        elif direction == 8: return row-1, col+1
        elif direction == 16: return row, col+1
        elif direction == 32: return row+1, col+1
        elif direction == 64: return row+1, col
        else: return row+1, col-1

    # method of finding the neighboring cells of a given cell in all directions
    @staticmethod
    def get_neighbouring_cells(row, col):
        cells = []
        for d in Upstream.directions: cells.append(Upstream.get_neighbour_cell_towards_direction(row, col, d))

        return cells

    # method of finding the upstream cells of a given cell
    @staticmethod
    def get_upstream_cells(row, col):
        list_out = []
        adj_cells = Upstream.get_neighbouring_cells(row, col)
        for i in range(len(adj_cells)):
            row = adj_cells[i][0]
            col = adj_cells[i][1]
            direction = Upstream.directions[i]
            if Upstream.is_upstream(row, col, direction):
                list_out.append((row, col))
                temp = Upstream.get_upstream_cells(row, col)
                if temp: list_out = list_out + temp

        return list_out

    @staticmethod
    def theta_degree(direction):
        try: return -math.log2(direction) * 45
        except: return None

    @staticmethod
    def theta_radian(direction):
        try: return -math.log2(direction) * math.radians(45)
        except: return None

    @staticmethod
    def origin_to_destination_point(x, y, length_of_line, theta_radian):
        x2 = x + length_of_line * math.cos(theta_radian)
        y2 = y + length_of_line * math.sin(theta_radian)
        return x2, y2

    @staticmethod
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

    @staticmethod
    def get_direction_line(centroid, degree_resolution=0.5):
        dline, arrows = [], []

        try:
            row, col = grid.find_row_column(centroid[0], centroid[1], degree_resolution=degree_resolution)
            direction = Upstream.get_flow_direction(row, col)

            dline.append([centroid[1], centroid[0]])
            theta = Upstream.theta_radian(direction)
            if math.log2(direction)%2 ==0:
                dest = Upstream.origin_to_destination_point(centroid[1], centroid[0], degree_resolution * 0.5 * 1.5, theta)
            else: dest = Upstream.origin_to_destination_point(centroid[1], centroid[0], degree_resolution * 1.06066, theta)
            dline.append([dest[0], dest[1]])

            arrows = Upstream.arrow_pointers(dest[0], dest[1], theta, degree_resolution / 6, array_angle_degree=30)
        except: return [], []

        return dline, arrows

    @staticmethod
    def create_basin_shape(filename, stations, basin_ids=[], add_wghm_cnum=False, draw_flow_direction=False, base_resolution=0.5):
        succeed = True

        if not stations: succeed = False
        elif not filename: succeed = False
        elif basin_ids and len(basin_ids) != len(stations): succeed = False
        else:
            for s in stations:
                if len(s) != 2:
                    succeed = False
                    break

        if succeed:
            upstreams = []
            for s in stations:
                row, col = s[0], s[1]
                if base_resolution != 0.5: row, col = grid.transform_row_column(row, col, base_resolution, target_resolution=0.5)
                temp = Upstream.get_upstream_cells(row, col)
                if temp: upstreams.append([(row, col)]+temp)
                else: upstreams.append([(row, col)])

            geopoints = []
            for basin in upstreams:
                centroids = []
                for cell in basin: centroids.append(grid.find_centroid(cell[0], cell[1], deg_resolution=0.5))
                geopoints.append(grid.cell_vertices(centroids, degree_resolution=0.5))

            # creating shape file
            import shapefile as shp
            try:
                shp_basin = shp.Writer(shp.POLYGON)
                shp_basin.autoBalance = 1

                shp_basin.field('BASIN', 'N', 8)

                if add_wghm_cnum:
                    shp_basin.field('CNUM', 'N', 8)

                    for i in range(len(upstreams)):
                        basin = upstreams[i]
                        points = geopoints[i]

                        if basin_ids: basin_id = basin_ids[i]
                        else: basin_id = i + 1

                        for j in range(len(basin)):
                            cnum = grid.map_wghm_cell_number(basin[j][0], basin[j][1], base_resolution=0.5)
                            shp_basin.poly(parts=[points[j]], shapeType=shp.POLYGON)
                            shp_basin.record(basin_id, cnum)
                else:
                    for i in range(len(upstreams)):
                        basin = upstreams[i]
                        points = geopoints[i]

                        if basin_ids: basin_id = basin_ids[i]
                        else: basin_id = i + 1

                        for j in range(len(basin)):
                            shp_basin.poly(parts=[points[j]], shapeType=shp.POLYGON)
                            shp_basin.record(basin_id)

                if succeed:
                    shp_basin.save(filename)
                    ndx = filename.lower().find('.shp')
                    if ndx >= 0: filename = filename[:ndx]
                    filename += '.prj'
                    f = open(filename, 'w')
                    prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                    f.write(prj_string)
                    f.close()
            except: succeed = False

            if succeed and draw_flow_direction:
                shp_arrow = shp.Writer(shp.POLYLINE)
                shp_arrow.field('ARROW', 'N', 8)

                arrow_id = 1
                for basin in upstreams:
                    for cell in basin:
                        centroid = grid.find_centroid(cell[0], cell[1], deg_resolution=0.5)
                        arrow, pointer = Upstream.get_direction_line(centroid)
                        shp_arrow.line(parts=[arrow, pointer], shapeType=shp.POLYLINEM)
                        shp_arrow.record(arrow_id)
                        # shp_arrow.line(parts=[pointer], shapeType=shp.POLYLINE)
                        # shp_arrow.record(arrow_id)
                        arrow_id += 1

                ndx = filename.lower().find('.prj')
                if ndx >= 0: filename = filename[:ndx]
                else:
                    ndx = filename.lower().find('.shp')
                    if ndx >= 0: filename = filename[:ndx]
                filename = filename + '_arrows'
                shp_arrow.save(filename + '.shp')
                f = open(filename + '.prj', 'w')
                prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                f.write(prj_string)
                f.close()

        return succeed
