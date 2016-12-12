__author__ = 'mhasan'

from utilities.fileio import *
from utilities.grid import grid
import numpy as np
import shapefile as shp
from utilities.upstream import Upstream

# method of finding stations from the station file
def find_stations_from_file(station_file):
    headers, records = read_flat_file(station_file, separator=' ', header=False)

    stations = []
    if records:
        for record in records:
            if len(record) >= 3 and -90<=record[2]<=90 and -180<=record[1]<=180:
                stations.append((record[2], record[1]))

    return stations

station_file = 'STATIONS_brahmaputra.DAT'
stations = find_stations_from_file(station_file)
output_filename = 'brahmaputra_basin.shp'
direction_file_flag = False



upstream_cells = []
for station in stations:
    row, col = grid.find_row_column(station[0], station[1], degree_resolution=0.5)
    uscells = [(row, col)]
    uscells += Upstream.get_upstream_cells(row, col)
    upstream_cells.append(uscells)

for i in range(len(upstream_cells)):
    basin = upstream_cells[i]
    for j in range(len(basin)):
        basin[j] = grid.find_centroid(basin[j][0], basin[j][1], deg_resolution=0.5)

succeed = False
try:
    s_a = shp.Writer(shp.POLYLINE)
    s_a.field('ARROW', 'N', 8)

    s_b = shp.Writer(shp.POLYGON)
    s_b.field('BASIN', 'N', 8)

    fid = 0
    basin_id = 0
    arrow_id = 0
    for basin in upstream_cells:
        points = grid.cell_vertices(basin, degree_resolution=0.5)

        for point in points:
            s_b.autoBalance = 1 # ensures gemoetry and attributes match
            s_b.poly(parts=[point], shapeType=shp.POLYGON)
            s_b.record(basin_id)
            fid += 1

        for centroid in basin:
            arrow, pointer = Upstream.get_direction_line(centroid)
            s_a.line(parts=[arrow], shapeType=shp.POLYLINE)
            s_a.record(arrow_id)
            s_a.line(parts=[pointer], shapeType=shp.POLYLINE)
            s_a.record(arrow_id)
            arrow_id += 1

        basin_id += 1
    s_b.save(output_filename)
    succeed = True
    #s_a.save('direction.shp')
except: succeed = False

# write projection files
if succeed:
    try:
        ndx = output_filename.lower().find('.shp')
        if ndx >= 0: output_filename = output_filename[:ndx]
        output_filename += '.prj'
        f = open(output_filename, 'w')
        prj_string ='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        f.write(prj_string)
        f.close()
    except: pass

if direction_file_flag:
    output_filename = 'direction'
    try:
        output_filename += '.prj'
        f = open(output_filename, 'w')
        prj_string ='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        f.write(prj_string)
        f.close()
    except: pass


print(succeed)