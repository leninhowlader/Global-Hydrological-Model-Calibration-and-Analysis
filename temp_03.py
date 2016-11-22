from utilities.grid import grid
from utilities.fileio import write_flat_file

data = []

cid = 0
for col in range(0, 720):
    for row in range(0, 360):
        data.append([cid])
        centroid = grid.find_centroid(row, col, deg_resolution=0.5)
        data[cid] += [centroid[1], centroid[0]]
        data[cid].append(grid.find_wghm_cellarea(row))
        centroid = grid.nearest_centroid(centroid[0], centroid[1], degree_resolution=1.0)
        data[cid] += [centroid[1], centroid[0]]
        cid += 1

config_filename = 'grid0p5deg.csv'
succeed = write_flat_file(config_filename, data, data_headers=['cid', 'long', 'lat', 'area', 'CLong1deg', 'CLat1deg'], separator=',')
print(succeed)