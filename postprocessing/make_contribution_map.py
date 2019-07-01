
import os, sys, numpy as np
sys.path.append('..')
from postprocessing.storagecontribution import StorageContribution as sc

basin = 'mississippi'
start_year = 2003
end_year = 2012
model_output_directory = 'F:/mhasan/Code&Script/wgap22d_home/OUTPUT'
output_directory = 'F:/mhasan/private/temp/contribution_map_test'
target_cells_from_file = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/input/%s_cindex_wghm22d.txt' % basin
output_type = 'binary'
sc.set_start_year(start_year)
sc.set_end_year(end_year)
sc.set_prediction_directory(model_output_directory)
sc.set_target_cells(target_cells_from_file)


def basin_sum(d:np.ndarray): return np.sum(d, axis=0)

from scipy.ndimage.interpolation import shift
def storage_change(d:np.ndarray):
    t1 = basin_sum(d)
    t2 = shift(t1, 1, cval=np.NaN)
    return t1 - t2
# succeed = sc.storage_contribution(model_output_directory, target_cells_from_file, start_year, end_year, output_directory,
#                                   output_filename_prefix='vicksburg_contribution', output_format='binary', contribution_type='both')

contrib_file = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/summary/%s_contrib_summary.csv'%basin
summary_file = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/summary/%s_contrib_summary.txt'%basin

contrib_file, summary_file = '', ''
succeed = sc.basin_scale_contribution_report(export_contributions_to_csv=contrib_file, export_summary_to_file=summary_file, print_on_screen=True)
#succeed = sc.contribution_to_total_volume(summary_type='all', output_filename_prefix='absolute_contribution', output_format='both')

target_dir = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/summary'
sc.export_prediction(target_dir, basin, summary_fun=storage_change)
sc.export_prediction(target_dir, basin, summary_fun=basin_sum)




# draw basin level predictions

pred_canopy = storage_change(sc.storage_variables['canopy']['predictions'])
pred_snow = storage_change(sc.storage_variables['snow']['predictions'])
pred_soil = storage_change(sc.storage_variables['soil']['predictions'])
pred_gw = storage_change(sc.storage_variables['groundwater']['predictions'])

pred_llake = storage_change(sc.storage_variables['locallake']['predictions'])
pred_glake = storage_change(sc.storage_variables['globallake']['predictions'])
pred_lwetland = storage_change(sc.storage_variables['localwetland']['predictions'])
pred_gwetland = storage_change(sc.storage_variables['globalwetland']['predictions'])
pred_reservoir = storage_change(sc.storage_variables['reservoir']['predictions'])
pred_river = storage_change(sc.storage_variables['river']['predictions'])
pred_sws = pred_llake + pred_glake + pred_lwetland + pred_gwetland + pred_reservoir + pred_river

varnams = ['canopy', 'snow', 'soil', 'groundwater', 'sws']
colors = []
for v in varnams: colors.append(sc.get_storage_color(v))

hi, lo = np.zeros(120), np.zeros(120)

c1 = pred_canopy.reshape(120, 1)
c2 = pred_snow.reshape(120, 1)
c3 = pred_soil.reshape(120, 1)
c4 = pred_gw.reshape(120, 1)
c5 = pred_sws.reshape(120, 1)

data = np.concatenate((c1, c2, c3, c4, c5), axis=1)

x = month_end_dates(2003, 2012)
hi, lo = np.zeros(120), np.zeros(120)
nrow, ncol = data.shape
for i in range(ncol): add_bar(data[:,i], color=colors[i])

filename = 'test_storage_change.png'
title = 'storage change'
sc.plot_storage_change(data, 2003, 2012, varnams, xdate_interval=3, ylim=(-200, 200), title=title, filename='')
