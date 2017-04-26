
import sys
sys.path.append('..')
from utilities.upstream import Upstream
from utilities.grid import grid
from utilities.station import  Station


station_file = 'STATIONS.DAT'
s = Station.read_stations(station_file)

print(s)
row, col = grid.find_row_column(s[1][2], s[1][1])
cells = Upstream.get_upstream_cells(row, col)
cells = [(row, col)] + cells
area = 0
for c in cells:
    area += grid.find_wghm_cellarea(c[0])
print(area)