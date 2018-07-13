#!/usr/bin/python3

flowdirection_filename = 'flow-direction.asc'
wghm_areafile = 'GAREA.UNF0'
reference_cell_longitude = 88.75
reference_cell_latitude = 24.25
print_cell_list = True
output_filename = ''


import os, csv, struct

class Upstream:
    data_flowdirection = []
    directions = [1, 2, 4, 8, 16, 32, 64, 128]
    flow_direction_file = 'flow-direction.asc'

    @staticmethod
    def set_flow_direction_filename(filename): Upstream.flow_direction_file = filename

    @staticmethod
    def read_flowdirection_dataset():
        succeed = True
        try:
            f = open(Upstream.flow_direction_file, 'r')
            reader = csv.reader(f, delimiter=' ')
            Upstream.data_flowdirection = [list(map(int, rec[:720])) for rec in list(reader)[6:]]
            if len(Upstream.data_flowdirection) != 360: succeed = False
        except: succeed = False
        return succeed

    @staticmethod
    def find_flow_direction(row, col): return Upstream.data_flowdirection[row][col]

    @staticmethod
    def does_neighbour_flow_into(neighbour_row, neighbour_col, incoming_direction):
        if Upstream.find_flow_direction(neighbour_row, neighbour_col) == incoming_direction: return True
        else: return False

    @staticmethod
    def find_neighbour_at_incoming_direction(reference_cell_row, reference_cell_col, incoming_direction):
        if incoming_direction == 1: return reference_cell_row, reference_cell_col - 1
        elif incoming_direction == 2: return reference_cell_row - 1, reference_cell_col - 1
        elif incoming_direction == 4: return reference_cell_row - 1, reference_cell_col
        elif incoming_direction == 8: return reference_cell_row - 1, reference_cell_col + 1
        elif incoming_direction == 16: return reference_cell_row, reference_cell_col + 1
        elif incoming_direction == 32: return reference_cell_row + 1, reference_cell_col + 1
        elif incoming_direction == 64: return reference_cell_row + 1, reference_cell_col
        else: return reference_cell_row + 1, reference_cell_col - 1

    @staticmethod
    def find_immediate_neighbours(refc_row, refc_col):   # refc_row and refc_col are row and col num of ref cell respectively
        return [Upstream.find_neighbour_at_incoming_direction(refc_row, refc_col, d) for d in Upstream.directions]

    @staticmethod
    def find_upstream_cells(refc_row, refc_col):
        upstream_cells = []
        neighbours = Upstream.find_immediate_neighbours(refc_row, refc_col)
        for i in range(len(neighbours)):
            refc_row = neighbours[i][0]
            refc_col = neighbours[i][1]

            if Upstream.does_neighbour_flow_into(refc_row, refc_col, Upstream.directions[i]):
                upstream_cells.append((refc_row, refc_col))
                temp = Upstream.find_upstream_cells(refc_row, refc_col)
                if temp: upstream_cells = upstream_cells + temp
        return upstream_cells

    @staticmethod
    def is_ready():
        if not Upstream.data_flowdirection: Upstream.read_flowdirection_dataset()
        if not Upstream.data_flowdirection: return False
        else: return True

