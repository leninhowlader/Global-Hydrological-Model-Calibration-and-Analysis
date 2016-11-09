import shapefile as shp
import sys
from grid import grid



filename = 'upstream_brahmaputra.txt'
up_cells = grid.read_groupfile(filename)[0]

for i in range(len(up_cells)):
    up_cells[i] = grid.map_centroid_from_wghm_cell_number(up_cells[i])

#sys.setrecursionlimit(1500)
print(up_cells)
up_cells = grid.combine_grid_cells(up_cells, deg_resolution=0.5)
# up_cells = grid.bubble_sort(up_cells)
#print(up_cells)
# print(up_cells)
try:
    points = []
    for ucg in up_cells:
        pts = []
        for uc in ucg: pts.append((uc[1], uc[0]))
        pts.append((ucg[-1][1], ucg[-1][0]))
        points.append(pts)

    s_b = shp.Writer(shp.POLYGON)
    s_b.field('BASIN', 'N', 8)

    fid = 0
    basin_id = 0
    arrow_id = 0



    s_b.autoBalance = 1 # ensures gemoetry and attributes match
    for pt in points:
        s_b.poly(parts=[pt], shapeType=shp.POLYGON)
        s_b.record(fid)
        fid += 1
    s_b.save('brahmaputra_001.shp')

    print('shape has been created!!')

except: pass