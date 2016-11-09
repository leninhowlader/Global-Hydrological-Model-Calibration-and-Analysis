from utilities.upstream import Upstream
from utilities.grid import grid

row,col = grid.find_row_column(24.25, 88.75)
basin = Upstream.get_upstream_cells(row, col)

area = 0
for c in basin:
    area += grid.find_wghm_cellarea(c[0])
print(area)