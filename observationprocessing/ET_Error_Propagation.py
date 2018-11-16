import numpy as np, os
from calendar import monthrange
from scipy import stats

os.chdir(os.path.join(os.getcwd(), 'observationprocessing'))

def error_propagation(errors, mode=0):
    if not type(errors) is np.ndarray: errors = np.array(errors)
    if mode==1:
        err = np.sqrt(np.sum(errors**2))
    else:
        n = len(errors)
        err = np.sqrt(np.sum((errors/n)**2))
    return err

f = 'output/brahmaputra_bahadurabad_ET_Mueller2013_mean_mm_daily.csv'
means = np.loadtxt(f, delimiter=',')

f = 'output/brahmaputra_bahadurabad_ET_Mueller2013_sd_mm_daily.csv'
sds = np.loadtxt(f, delimiter=',')

days = [monthrange(y,m)[1] for y,m in means[:,1:3].astype('int')]

month_sums = days * means[:,3]
errors = np.array([error_propagation([sds[i,3]]*days[i], mode=1) for i in range(len(days))])

# mean monthly values
mons = np.unique(means[:,2]).astype('int')

month_means, month_errors = [], []
for i in mons:
    ndx = np.where(means[:,2] == i)
    month_means.append(np.mean(month_sums[ndx]))
    month_errors.append(error_propagation(errors[ndx]))

# compute confidence interval
ci = [stats.t.interval(.95, 13, month_means[i], month_errors[i]) for i in range(len(month_means))]
ci_low = [ele[0] for ele in ci]
ci_hi = [ele[1] for ele in ci]

import csv
f = 'monthly_means_brahmaputra_et.csv'
with open(f, 'w', newline='') as csvfile:
    headers = ['month', 'month_mean', 'error', 'ci_low_bound', 'ci_hi_bound']
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(headers)
    for i in range(len(month_means)):
        csvwriter.writerow([mons[i], month_means[i], month_errors[i], ci_low[i], ci_hi[i]])
csvfile.close()
# draw the graph