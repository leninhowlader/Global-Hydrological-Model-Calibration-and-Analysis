
import sys, numpy as np

from core.variable import DataCloud
from core.stats import stats
from collections import OrderedDict


class SeasonalStatistics(stats):
    @staticmethod
    def test():
        text_lines = """
        Class Name: SeasonalStatistics
        Author: H.M. Mehedi Hasan
        Date: April 2017

        Description: This class is primarily designed for calculating seasonal 
        statistics.
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

            months = ['0th', 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1, 0]

            years = []
            peaks = []
            peakmons = []       # peak months
            bottoms = []
            btmmons = []       # bottom months
            amplitudes = []
            means = []
            std_devs = []
            for year in np.unique(dt[:, 0]):
                ndx = np.where(dt[:, 0] == year)
                ds = dt[:, :][ndx]  #ds = data slice
                if len(ds) >= 8:
                    d = ds[:, 2]
                    m = ds[:, 1]
                    mx = max(d)
                    peaks.append(mx)
                    mx_mon = m[np.where(d==mx)][0]
                    peakmons.append(mx_mon)
                    ndx = np.ma.where(m<=mx_mon)
                    not_ndx = np.ma.where(m <= mx_mon)
                    mn1, mn2 = np.min(d[ndx]), np.min(d[not_ndx])
                    mn1_mon, mn2_mon = int(m[np.where(d==mn1)][0]), int(m[np.where(d==mn2)][0])
                    bottoms.extend([mn1, mn2])
                    btmmons.extend([months[mn1_mon], months[mn2_mon]])
                    means.append(np.mean(d))
                    std_devs.append(np.std(d))
                    years.append(year)

            if years and len(bottoms) == len(years)*2:
                bottoms.pop(-1)
                btmmons.pop(-1)
                for i in range(len(bottoms)-1,0,-2):
                    if bottoms[i-1] < bottoms[i]:
                        bottoms.pop(i)
                        btmmons.pop(i)
                    else:
                        bottoms.pop(i-1)
                        btmmons.pop(i-1)

                for i in range(len(bottoms)): amplitudes.append(peaks[i]-bottoms[i])

            if years and peaks and peakmons and bottoms and btmmons and amplitudes:
                return np.column_stack((years, means, std_devs, peaks, peakmons, bottoms, btmmons, amplitudes))

        return None

    @staticmethod
    def seasonal_behaviour_summary(data):
        results = []

        for i in range(0, np.shape(data)[1]):
            d = data[:,i]

            avg = np.mean(d)
            per10 = np.percentile(d, 10)
            q1 = np.percentile(d, 25)
            median = np.percentile(d, 50)
            q3 = np.percentile(d, 75)
            per90 = np.percentile(d, 90)
            std_dev = np.std(d)
            mn = np.min(d)
            mx = np.max(d)
            rng = mx - mn

            results.append((avg, per10, q1, median, q3, per90, std_dev, mn, mx, rng))

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
                    stat_names = ['Mean', '10th Percentile', '1st Quartile', 'Median', '3rd Quartile', '90th Percentile', 'Std. deviation', 'Min', 'Max', 'Range']
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
            stat_names = ['mean', 'median', 'std_dev', 'min', 'max', 'range']

            month_names = ['0th', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            for month in range(1, 13):
                ndx = np.where(data[:, 1] == month)
                d = data[:, 2][ndx]

                avg, median, std_dev, mn, mx = np.mean(d), np.percentile(d, 50), np.std(d), np.min(d), np.max(d)
                results[month_names[month]] = (avg, median, std_dev, mn, mx, mx-mn)

        return stat_names, results

    @staticmethod
    def save_numpy_data(filename, data, headers=[], delimiter=',', fmt=''):
        succeed = True
        if headers: headers=delimiter.join(headers)
        if type(fmt) is list or type(fmt) is tuple: fmt = delimiter.join(fmt)

        try: np.savetxt(filename, data, header=headers, delimiter=delimiter, fmt=fmt, comments='')
        except: succeed = False

        return succeed

    @staticmethod
    def get_seasonal_amplitudes(
        data:np.ndarray,
        season:np.ndarray=np.empty(0),
    ):
        """
        Finds seasonal amplitudes for each season.

        Parameters:
        @param data: (2-d numpy array) data. each column must represent a time-
                        series
        @param season: (1-d numpy array, optional) hydrological season. this
                        should have 12 integer values codifying to which season
                        the monthly values, starting from Jan to Dec, belongs to.
                        however, defining season for other than monthly time-
                        step is also possible.
                        the lowest value in the season variable would indicate 
                        the start of the first season. if a hydrological season
                        occurs in month belonging to two years, appropriate 
                        shifting will be done
        @return (1-d or 2-d numpy array) the list of amplitudes for each season 
                        in the order of occurance of the hydrological season
        """

        ## [step] create season identifier array
        season_array = SeasonalStatistics.season_identifier_array(
            n=data.shape[0],
            season=season
        )
        ## [end]

        ## [step] delete data for fractional seasons at the beginning and at
        ## the end
        ii = np.isnan(season_array)
        data = data[~ii]
        season_array = season_array[~ii]
        ## [end]

        amplitudes = np.empty(0)
        for sn in np.unique(season_array):
            ii = (season_array==sn)
            d = data[ii]
            a = (np.nanmax(d, axis=0) - np.nanmin(d, axis=0)).reshape(1, -1)
            
            try: amplitudes = np.concatenate((amplitudes, a), axis=0)
            except: amplitudes = a
        
        return amplitudes


    @staticmethod
    def season_identifier_array(
        n:int,
        season:np.ndarray=np.empty(0),
    ):
        """
        The function generates an array containing unique identifiers for 
        successive seasons until the end of time step reach

        Paramters:
        @paran n: (int) number of time steps in total
        @param season: (1-d numpy array) describes the seasons in each successive
                        time steps till the season repeats. the lowest value in 
                        the season variable would indicate 
                        the start of the first season. if a hydrological season
                        occurs in month belonging to two years, appropriate 
                        shifting will be done
        @return (1-d numpy array of int) season identifier array
        """
        season = np.array(season)
        if season.shape[0] == 0: season = np.zeros(12, dtype=int)
        
        ## [step] shift seasons, if necessary
        first_sni = np.argsort(season)[0]
        if first_sni > 0:
            season = np.concatenate((season[first_sni:],season[:first_sni]), 
                                    axis=0)
        ## [end]

        ## [step] create season identifier array
        nseasons = np.unique(season).shape[0]
        lp = 0                  # no. of loops
        season_all = np.array([np.nan] * first_sni)
        while season_all.shape[0] < n:
            season_all = np.concatenate((season_all, season + (lp * nseasons)), 
                                        axis=0)
            lp += 1
        season_all = season_all[:n]
        ## [end]

        ## [step] discard values from the end, if necessary
        last_sn = np.nanmax(season_all)
        sn_actual = last_sn - (lp - 1) * nseasons

        count0 = (season==sn_actual).sum()
        count1 = (season_all==last_sn).sum()
        if count0 != count1: season_all[season_all==last_sn] = np.nan
        ## [end]

        return season_all

