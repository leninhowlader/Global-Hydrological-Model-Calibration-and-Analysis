import sys, os, numpy as np
sys.path.append('..')
from utilities.globalgrid import GlobalGrid
from utilities.upstream import Upstream
from utilities.station import Station
from copy import deepcopy

model_version = 'wghm22d'
filename_staion = 'F:/mhasan/data/GlobalCDA/experiment/stations.txt'
filename_upstream = 'F:/mhasan/experiments/GlobalCDA/SA_mississippi/mississippi_subbasin_1234a4b45_upstream.txt'
filename_area = 'F:/mhasan/experiments/GlobalCDA/SA_mississippi/mississippi_subbasin_1234a4b45_area.txt'

def get_wghm_cell_area(wghm_cellnum):
    lat, lon = GlobalGrid.get_wghm_centroid(wghm_cellnum)
    row = GlobalGrid.find_row_number(lat)
    area = GlobalGrid.find_wghm_cellarea(row)

    return area

def main():
    # step: load global variables
    global model_version, filename_staion, filename_upstream, filename_area

    # step: set the reference grid file
    succeed = GlobalGrid.set_wghm_grid_lookup_table_filename('data/grid_%s.txt' % model_version)
    GlobalGrid.set_model_version(model_version)
    if not succeed: return 101

    # step: read station from station file
    stations = Station.read_stations(filename_staion)
    if not stations: return 102

    # step: read upstream cell-num and cell area
    upstream_cell, upstream_area = {}, {}
    for s in stations:
        sid = s[0]
        lon, lat = s[1], s[2]

        row, col = GlobalGrid.find_row_column(lat, lon)
        ucell = Upstream.get_upstream_cells(row, col)
        ucell = [(row, col)] + ucell

        wghm_cid, wghm_area = [], []
        for cell in ucell:
            row, col = cell
            wghm_cid.append(GlobalGrid.get_wghm_cell_number(row, col))
            wghm_area.append(GlobalGrid.find_wghm_cellarea(row))

        upstream_cell[sid] = wghm_cid
        upstream_area[sid] = wghm_area
    if not upstream_cell: return 103
    if not upstream_area: return 104

    # special operations required for Mississippi stations for experiment 1 to 4 of Nov 2018
    ucell_4127800, uarea_4127800 = deepcopy(upstream_cell[4127800]), deepcopy(upstream_area[4127800])
    #ucell_4127800, uarea_4127800 = upstream_cell[4127800], upstream_area[4127800]

    temp = []
    for key, value in upstream_cell.items():
        if key != 4127800:
            temp += value

    for i in reversed(range(len(upstream_cell[4127800]))):
        if upstream_cell[4127800][i] in temp:
            upstream_cell[4127800].pop(i)
            upstream_area[4127800].pop(i)

    # step: save upstream cell numbers into upstream cell file and upstream areas into upstream area file
    # add cell list and area list into temporary structures
    ucell, uarea = [], []

    # station 1: 4122900
    ucell.append(upstream_cell[4122900])
    uarea.append(upstream_area[4122900])

    # station 2: 4119800
    ucell.append(upstream_cell[4119800])
    uarea.append(upstream_area[4119800])

    # station 3: 4123050
    ucell.append(upstream_cell[4123050])
    uarea.append(upstream_area[4123050])

    # station 4a: 4125800
    ucell.append(upstream_cell[4125800])
    uarea.append(upstream_area[4125800])

    # station 4b: 4127800
    ucell.append(upstream_cell[4127800])
    uarea.append(upstream_area[4127800])

    # station 4: [station 4125800 + station 4127800]
    ucell.append(upstream_cell[4125800] + upstream_cell[4127800])
    uarea.append(upstream_area[4125800] + upstream_area[4127800])

    # station 5: [Whole 4127800 upstream basin]
    ucell.append(ucell_4127800)
    uarea.append(uarea_4127800)

    succeed = GlobalGrid.write_cell_info(filename_upstream, ucell, mode='w')
    if not succeed: return 105
    succeed = GlobalGrid.write_cell_info(filename_area, uarea, mode='w')
    if not succeed: return 106

    return 0

if __name__ == '__main__': main()