
import sys, numpy as np
sys.path.append('..')
from calibration.variable import DataCloud
from calibration.stats import stats
from collections import OrderedDict

class SeasonalStatistics(stats):
    @staticmethod
    def test():
        text_lines = """
        Class Name: SeasonalStatistics
        Author: H.M. Mehedi Hasan
        Date: April 2017

        Description: This class is primarily designed for calculating seasonal statistics.
        """
        print(text_lines)

        return True

    @staticmethod
    def seasonal_behaviours(data, year_column=0, month_column=1, value_column=2):
        # this fuction will find yearly peak, peak period, depression, depression period and yearly amplitude
        # returns: ndarray (2d) with columns year, peak, month of peak, depression, month of depression, seasonal amplitude

        succeed = True

        # check arguments
        if type(data) is not np.ndarray: succeed = False
        else:
            mx_ndx = max(year_column, month_column, value_column)
            if np.shape(data)[1] < (mx_ndx+1): succeed = False

        if succeed:
            dt = data[:, [year_column, month_column, value_column]]

            years = []
            peaks = []
            pperiods = []       # peak months
            bottoms = []
            bperiods = []       # bottom months
            amplitudes = []
            means = []
            std_devs = []
            for year in np.unique(dt[:, 0]):
                ndx = np.where(dt[:, 0] == year)
                d = dt[:, 2][ndx]
                if len(d) >= 8:
                    mx, mn = max(d), min(d)
                    peaks.append(mx)
                    pperiods.append(dt[:, 1][ndx][np.where(d == mx)][0])
                    bottoms.append(mn)
                    bperiods.append(dt[:, 1][ndx][np.where(d == mn)][0])
                    amplitudes.append(mx-mn)
                    means.append(np.mean(d))
                    std_devs.append(np.std(d))
                    years.append(year)

            if years and peaks and pperiods and bottoms and bperiods and amplitudes:
                return np.column_stack((years, means, std_devs, peaks, pperiods, bottoms, bperiods, amplitudes))

        return None

    @staticmethod
    def seasonal_behaviour_summary(data):
        results = []

        for i in range(0, np.shape(data)[1]):
            d = data[:,i]

            avg = np.mean(d)
            per50 = np.percentile(d, 50)
            per75 = np.percentile(d, 75)
            per80 = np.percentile(d, 80)
            per90 = np.percentile(d, 90)
            std_dev = np.std(d)
            mn = np.min(d)
            mx = np.max(d)
            rng = mx - mn

            results.append((avg, per50, per75, per80, per90, std_dev, mn, mx, rng))

        return results

    @staticmethod
    def seasonal_summary(data_cloud, ndx_year=-1, ndx_month=-1):
        stat_names, results = None, None

        succeed = True
        if ndx_year == -1: ndx_year = data_cloud.index_count() - 2
        if ndx_month == -1: ndx_month = data_cloud.index_count() - 1

        if ndx_year == ndx_month or ndx_year < 0 or ndx_month < 0: succeed = False
        if not data_cloud.data_indices or not data_cloud.data: succeed = False

        if succeed:
            data = np.c_[np.array(data_cloud.data_indices)[:,[ndx_year, ndx_month]], np.array(data_cloud.data)]

            behaviors = SeasonalStatistics.seasonal_behaviours(data, year_column=0, month_column=1, value_column=2)

            if behaviors.size > 0:
                temp_results = SeasonalStatistics.seasonal_behaviour_summary(behaviors[:,1:])

                if temp_results:
                    results = OrderedDict()
                    stat_names = ['Mean', 'Mode', '3QR', '80 Percentile', '90 Percentile', 'Std. deviation', 'Min', 'Max', 'Range']
                    dic_indices = ['Yearly Mean', 'Yearly Std. Dev', 'Year Peak', 'Peak Month', 'Year Bottom', 'Bottom Month', 'Amplitude']
                    if len(temp_results) == len(dic_indices):
                        for i in range(len(temp_results)): results[dic_indices[i]] = temp_results[i]
        return stat_names, results

    @staticmethod
    def monthly_summary(data_cloud, ndx_year=-1, ndx_month=-1):
        stat_names, results = [], OrderedDict()

        succeed = True
        if ndx_year == -1: ndx_year = data_cloud.index_count() - 2
        if ndx_month == -1: ndx_month = data_cloud.index_count() - 1

        if ndx_year == ndx_month or ndx_year < 0 or ndx_month < 0: succeed = False
        if not data_cloud.data_indices or not data_cloud.data: succeed = False

        if succeed:
            data = np.c_[np.array(data_cloud.data_indices)[:, [ndx_year, ndx_month]], np.array(data_cloud.data)]
            stat_names = ['mean', 'mode', 'std_dev', 'min', 'max', 'range']

            month_names = ['0th', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            for month in range(1, 13):
                ndx = np.where(data[:, 1] == month)
                d = data[:, 2][ndx]

                avg, mode, std_dev, mn, mx = np.mean(d), np.percentile(d, 50), np.std(d), np.min(d), np.max(d)
                results[month_names[month]] = (avg, mode, std_dev, mn, mx, mx-mn)

        return stat_names, results

    @staticmethod
    def save_numpy_data(filename, data, headers=[], delimiter=',', fmt=''):
        succeed = True
        if headers: headers=delimiter.join(headers)
        if type(fmt) is list or type(fmt) is tuple: fmt = delimiter.join(fmt)

        try: np.savetxt(filename, data, header=headers, delimiter=delimiter, fmt=fmt, comments='')
        except: succeed = False

        return succeed