'''
Author: H.M. Mehedi Hasan
Date: 11 March 2017

This script will produce inflow map from the outflow dataset.


'''
home_directory = '../wgap_home'
output_directory = 'OUTPUT'
prediction_filename = 'G_RIVER_AVAIL_[YEAR].12.UNF0'
degree_resolution = 0.5
flag_station_output_only = True
station_filename = 'STATIONS.DAT'
file_endian = 2
start_year = 1989
end_year = 2005


import sys, numpy as np, os, shapefile as shp
sys.path.append('..')
from utilities.upstream import Upstream
from calibration.wgapoutput import WGapOutput
from utilities.grid import grid
from copy import deepcopy
from utilities.station import Station
from calibration.enums import FileEndian

# GLOBAL VARIABLES
direction_map = None
wgmap_GeoPoints = []
wgmap_RowColumn = []
target_WgCells = []


# set output file endian type
if file_endian == 2: file_endian = FileEndian.big_endian
else: file_endian = FileEndian.little_endian

def generate_target_cells():
    global station_filename, target_WgCells

    upstreams = []
    if home_directory and station_filename: station_filename = os.path.join(home_directory, station_filename)
    if os.path.exists(station_filename):
        stations = Station.read_stations(station_filename)

        for station in stations:
            row, col = grid.find_row_column(station[2], station[1], degree_resolution=0.5)
            uscells = [(row, col)]
            uscells += Upstream.get_upstream_cells(row, col)
            upstreams += uscells

        for i in range(len(upstreams)):
            row, col = upstreams[i]
            cnum = grid.map_wghm_cell_number(row, col, base_resolution=0.5)
            upstreams[i] = cnum

        for i in reversed(range(len(upstreams))):
            for j in range(i):
                if upstreams[i] == upstreams[j]:
                    upstreams.pop(i)
                    break

    if upstreams:
        target_WgCells = upstreams
        return True
    else: return False

def create_inflow_shapefile(filename, inflow_data, projection_file=True):
    global wgmap_GeoPoints, wgmap_RowColumn, target_WgCells

    succeed = True
    try:
        inflow_shp = shp.Writer(shp.POLYGON)
        inflow_shp.field('CID', 'N', '8')
        inflow_shp.field('INFLOW', 'N', '20', 15)

        if not target_WgCells:
            for i in range(len(wgmap_GeoPoints)):
                point = wgmap_GeoPoints[i]
                inflow_shp.autoBalance = 1 # ensures gemoetry and attributes match
                inflow_shp.poly(parts=[point], shapeType=shp.POLYGON)

                row, col = wgmap_RowColumn[i]
                cid = i + 1
                inflow = inflow_data[row][col]
                inflow_shp.record(cid, inflow)
        else:
            for cnum in target_WgCells:
                point = wgmap_GeoPoints[cnum-1]
                inflow_shp.autoBalance = 1  # ensures gemoetry and attributes match
                inflow_shp.poly(parts=[point], shapeType=shp.POLYGON)

                row, col = wgmap_RowColumn[cnum-1]
                inflow = inflow_data[row][col]
                inflow_shp.record(cnum, inflow)

        inflow_shp.save(filename)
    except: succeed = False

    if succeed and projection_file:
        try:
            ndx = filename.lower().find('.shp')
            if ndx >= 0: filename = filename[:ndx]
            filename += '.prj'
            f = open(filename, 'w')
            prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
            f.write(prj_string)
            f.close()
        except: succeed = False

    return succeed

def find_next_row_column(direction, row, col):
    '''
    Directions:
    dvalue  desc    (row, col)
    0	    River mouth to ocean, internal sink
    1	    E	    ( 0, +1)
    2	    SE	    (+1, +1)
    4	    S	    (+1,  0)
    8	    SW	    (+1, -1)
    16	    W	    ( 0, -1)
    32	    NW	    (-1, -1)
    64	    N	    (-1,  0)
    128	    NE	    (-1, +1)
    -9999	Ocean
    '''
    if direction == 1: return row, col+1
    elif direction == 2: return row+1, col+1
    elif direction == 4: return row+1, col
    elif direction == 8: return row+1, col-1
    elif direction == 16: return row, col-1
    elif direction == 32: return row-1, col-1
    elif direction == 64: return row-1, col
    elif direction == 128: return row-1, col+1
    else: return None, None

def main():
    global direction_map, wgmap_GeoPoints, wgmap_RowColumn, degree_resolution, \
        flag_station_output_only, target_WgCells

    succeed = True

    # if the flag for producing output for specific station is set on, read target cells
    if flag_station_output_only: succeed = generate_target_cells()

    # read flow direction map
    Upstream.read_flow_data()
    direction_map = np.array(Upstream.flow_direction_data)

    # read and translate WaterGAP grid into row-column pairs
    wgmap_centroids = grid.get_wghm_world_grid_centroids()
    wgmap_GeoPoints = grid.cell_vertices(wgmap_centroids, degree_resolution=degree_resolution)
    for i in range(len(wgmap_centroids)):
        wgmap_RowColumn.append(grid.find_row_column(wgmap_centroids[i][0], wgmap_centroids[i][1], degree_resolution=degree_resolution))

    # initialize empty inflow map with 0 values
    GFactor = int(1 / degree_resolution)
    zero_inflows = np.zeros((180 * GFactor, 360 * GFactor))

    if succeed:

        for year in range(start_year, end_year+1):
            # read WaterGAP prediction for outflow
            filename = os.path.join(home_directory, output_directory, prediction_filename.replace('[YEAR]', str(year)))
            data = WGapOutput.read_unf(filename, file_endian=file_endian)

            if data and len(data) == len(wgmap_RowColumn):

                for m in range(12):
                    # make a deepcopy of inflow map with zero values
                    inflows = deepcopy(zero_inflows)

                    if not target_WgCells:
                        for i in range(len(data)):
                            row, col = wgmap_RowColumn[i]
                            dValue = direction_map[row][col]
                            if dValue not in [-9999, 0]:
                                row, col = find_next_row_column(dValue, row, col)
                                if row != None and col != None: inflows[row][col] += data[i][m]
                    else:
                        for cnum in target_WgCells:
                            row, col = wgmap_RowColumn[cnum-1]
                            dValue = direction_map[row][col]
                            if dValue not in [-9999, 0]:
                                row, col = find_next_row_column(dValue, row, col)
                                if row != None and col != None:
                                    inflows[row][col] += data[cnum-1][m]

                    #if 1: break
                    # write output into a shape file
                    month = m + 1
                    filename = '/media/sf_mhasan/private/temp/inflow_map/inflow_%d_%s.shp' % (year, str(month).rjust(2, '0'))
                    create_inflow_shapefile(filename, inflows)
                    break
            else: break
            break

if __name__ == '__main__':
    main()