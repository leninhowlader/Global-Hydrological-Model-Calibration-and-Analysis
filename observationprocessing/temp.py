import sys, os
sys.path.append('..')

from utilities.station import Station
from utilities.grid import grid
from utilities.upstream import Upstream

filename = 'output/brahmaputra_upstreams_bahadurabad.txt'
cells = grid.read_groupfile(filename, data_type=int)


print(cells)