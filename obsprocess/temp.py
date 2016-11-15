import sys
sys.path.append('..')
from utilities.grid import grid
import shapefile as shp


sub_basin = grid.read_groupfile('sub_basin_ganges_upstream.txt')[0]
#print(sub_basin)
# centriods = []
# for i in range(len(sub_basin)):
#     centriods.append(grid.map_centroid_from_wghm_cell_number(sub_basin[i]))

area = []
for cell in sub_basin:
    centriod = grid.map_centroid_from_wghm_cell_number(cell)
    row, col = grid.find_row_column(centriod[0], centriod[1])
    area.append(grid.find_wghm_cellarea(row))
print(len(area), len(sub_basin))

grid.write_groupfile('sub_basin_ganges_area.txt', [area] )
succeed = False
output_filename = 'sub_basin_ganges.shp'
try:
    s_b = shp.Writer(shp.POLYGON)
    s_b.field('CNUM', 'N', 8)


    points = grid.cell_vertices(centriods, degree_resolution=0.5)
    for i in range(len(points)):
        point = points[i]
        s_b.autoBalance = 1 # ensures gemoetry and attributes match
        s_b.poly(parts=[point], shapeType=shp.POLYGON)
        s_b.record(sub_basin[i])

    s_b.save(output_filename)

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

print(succeed)