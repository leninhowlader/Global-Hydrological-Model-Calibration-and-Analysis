__author__ = 'mhasan'

import sys, os, numpy as np
sys.path.append('..')

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

        d = np.loadtxt(direction_datafile, skiprows=6)
        if d.shape == (360, 720): Upstream.flow_direction_data = d.tolist()
        else:
            message = 'Flow direction data could not be retrieved. Either "%s" does not exists or has bad-format.' % direction_datafile
            print(message)
            exit(os.EX_NOINPUT)

    # method of finding flow-direction for a given cell
    @staticmethod
    def get_flow_direction(row, col):
        if not Upstream.flow_direction_data: Upstream.read_flow_data()

        return Upstream.flow_direction_data[row][col]

    # method of finding if a given cell is a upstream cell for another reference cell;
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