class Grid:
    area_filename = 'GAREA.UNF0'
    areas_0p5_cells = []

    @staticmethod
    def set_area_filename(filename): Grid.area_filename = filename

    @staticmethod
    def read_0p5_latitude_cell_area():
        succeed = True
        try:
            f = open(Grid.area_filename, 'rb')
            bsize, bformat = 4*360, '>' + 'f'*360
            block = f.read(bsize)
            temp = struct.unpack(bformat, block)
            if temp and len(temp) == 360: Grid.areas_0p5_cells = list(temp)
        except: succeed = False
        return succeed

    @staticmethod
    def find_area(row):
        if 0<=row<360: return Grid.areas_0p5_cells[row]
        else: return None

    @staticmethod
    def find_column_number(longitude, degree_resolution=0.5):
        if -180 <= longitude <= 180:
            if longitude == 180: return int(((longitude + 180) // degree_resolution) - 1)
            else: return int((longitude + 180) // degree_resolution)
        else: return None

    @staticmethod
    def find_row_number(latitude, degree_resolution=0.5):
        if -90 <= latitude <= 90:
            if latitude == -90: return int((abs(latitude - 90) // degree_resolution) - 1)
            else: return int(abs(latitude - 90) // degree_resolution)
        else: return None

    @staticmethod
    def find_row_column(latitude, longitude, degree_resolution=0.5):
        return Grid.find_row_number(latitude, degree_resolution), Grid.find_column_number(longitude, degree_resolution)

    @staticmethod
    def find_centroid(row, column, deg_resolution=0.5):
        longitude = (column * deg_resolution) - 180 + (deg_resolution / 2)
        latitude = -(row * deg_resolution) + 90 - (deg_resolution / 2)
        if -90 <= latitude <= 90 and -180 <= longitude <= 180: return latitude, longitude
        else: return None, None

    @staticmethod
    def is_okay():
        if not Grid.areas_0p5_cells: Grid.read_0p5_latitude_cell_area()
        if not Grid.areas_0p5_cells: return False
        else: return True

def main():
    # step-01: get global parameters and transfer to class variables (if necessary)
    global flowdirection_filename, wghm_areafile, reference_cell_longitude, reference_cell_latitude
    global print_cell_list, output_filename
    if flowdirection_filename: Upstream.set_flow_direction_filename(flowdirection_filename)
    if wghm_areafile: Grid.set_area_filename(wghm_areafile)

    # step-02: check input
    succeed = False
    if -90<=reference_cell_latitude<=90 and -180<=reference_cell_longitude<=180: succeed = True
    if succeed:
        if Upstream.is_ready() and Grid.is_okay(): succeed = True
    if not succeed:
        print('The program can not find upstream. Please check input parameters.')
        exit(os.EX_NOINPUT)

    # step-03: generate upstream and find area of each upstream cell
    centroids, carea = [], []
    basin_area = 0
    if succeed:
        # find the row and col num for the reference geo-location
        row, col = Grid.find_row_column(reference_cell_latitude, reference_cell_longitude)
        # find upstream cells
        upstream_cells = Upstream.find_upstream_cells(row, col)
        # add the first cell into the upstream list
        upstream_cells = [(row, col)] + upstream_cells

        # find cell area for each upstream cell
        carea = [Grid.find_area(cell[0]) for cell in upstream_cells]
        # calculate total basin area
        basin_area = sum(carea)

        # find geo-centroid of each upstream cells
        centroids = [Grid.find_centroid(c[0], c[1]) for c in upstream_cells]

        if not (centroids and carea and len(centroids) == len(carea)): succeed = False


    # step-04: prepare for output
    lines = []
    if succeed:
        lines.append('Summary Report:')
        lines.append('\tstarting point: LAT %f\tLON %f' % (reference_cell_latitude, reference_cell_longitude))
        lines.append('\ttotal number of grid cells: %d' % len(centroids))
        lines.append('\ttotal area: %0.5f' % basin_area)

        # extent of the basin
        min_lat, max_lat = min([c[0] for c in centroids]) + 0.25, max([c[0] for c in centroids]) + 0.25
        min_lon, max_lon = min([c[1] for c in centroids]) + 0.25, max([c[1] for c in centroids]) + 0.25
        lines.append('\tbasin extent: TL-(Lat %0.2f Lon %0.2f) BL-(%0.2f %0.2f) BR-(%0.2f %0.2f) TR-(%0.2f %0.2f)' %
                     (max_lat, min_lon, min_lat, min_lon, min_lat, max_lon, max_lat, max_lon))

        lines.append('\nArea of Each Cell:\n%s%s%s' % ('Latitude'.ljust(12), 'Longitude'.ljust(12), 'Area (km sq)'.rjust(12)))
        if print_cell_list:
            for i in range(len(centroids)):
                lines.append(('%0.2f'%centroids[i][0]).ljust(12) + ('%0.2f'%centroids[i][1]).ljust(12) + ('%0.3f'%carea[i]).rjust(12))

        if not lines: succeed = False

    # step-04: print result either in file or in screen
    if succeed:
        if output_filename:
            try:
                f = open(output_filename, 'w')
                for line in lines: f.write(line + '\n')
                f.close()
            except: succeed = False
        else:
            for line in lines: print(line)

    if succeed:
        print('Program ends successfully.')
        exit(os.EX_OK)
    else:
        print('Program failed!!')
        exit(os.EX_DATAERR)


if __name__ == '__main__': main()