__author__ = 'mhasan'

import sys,os
import numpy as np

sys.path.append('..')
from utilities.grid import grid
from utilities.upstream import Upstream
from utilities.station import Station

from calibration.configuration import Configuration
from calibration.watergap import WaterGAP

config = Configuration.read_configuration_file('ganges_configuration.txt')
print(config.parameters)
# Upstream.set_flow_direction_file('preparation/flow-direction.asc')

# filename = ''# 'input/STATIONS.DAT'
# stations = Station.read_stations(filename)
# print(stations)

# station = stations[0]
# # find upstream cells
# row, col = grid.find_row_column(station[0],station[1], degree_resolution=0.5)
# up_cells = Upstream.get_upstream_cells(row, col)
#
# a = np.array(up_cells)
# # x_max, x_min, y_max, y_min = 0.0,0.0,0.0,0.0
# #print(a)
# print(a.shape)
print(config.is_okay())
print(WaterGAP.is_okay())