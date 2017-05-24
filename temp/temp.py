import sys, numpy as np, os
sys.path.append('..')
from calibration.predstat import SeasonalStatistics as ps
from utilities.fileio import read_flat_file
from calibration.configuration import Configuration


filename = 'brahmaputra_bahadurbad_2646100_configuration.txt'

config = Configuration.read_configuration_file(filename)
if config.is_okay(): print('success!!')

data_cloud = config.obs_variables[0].data_cloud

stats, results = ps.seasonal_summary(data_cloud)
print(stats)

# headers = ['average_seasonal_mean', '50pr_seasonal_mean', '75pr_seasonal_mean', '80pr_seasonal_mean', '90pr_seasonal_mean',
#            'stddev_seasonal_mean', 'min_seasonal_mean', 'max_seasonal_mean', 'range_seasonal_mean',
#            'average_seasonal_deviation', '50pr_seasonal_deviation', '75pr_seasonal_deviation', '80pr_seasonal_deviation', '90pr_seasonal_deviation',
#            'stddev_seasonal_deviation', 'min_seasonal_deviation', 'max_seasonal_deviation', 'range_seasonal_deviation',
#            'average_seasonal_peak', '50pr_seasonal_peak', '75pr_seasonal_peak', '80pr_seasonal_peak', '90pr_seasonal_peak',
#            'stddev_seasonal_peak', 'min_seasonal_peak', 'max_seasonal_peak', 'range_seasonal_peak',
#            'average_peak_period', '50pr_peak_period', '75pr_peak_period', '80pr_peak_period', '90pr_peak_period',
#            'stddev_peak_period', 'min_peak_period', 'max_peak_period', 'range_peak_period',
#            'average_seasonal_bottom', '50pr_seasonal_bottom', '75pr_seasonal_bottom', '80pr_seasonal_bottom', '90pr_seasonal_bottom',
#            'stddev_seasonal_bottom', 'min_seasonal_bottom', 'max_seasonal_bottom', 'range_seasonal_bottom',
#            'average_bottom_period', '50pr_bottom_period', '75pr_bottom_period', '80pr_bottom_period', '90pr_bottom_period',
#            'stddev_bottom_period', 'min_bottom_period', 'max_bottom_period', 'range_bottom_period',
#            'average_seasonal_amplitude', '50pr_seasonal_amplitude', '75pr_seasonal_amplitude', '80pr_seasonal_amplitude', '90pr_seasonal_amplitude',
#            'stddev_seasonal_amplitude', 'min_seasonal_amplitude', 'max_seasonal_amplitude', 'range_seasonal_amplitude',
#            'jan_mean', 'jan_stddev', 'jan_min', 'jan_max', 'jan_range', 'feb_mean', 'feb_stddev', 'feb_min', 'feb_max', 'feb_range',
#            'mar_mean', 'mar_stddev', 'mar_min', 'mar_max', 'mar_range', 'apr_mean', 'apr_stddev', 'apr_min', 'apr_max', 'apr_range',
#            'may_mean', 'may_stddev', 'may_min', 'may_max', 'may_range', 'jun_mean', 'jun_stddev', 'jun_min', 'jun_max', 'jun_range',
#            'jul_mean', 'jul_stddev', 'jul_min', 'jul_max', 'jul_range', 'aug_mean', 'aug_stddev', 'aug_min', 'aug_max', 'aug_range',
#            'sep_mean', 'sep_stddev', 'sep_min', 'sep_max', 'sep_range', 'oct_mean', 'oct_stddev', 'oct_min', 'oct_max', 'oct_range',
#            'nov_mean', 'nov_stddev', 'nov_min', 'nov_max', 'nov_range', 'dec_mean', 'dec_stddev', 'dec_min', 'dec_max', 'dec_range']
#print(len(headers))


for key in results.keys(): print(key, results[key], sep=': ')
stats, results = ps.monthly_summary(data_cloud)

for key in results.keys(): print(key, results[key], sep=': ')
if True: exit(0)

filename = 'discharge_km3pm.csv'
h, data = read_flat_file(filename, separator=',', header=False)
data = np.array(data)
# dt = data[:,[1,2,3]]
#
# peaks = []
# peak_months = []
# for year in np.unique(dt[:,0]):
#     ndx = np.where(dt[:,0]==year)
#     d = dt[:,2][ndx]
#     if len(d) >= 8:
#         mx, mn = max(d), min(d)
#         peaks.append(mx)
#         peak_months.append(dt[:,1][ndx][np.where(d==mx)][0])


dt = ps.seasonal_behaviours(data, year_column=1, month_column=2, value_column=3)
results = ps.seasonal_behaviour_summary(dt[:, 1:])
print(list(results[0]))

print(ps.seasonal_behaviour_summary(dt))

# filename = '/media/sf_mhasan/private/month_data/peaks_and_depressions.csv'
# ps.save_numpy_data(filename, dt, delimiter=',',fmt=('%d','%s','%d','%s','%d','%s'))
#np.savetxt(filename, dt, header=('year,peak,peak_moonth,bottom,bottom_month,amplitude'), delimiter=',', fmt=('%d','%s','%d','%s','%d','%s'), comments='')

# seasonal peaks and depressions: mean, mode, 70 percentile, 80 p percentile, 90 percentile, std dev
# periods of peaks and depressions: mean, mode, range
# seasonal amplitudes: mean, mode, 70 percentile, 80 percentile, 90 percentile
# later on also find contribution ...


ps.test()