import shapefile as shp
import sys
from utilities.grid import grid



config_filename = 'ganges_upstream.txt'
up_cells = grid.read_groupfile(config_filename)[0]

for i in range(len(up_cells)):
    up_cells[i] = grid.map_centroid_from_wghm_cell_number(up_cells[i])

#sys.setrecursionlimit(1500)
print(up_cells)
up_cells = grid.combine_grid_cells(up_cells, deg_resolution=0.5)
# up_cells = grid.bubble_sort(up_cells)
#print(up_cells)
# print(up_cells)
output_filename = 'ganges_basin.shp'
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
    s_b.save(output_filename)

    print('shape has been created!!')

except: pass
try:
    ndx = output_filename.lower().find('.shp')
    if ndx >= 0: output_filename = output_filename[:ndx]
    output_filename += '.prj'
    f = open(output_filename, 'w')
    prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
    f.write(prj_string)
    f.close()
except:
    pass