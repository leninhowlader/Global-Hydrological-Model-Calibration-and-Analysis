import sys, numpy as np
sys.path.append('..')
# sys.path.append('F:/mhasan/PyScript')
from utilities.globalgrid import GlobalGrid
GlobalGrid.set_model_version('wghm22d')
from utilities.upstream import Upstream
from wgap.wgapio import WaterGapIO


upstream_filename = 'F:/mhasan/experiments/GlobalCDA/SA_mississippi/replication_one/input/mississippi_subbasin_1234a4b45_upstream.txt'
basins = GlobalGrid.read_cell_info(upstream_filename, data_type=int)
basin_names = ['Hermann', 'Alton', 'Metropolis', 'Little Rock', 'Vicksburg', 'Little Rock and Vicksburg', 'Mississippi']

#
# basin = basins[-1]
# filename = 'F:/mhasan/Code&Script/ProjectWGHM/postprocessing/input/upstream_mississippi.txt'
# grid.write_groupfile(filename, [basin])

# calculate Ground Water Factor
# from groundwater import GroundWater
# gw_factor = GroundWater.get_recharge_factor()


# # basin_id = 1
# for basin_id in [1,2,3,4,5,7]:
#
#     basin = np.array(basins[basin_id-1])
#
#
#
#
#     filename = 'F:/mhasan/data/GlobalCDA/ground_water_recharge_factor/gw_recharge_factor_%s.shp' % basin_names[basin_id-1].replace(' ', '_')
#     succeed = Upstream.create_shape_with_data(filename, basin_id=basin_id, data=gw_factor[basin-1], wghm_cnum_list=basin)
#     print(succeed)

# from matplotlib import pyplot as plt
# basin = np.array(basins[-1])
# gwf = gw_factor[basin-1]
#
# fig = plt.figure(figsize=(6,4))
# ax = plt.subplot(1, 1, 1)
# ax.set_xlabel('Groundwater Recharge Factor')
# ax.set_ylabel('Frequency')
# plt.hist(gwf, bins=50, cumulative=False, histtype='bar', normed=False)
# filename = 'F:/mhasan/data/GlobalCDA/ground_water_recharge_factor/histogram.png'
# fig.tight_layout()
# fig.savefig(filename)
# plt.show()

# for bid in range(len(basins)):
#     if bid != 5:
#         basin = np.array(basins[bid])
#         gwf = gw_factor[basin-1]
#         print('%s%0.3f\t%0.3f\t%0.3f' %(basin_names[bid].ljust(15, ' '), np.min(gwf), np.max(gwf), np.percentile(gwf, 0.5)))



# arid_humid = WaterGapIO.read_unf('INPUT/G_ARID_HUMID.UNF2')
# basin = np.array(basins[-1])
# filename = 'F:/mhasan/data/GlobalCDA/input_data/arid_humid.shp'
# succeed = Upstream.create_shape_with_data(filename, basin_id=5, data=arid_humid[basin-1], wghm_cnum_list=basin)
# print(succeed)

# for bid in range(len(basins)):
#     basin = np.array(basins[bid])
#     name = basin_names[bid]
#     ah = arid_humid[basin-1]
#     per_arid = np.sum(ah)/len(basin)
#     per_humid = (len(basin) - np.sum(ah))/len(basin)
#     print('%s\t%0.3f\t%0.3f' % (name.ljust(15, ' '), per_arid, per_humid))


filename = 'F:/mhasan/Code&Script/wgap22d_home/INPUT/G_LANDCOVER.UNF1'
land_cover = WaterGapIO.read_unf(filename)

# for basin_id in [1,2,3,4,5,7]:
#     basin = np.array(basins[basin_id-1])
#
#     filename = 'F:/mhasan/data/GlobalCDA/land_cover_22d/landcover_%s.shp' % basin_names[basin_id-1].replace(' ', '_')
#     succeed = Upstream.create_shape_with_data(filename, basin_id=basin_id, data=land_cover[basin-1], wghm_cnum_list=basin)
#     print(succeed)
#
#
# basin = np.array(basins[-1])
#
# from matplotlib import pyplot as plt
# fig = plt.figure(figsize=(6,4))
# ax = plt.subplot(1, 1, 1)
# ax.set_xlabel('Groundwater Recharge Factor')
# ax.set_ylabel('Frequency')
# plt.hist(land_cover[basin-1], bins=50, cumulative=False, histtype='bar', normed=False)
# filename = 'F:/mhasan/data/GlobalCDA/land_cover_22d/histogram.png'
# fig.tight_layout()
# fig.savefig(filename)
# plt.show()
#
# d, c = np.histogram(land_cover[basin-1])

filename = 'F:/mhasan/Code&Script/wgap22d_home/INPUT/G_TAWC.UNF0'
tawc = WaterGapIO.read_unf(filename)

basin = np.array(basins[-1])
tawc_mis = tawc[basin-1]
lc_mis = land_cover[basin-1]

lctype = [1, 4, 5, 8]
lcrootd = [2, 2, 2, 1.5]

for i in range(len(lctype)):
    ndx = np.where(lc_mis==lctype[i])
    tawc_mis[ndx] = tawc_mis[ndx] * lcrootd[i]

filename = 'F:/mhasan/data/GlobalCDA/max_soil_capacity_22d/max_soil_water_capacity.shp' # % basin_names[basin_id-1].replace(' ', '_')
succeed = Upstream.create_shape_with_data(filename, basin_id=5, data=tawc_mis, wghm_cnum_list=basin)
print(succeed)

from matplotlib import pyplot as plt
fig = plt.figure(figsize=(6,4))
ax = plt.subplot(1, 1, 1)
ax.set_xlabel('Maximum Soil Storage Capacity (mm)')
ax.set_ylabel('Frequency')
plt.hist(tawc_mis, bins=50, cumulative=False, histtype='bar', normed=False)
filename = 'F:/mhasan/data/GlobalCDA/max_soil_capacity_22d/histogram.png'
fig.tight_layout()
fig.savefig(filename)
plt.show()