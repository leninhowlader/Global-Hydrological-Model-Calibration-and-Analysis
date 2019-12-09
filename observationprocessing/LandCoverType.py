
import sys
sys.path.append('..')
from utilities.fileio import FileInputOutput as io
from utilities.globalgrid import GlobalGrid

filename = '/media/sf_mhasan/private/month_data/ET_STD_WGAP_OUTPUT/Landcover/LCT_Brahmaputra.csv'

headers, data = io.read_flat_file(filename, separator=',', header=True)

land_cover_types = []
cell_groups = []
group_areas = []

for cell in data:
    row, col = GlobalGrid.find_row_column(cell[1], cell[0], degree_resolution=0.5)
    cnum = GlobalGrid.get_wghm_cell_number(row, col)
    area = GlobalGrid.find_wghm_cellarea(row, base_resolution=0.5)
    try:
        ndx = land_cover_types.index(cell[2])
        cell_groups[ndx].append(cnum)
        group_areas[ndx].append(area)
    except:
        land_cover_types.append(cell[2])
        cell_groups.append([cnum])
        group_areas.append([area])

for i in reversed(range(len(cell_groups))):
    if len(cell_groups[i]) < 10:
        cell_groups.pop(i)
        land_cover_types.pop(i)
        group_areas.pop(i)


for i in range(len(cell_groups)): print(land_cover_types[i], cell_groups[i])
filename = 'Brahmaputra.txt'

output_filename = 'LCT_Groups_' + filename
GlobalGrid.write_cell_info(output_filename, cell_groups, mode='w')
output_filename = 'LCT_areas_' + filename
GlobalGrid.write_cell_info(output_filename, group_areas, mode='w')
output_filename = 'LC_Types_' + filename
io.write_flat_file(output_filename, [land_cover_types], separator=',')