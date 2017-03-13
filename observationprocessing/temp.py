import sys, os
sys.path.append('..')

from utilities.station import Station
from utilities.grid import grid
from utilities.upstream import Upstream

station_file = 'STATIONS_G4B3.DAT'

stations = Station.read_stations(station_file=station_file)

basins = []
for station in stations:
    snum, lon, lat = station
    row, col = grid.find_row_column(lat, lon, degree_resolution=0.5)
    #cnum = grid.map_wghm_cell_number(row, col, base_resolution=0.5)

    bCells = [(row, col)]
    bCells += Upstream.get_upstream_cells(row, col)
    basins.append(bCells)

for basin in basins:
    area = 0
    for cell in basin:
        row, col = cell
        cnum = grid.map_wghm_cell_number(row, col)
        area += grid.find_wghm_cellarea(row)

    print(area)
