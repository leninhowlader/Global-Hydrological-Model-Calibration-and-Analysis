__author__ = 'mhasan'

import sys, shapefile as shp, os, numpy as np
sys.path.append('..')
from utilities.globalgrid import GlobalGrid
GlobalGrid.set_model_version('wghm22d')
from collections import OrderedDict
from matplotlib import pyplot as plt, animation as ani
from matplotlib.offsetbox import AnchoredText
import matplotlib.dates as mdates

# contibution map types:
#       (1) contribution of storage compartments to TWS seasonal amplitude [per year]
#       (2) contribution of storage compartments to mean TWS seasonal amplitude [long term]
#       (3) monthly contribution of storage components to tws [per month]
#       (4) monthly contribution of storage components to tws change/variation [per month]
'''
Contribution map produced by this scrip has been compared with contribution map produced manually using ArcMap (see 
below). No difference was observed expect some rounding effect.

Contribution Map using ArcMap [Algorithm]:
> read unf files using 'IPG UNF to SHAPE' function
> add an attribute to each shapefile namely 'amplitude'
> compute amplitude for each storage variable using follow field calculator python script
def amplitude(*args): return max(args) - min(args)
amplitude = amplitude(!VALUE001!,!VALUE002!, .., !VALUE012!)
> join TWS shapefile with other storage shape file
> export joined dataset as new shapefile
> [clean attribute tables if necessary]
> compute contribution of each variable as the ratio of amplitude of that variable and tws amplitude
'''


# Enum class definitions
from enum import Enum
class FileEndian(Enum): little_endian, big_endian = 0, 1
class PredictionType(Enum): monthly, daily365, daily31 = 0, 1, 2

class StorageContribution:
    start_year = 1901
    end_year = 2100
    model_output_directory = ''
    output_directory = ''
    target_cells = []
    file_endian = FileEndian.big_endian
    prediction_type = PredictionType.monthly
    export_cell_geo_coordinates = True
    flag_export_coordinates_done = False

    storage_variables = OrderedDict()
    storage_variables['totalstorage'] = {'acronym': 'tws', 'filename': 'G_TOTAL_STORAGES_km3_[YEAR].12.UNF0',
                                         'predictions': None, 'contributions': None}
    storage_variables['canopy'] = {'acronym': 'canopy', 'filename': 'G_CANOPY_WATER_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['snow'] = {'acronym': 'snow', 'filename': 'G_SNOW_WATER_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['soil'] = {'acronym': 'soil', 'filename': 'G_SOIL_WATER_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['groundwater'] = {'acronym': 'gw', 'filename': 'G_GROUND_WATER_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['locallake'] = {'acronym': 'llake', 'filename': 'G_LOC_LAKE_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['globallake'] = {'acronym': 'glake', 'filename': 'G_GLO_LAKE_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['localwetland'] = {'acronym': 'lwetland', 'filename': 'G_LOC_WETL_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['globalwetland'] = {'acronym': 'gwetland', 'filename': 'G_GLO_WETL_STORAGE_km3_[YEAR].12.UNF0'}
    storage_variables['reservoir'] = {'acronym': 'resrvor', 'filename': 'G_RES_STORAGE_MEAN_km3_[YEAR].12.UNF0'}
    storage_variables['river'] = {'acronym': 'river', 'filename': 'G_RIVER_STORAGE_km3_[YEAR].12.UNF0'}

    # defination of colors
    color_canopy = '#A3FF73' # RGB Color Code: 163, 255, 115
    color_soil = '#686868' # RGB Color Code: 104, 104, 104
    color_gw = '#002673' # RGB Color Code: 0, 38, 115
    color_sws =  '#73B2FF' # RGB Color Code: 115, 178, 255
    color_snow =  '#FFFFFF' # RGB Color Code: 255, 255, 255
    color_llake = '#D3FFBE' # RGB Color Code: 211, 255, 190
    color_glake = '#00E6A9' # RGB Color Code: 0, 230, 169
    color_lwetland = '#73DFFF' # RGB Color Code: 115, 223, 255
    color_gwetland = '#00A9E6' # RGB Color Code: 0, 169, 230
    color_reservoir = '#005CE6' # RGB Color Code: 0, 92, 230
    color_river = '#002673' # RGB Color Code: 0, 38, 115
    color_others = '#FFFFFF' # RGB Color Code: 255, 255, 255
    color_border = '#9C9C9C' # RGB Color Code: 156, 156, 156
    color_background = '#FFFFBE' # RGB Color Code: 255, 255, 190
    
    @staticmethod
    def get_storage_color(storage_name:str):
        storage_name = storage_name.lower()
        if storage_name in ['canopy', 'canopy storage']: return StorageContribution.color_canopy
        elif storage_name in ['soil', 'soil storage']: return StorageContribution.color_soil
        elif storage_name in ['groundwater', 'groundwater storage']: return StorageContribution.color_gw 
        elif storage_name in ['surface water storage', 'sws']: return StorageContribution.color_sws
        elif storage_name in ['snow', 'snow storage']: return StorageContribution.color_snow
        elif storage_name in ['local lake', 'llake', 'local lake storage']: return StorageContribution.color_llake
        elif storage_name in ['global lake', 'glake', 'global lake storage']: return StorageContribution.color_glake
        elif storage_name in ['local wetland', 'local wetland storage', 'lwetland']: return StorageContribution.color_lwetland
        elif storage_name in ['global wetland', 'global wetland storage', 'gwetland']: return StorageContribution.color_gwetland
        elif storage_name in ['reservoir', 'reservoir storage']: return StorageContribution.color_reservoir 
        elif storage_name in ['river', 'river storage']: return StorageContribution.color_river
        elif storage_name in ['others', 'other']: return StorageContribution.color_others 
        elif storage_name in ['border', 'shape border']: return StorageContribution.color_border
        elif storage_name in ['background']: return StorageContribution.color_background
        else: return ''
        
    @staticmethod
    def is_okay():
        '''
        Check inputs for consistency and completeness.

        :return: (boolean) TRUE on fulfilling requirements; FALSE otherwise.
        '''
        start_year, end_year = StorageContribution.start_year, StorageContribution.end_year
        if start_year < 1901 or end_year < 1901 or start_year > end_year: return False
        elif not StorageContribution.model_output_directory: return False
        elif not os.path.exists(StorageContribution.model_output_directory): return False
        elif not os.path.exists(StorageContribution.output_directory): return False

        # checking if all necessary model output files exist between start and end years
        for var_name in StorageContribution.storage_variables.keys():
            filelist = StorageContribution.model_output_files(var_name)
            for f in filelist:
                if not os.path.exists(f): return False

        return True

    @staticmethod
    def set_start_year(year): StorageContribution.start_year = year

    @staticmethod
    def set_end_year(year): StorageContribution.end_year = year

    @staticmethod
    def set_target_cells(target_cells_from_file:str= '', target_cells:list=[]):
        '''
        Sets target cell list from either file or provided list

        :param target_cells_from_file: (string, optional) name of the file from the cellnum will be read in. default value ''
        :param target_cells: (list, optional) list of target cells. default value []
        :return: True on success, False otherwise. [Note that if both the parameters are missing, the function will return
            FALSE]
        '''
        succeed = True

        if target_cells_from_file:
            target_cells.clear()

            temp = GlobalGrid.read_cell_info(target_cells_from_file)
            if type(temp[0]) is list:
                for i in range(len(temp)): target_cells += temp[i]
            else: target_cells += temp

        if target_cells: StorageContribution.target_cells = target_cells
        else: succeed = False

        StorageContribution.flag_export_coordinates_done = False

        return succeed

    @staticmethod
    def set_prediction_directory(directory:str): StorageContribution.model_output_directory = directory

    @staticmethod
    def set_prediction_type(prediction_type:str):
        '''
        Sets prediction type [and changes the output filename for storage variables - not done yet]

        :param prediction_type: (string) type of model prediction output. Possible values are 'monthly', 'daily365',
            'daily31'
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True

        prediction_type = prediction_type.lower()
        if prediction_type in ['month', 'monthly']:
            StorageContribution.prediction_type = PredictionType.monthly
        elif prediction_type in ['daily', 'daily365', 'daily.365']:
            StorageContribution.prediction_type = PredictionType.daily365
        else: StorageContribution.prediction_type = PredictionType.daily31

        # change filename in storage_variables dictionary

        return succeed

    @staticmethod
    def model_output_files(variable_name):
        '''
        Generate list of model output filenames for target variable within start and end years.

        :param variable_name: (string) Name of the storage variable e.g. canopy, snow etc.
        :return: (list of string) model output filenames to be read
        '''
        start_year, end_year = StorageContribution.start_year, StorageContribution.end_year
        filename = StorageContribution.storage_variables[variable_name]['filename']

        filelist = []
        for year in range(start_year, end_year+1):
            f = os.path.join(StorageContribution.model_output_directory, filename.replace('[YEAR]', str(year)))
            filelist.append(f)

        return filelist

    @staticmethod
    def annual_amplitude(storage:np.ndarray):
        '''
        Computes annual amplitude

        :param storage: (numpy 2d-array) input storage as rows of cell storage and monthly storages in columns
        :return: (2d-array) annual amplitude
        '''
        nrow, ncol = storage.shape
        return (storage.max(axis=1) - storage.min(axis=1)).reshape(nrow, 1)

    @staticmethod
    def mean_annual_amplitude(annual_ampplitudes:np.ndarray):
        '''
        Computes mean annual amplitude of grid cells

        :param annual_ampplitudes: (numpy 2d-array) amplitude data as rows of amplitudes of gird cells and yearly
            amplitudes in columns
        :return: (numpy 2d-array) mean amplitudes
        '''
        nrow, ncol = annual_ampplitudes.shape
        return annual_ampplitudes.mean(axis=1).reshape(nrow, 1)

    @staticmethod
    def compute_contribution(component_storage_amplitude:np.ndarray, total_storage_amplitude:np.ndarray):
        '''
        computes contribution of a storage component to total storage amplitude.

        :param component_storage_amplitude: (numpy 2d-array) storage amplitude of target storage component. the shape
            and dimension must be the same as total_storage_amplitude
        :param total_storage_amplitude: (numpy 2d-array) amplitude of total storage. the shape and dimension must be
            the same as that of component_storage_amplitude
        :return: (numpy 2d-array) contribution of storage component to total storage amplitude. If inputs differ in
            dimension or shape, the function returns empty numpy array.

        Note: This function might be used to compute both annual and long-term contribution depending on the input data.

        Examples:

        '''
        if not component_storage_amplitude.shape == total_storage_amplitude.shape: return np.array([])

        return component_storage_amplitude/total_storage_amplitude

    @staticmethod
    def basin_scale_contribution_report(export_contributions_to_csv='', export_summary_to_file:str='',
                                        only_contribution_to_storage_change:bool=True, print_on_screen:bool=True):
        '''
        Computes basin-scale contribution summaries and prints either on file, on screen or on both

        :param export_contributions_to_csv: (string) filename where contributions will be exported.
        :param export_summary_to_file: (string) filename where contribution summary will be dumped
        :param only_contribution_to_storage_change: (bool) flag indicating whether or not contribution to absolute
                                storage volume would be calculated
        :param print_on_screen: (bool) flag indicating whether or not to print output on screen
        :return: None
        '''

        text_lines = []

        start_year, end_year = StorageContribution.start_year, StorageContribution.end_year

        # inner function
        def basin_sum(d): return np.sum(d, axis=0)
        # ... end of inner function


        # step: read predictions of water storage variables
        for var_name in StorageContribution.storage_variables.keys():
            succeed = StorageContribution.read_model_predictions(varname=var_name, summary_fun=None)
            if not succeed: break

        nrow = (end_year - start_year + 1) * 12
        varnames = []

        if not only_contribution_to_storage_change:
            # step: calculate contribution of each variable
            contrib = None
            pred_tws = basin_sum(StorageContribution.storage_variables['totalstorage']['predictions'])
            for var_name in StorageContribution.storage_variables.keys():
                if var_name == 'totalstorage': continue

                pred_var = basin_sum(StorageContribution.storage_variables[var_name]['predictions'])

                temp = StorageContribution.compute_contribution(pred_var, pred_tws).reshape(nrow, 1)
                try: contrib = np.concatenate((contrib, temp), axis=1)
                except: contrib = temp

                varnames.append(var_name)

            # print contributions
            text_lines.append('1. Storage Contributions to Basin Total (Volume)')
            temp = StorageContribution.print_contribution_summary(contrib, varnames, start_year=start_year, on_screen=False)
            for line in temp: text_lines.append(line)

            if export_contributions_to_csv:
                filename = export_contributions_to_csv.replace('.csv', '_storage_volume.csv')
                np.savetxt(filename, contrib, fmt='%f', delimiter=',')

        # inner function to compute storage change
        from scipy.ndimage.interpolation import shift
        def storage_change(d, lag=1):
            t = shift(d, lag, cval=np.NaN)
            return d-t
        # ... end of inner function

        # calculate storage contributions to total storage change
        varnames.clear()
        contrib = None
        pred_tws = storage_change(basin_sum(StorageContribution.storage_variables['totalstorage']['predictions']))
        for var_name in StorageContribution.storage_variables.keys():
            if var_name == 'totalstorage': continue

            pred_var = storage_change(basin_sum(StorageContribution.storage_variables[var_name]['predictions']))
            temp = StorageContribution.compute_contribution(pred_var, pred_tws).reshape(nrow, 1)
            try: contrib = np.concatenate((contrib, temp), axis=1)
            except: contrib = temp

            varnames.append(var_name)

        # print storage contributions
        text_lines.append('2. Storage Contributions to Total Storage (Volume) Change')
        temp = StorageContribution.print_contribution_summary(contrib, varnames, start_year=start_year, on_screen=False)
        for line in temp: text_lines.append(line)

        if export_contributions_to_csv: np.savetxt(export_contributions_to_csv, contrib, fmt='%f', delimiter=',')

        if export_summary_to_file:
            try:
                f = open(export_summary_to_file, 'w')
                for line in text_lines: f.write(line + '\n')
                f.close()
            except: pass

        if print_on_screen:
            for line in text_lines: print(line)

    @staticmethod
    def print_contribution_summary(contributions:np.ndarray, varnames:list, start_year:int=1, on_screen=False):
        lines = []

        # inner function year-summary
        def yearly_summary(d, fun=np.mean):
            nrow, ncol = d.shape
            nrow = nrow - nrow%12

            means = None
            for i in range(0, nrow, 12):
                m = fun(d[i:i+12], axis=0).reshape(1, ncol)
                try: means = np.concatenate((means, m), axis=0)
                except: means = m

            return means
        # ... end of inner function

        # inner function month-summary
        def month_summary(d, fun=np.mean):
            nrow, ncol = d.shape
            nrow -= nrow%12

            mndx = np.arange(0, nrow, 12)

            summary = None
            for i in range(12):
                m = fun(d[mndx+i], axis=0).reshape(1, ncol)
                try: summary = np.concatenate((summary, m), axis=0)
                except: summary = m

            return summary
        # ... end of inner function

        # a. long-term means
        text = '(a) Long-term mean:\n' + 'storage'.ljust(20, ' ') + 'mean'.rjust(10, ' ') + 'std. dev.'.rjust(10, ' ')
        lines.append(text)
        means = np.nanmean(contributions, axis=0)
        stddevs = np.nanstd(contributions, axis=0)

        for i in range(len(varnames)):
            text = varnames[i].ljust(20, ' ') + ('%0.4f' % means[i]).rjust(10, ' ') + ('%0.4f' % stddevs[i]).rjust(10, ' ')
            lines.append(text)

        # b. annual means (mean and std. deviation)
        text = '\n(b) Annual means:\n' + 'year'.ljust(8, ' ') + ''.join([x.rjust(15, ' ') for x in varnames])
        lines.append(text)
        means = yearly_summary(contributions, fun=np.mean)
        for i in range(len(means)):
            text = ('%d'%(start_year + i)).ljust(8, ' ') + ''.join([('%0.4f'%x).rjust(15, ' ') for x in means[i]])
            lines.append(text)

        text = '\nVariation (std. dev) in annual means:\n' + 'year    ' + ''.join([x.rjust(15, ' ') for x in varnames])
        lines.append(text)
        stddevs = yearly_summary(contributions, fun=np.std)
        for i in range(len(stddevs)):
            text = ('%d'% (start_year + i)).ljust(8, ' ') + ''.join([('%0.4f'% x).rjust(15, ' ') for x in stddevs[i]])
            lines.append(text)

        # c. month-summaries (mean and std. dev.)
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        text = '\n(c) Month-means:\n' + 'month'.ljust(8, ' ') + ''.join([x.rjust(15, ' ') for x in varnames])
        lines.append(text)
        means = month_summary(contributions, np.nanmean)
        for i in range(12):
            text = ('%s'%months[i]).ljust(8, ' ') + ''.join([('%0.4f'%x).rjust(15, ' ') for x in means[i]])
            lines.append(text)

        text = '\nStd. deviation of month-means:\n' + 'month'.ljust(8, ' ') + ''.join([x.rjust(15, ' ') for x in varnames])
        lines.append(text)
        stddevs = month_summary(contributions, np.nanstd)
        for i in range(12):
            text = ('%s' % months[i]).ljust(8, ' ')+ ''.join([('%0.4f'%x).rjust(15, ' ') for x in stddevs[i]])
            lines.append(text)

        if on_screen:
            for line in lines: print(lines)
        else: return lines

    @staticmethod
    def export_prediction(target_directory:str, filename_prefix:str, summary_fun:callable=None):
        for var_name in StorageContribution.storage_variables.keys():
            pred = StorageContribution.storage_variables[var_name]['predictions']

            if summary_fun: pred = summary_fun(pred)

            filename = os.path.join(target_directory, '%s_%s.csv'%(filename_prefix, var_name))
            np.savetxt(filename, pred, fmt='%f', delimiter=',')

    @staticmethod
    def contribution_to_total_volume(summary_type='all', output_filename_prefix='', output_format='both'):
        '''
        Computes storage contributions to total water storage in absolute term

        :param summary_type: (string) name of summary method. accepted values are 'annual', 'annual mean', 'long-term',
                            'long-term mean', 'month-mean', 'all', 'none', 'na' or an empty string. if no method is
                            specified, all monthly contributions will be saved in output files.
        :param output_filename_prefix: (string) prefix of output file(s)
        :param output_format: (string) output format. accepted values: 'shape', 'binary', or 'both'
        :return: (boolean) True on success, False otherwise
        '''
        if summary_type not in ['annual', 'annual mean', 'long-term', 'long-term mean', 'month-mean', 'all', 'none', 'na', '']: return False
        if output_format not in ['shape', 'binary', 'both']: return False

        # step: read predictions of water storage variables
        for var_name in StorageContribution.storage_variables.keys():
            succeed = StorageContribution.read_model_predictions(varname=var_name, summary_fun=None)
            if not succeed: break

        # step: compute contribution and save results in the variable dictionary temporarily
        pred_tws = StorageContribution.storage_variables['totalstorage']['predictions']
        for var_name in StorageContribution.storage_variables.keys():
            if var_name == 'totalstorage': continue

            pred_var = StorageContribution.storage_variables[var_name]['predictions']
            contrib_var = StorageContribution.compute_contribution(pred_var, pred_tws)
            StorageContribution.storage_variables[var_name]['contributions'] = contrib_var

        # step: compute summary when applicable and save contributions
        def annual_summary(monthly_data:np.ndarray):
            nrow, ncol = monthly_data.shape

            temp = None
            for start_ndx in range(0, ncol, 12):
                end_ndx = start_ndx + 12

                m = np.mean(monthly_data[:, start_ndx:end_ndx], axis=1).reshape(nrow, 1)
                try: temp = np.concatenate((temp, m), axis=1)
                except: temp = m

            return temp
        # ... end of inner function

        def month_mean(monthly_data:np.ndarray):
            nrow, ncol = monthly_data.shape

            ncol -= ncol%12  # only to ensure that no. of columns would be a multiple of 12
            jan_ndx = np.arange(0, ncol, 12)

            temp = None
            for m in range(12):
                cndx = jan_ndx + m

                t = np.mean(monthly_data[:,cndx], axis=1).reshape(nrow, 1)
                try: temp = np.concatenate((temp, t), axis=1)
                except: temp = t

            return temp
        # ... end of inner function

        def long_term_summary(monthly_data:np.ndarray):
            nrow, ncol = monthly_data.shape
            return np.mean(monthly_data, axis=1).reshape(nrow, 1)
        # ... end of inner function

        if summary_type in ['none', 'na', '']:
            succeed = StorageContribution.save_contribution(filename_prefix=output_filename_prefix, output_format=output_format,
                                                            contribution_type='monthly')

        elif summary_type in ['annual', 'annual mean']:
            for var_name in StorageContribution.storage_variables.keys():
                if var_name == 'totalstorage': continue

                contrib_var = StorageContribution.storage_variables[var_name]['contributions']
                StorageContribution.storage_variables[var_name]['contributions'] = annual_summary(contrib_var)

            succeed = StorageContribution.save_contribution(filename_prefix=output_filename_prefix, output_format=output_format,
                                                            contribution_type='annual')

        elif summary_type in ['long-term', 'long-term mean']:
            for var_name in StorageContribution.storage_variables.keys():
                if var_name == 'totalstorage': continue

                contrib_var = StorageContribution.storage_variables[var_name]['contributions']
                StorageContribution.storage_variables[var_name]['contributions'] = long_term_summary(contrib_var)

            succeed = StorageContribution.save_contribution(filename_prefix=output_filename_prefix, output_format=output_format,
                                                            contribution_type='long-term')

        elif summary_type in ['month-mean']:
            for var_name in StorageContribution.storage_variables.keys():
                if var_name == 'totalstorage': continue

                contrib_var = StorageContribution.storage_variables[var_name]['contributions']
                StorageContribution.storage_variables[var_name]['contributions'] = month_mean(contrib_var)

            succeed = StorageContribution.save_contribution(filename_prefix=output_filename_prefix, output_format=output_format,
                                                            contribution_type='month-mean')

        else: # if summary type = 'all'
            # copy monthly contribution data into temporary variable
            contribution_all = {}
            for var_name in StorageContribution.storage_variables.keys():
                if var_name == 'totalstorage': continue

                contrib_var = StorageContribution.storage_variables[var_name]['contributions']
                contribution_all[var_name] = contrib_var.copy()

            # compute long-term mean and save results
            for var_name, contrib in contribution_all.items():
                StorageContribution.storage_variables[var_name]['contributions'] = long_term_summary(contrib)

            succeed = StorageContribution.save_contribution(filename_prefix=output_filename_prefix, output_format=output_format,
                                                            contribution_type='long-term')

            # compute annual mean and save results
            for var_name, contrib in contribution_all.items():
                StorageContribution.storage_variables[var_name]['contributions'] = annual_summary(contrib)

            succeed = StorageContribution.save_contribution(filename_prefix=output_filename_prefix, output_format=output_format,
                                                            contribution_type='annual')

            # compute month-mean and save results
            for var_name, contrib in contribution_all.items():
                StorageContribution.storage_variables[var_name]['contributions'] = month_mean(contrib)

            succeed = StorageContribution.save_contribution(filename_prefix=output_filename_prefix, output_format=output_format,
                                                            contribution_type='month-mean')

            contribution_all = None

        # step: clean temporarily stored predictions
        StorageContribution.clear_temporary_data(predictions=True, contributions=True)

        return succeed

    @staticmethod
    def clear_temporary_data(predictions:bool=True, contributions:bool=True):
        '''
        Removes temporarily stored data inside storage variable dictionary

        :param predictions: (bool) flag for clearing predictions. if the value is true, predictions will be deleted
        :param contributions: (bool) flag for removing contributions: if the value is true, contributions will be deleted
        :return: None
        '''
        if predictions:
            for var_name in StorageContribution.storage_variables.keys():
                StorageContribution.storage_variables[var_name]['predictions'] = None

        if contributions:
            for var_name in StorageContribution.storage_variables.keys():
                StorageContribution.storage_variables[var_name]['contributions'] = None

    @staticmethod
    def contribution_to_seasonal_amplitude(contribution_type='annual', filename_prefix='contrib_amplitude', output_format='both'):
        '''
        Computes storage contributions to seasonal amplitude and creates maps (and/or stores contributions into
        binary files)

        :param contribution_type: (string) Type of contribution to be calculated. Parameter must have value one of the
            following values: 'annual', 'long-term', 'both'
        :return: (boolean) True on success, False otherwise
        '''
        # step-1: preparation
        succeed = True
        if contribution_type not in ['annual', 'long-term', 'both']: return False

        # step-2: read predictions of water storage variables
        for var_name in StorageContribution.storage_variables.keys():
            succeed = StorageContribution.read_model_predictions(varname=var_name, summary_fun=StorageContribution.annual_amplitude)
            if not succeed: break

        # step-3: compute contributions and save results into shape and/or binary files
        if succeed:
            if contribution_type in ['annual', 'both']: # compute annual contributions
                amplitudes_tws = StorageContribution.storage_variables['totalstorage']['predictions']

                for var_name in StorageContribution.storage_variables.keys():
                    if var_name == 'totalstorage': continue

                    amplitudes_var = StorageContribution.storage_variables[var_name]['predictions']
                    contributions = StorageContribution.compute_contribution(amplitudes_var, amplitudes_tws)
                    StorageContribution.storage_variables[var_name]['contributions'] = contributions

                # save contributions into shape and/or binary files
                succeed = StorageContribution.save_contribution(filename_prefix=filename_prefix, output_format=output_format)

            if contribution_type in ['long-term', 'both']: # compute long-term mean contributions
                amplitudes_tws = StorageContribution.storage_variables['totalstorage']['predictions']
                amplitudes_tws = StorageContribution.mean_annual_amplitude(amplitudes_tws)
                # StorageContribution.storage_variables['totalstorage']['predictions'] = amplitudes_tws

                for var_name in StorageContribution.storage_variables.keys():
                    if var_name == 'totalstorage': continue

                    amplitudes_var = StorageContribution.storage_variables[var_name]['predictions']
                    amplitudes_var = StorageContribution.mean_annual_amplitude(amplitudes_var)
                    contributions = StorageContribution.compute_contribution(amplitudes_var, amplitudes_tws)
                    StorageContribution.storage_variables[var_name]['contributions'] = contributions

                # save contributions into shape and/or binary files
                succeed = StorageContribution.save_contribution(filename_prefix=filename_prefix, output_format=output_format)

        # step: clean temporarily stored data
        for var_name in StorageContribution.storage_variables.keys():
            StorageContribution.storage_variables[var_name]['predictions'] = None
            StorageContribution.storage_variables[var_name]['contributions'] = None

        return succeed

    @staticmethod
    def read_model_predictions(varname:str, summary_fun=None):
        '''
        Reads model prediction output files for given prediction variable. If summary function is used, the predictions
        will be summerized accordingly

        :param varname: (string) Name of the target prediction variable
        :param summary_fun: (function; optional) Name of the summary function to be used. Default value is None
        :return: (ndarray) model predictions and summaries
        '''
        succeed = True

        ncol = -1
        if StorageContribution.prediction_type == PredictionType.monthly: ncol = 12
        elif StorageContribution.prediction_type == PredictionType.daily365: ncol = 365
        else: ncol = 31

        crop = True
        if not StorageContribution.target_cells: crop = False
        if crop: ndx = np.array(StorageContribution.target_cells) - 1   # !!important!!: reduction by 1 is necessary

        # step-2: read total water storage predictions and compute amplitudes
        predictions = None
        try:
            filelist = StorageContribution.model_output_files(varname)
            for filename in filelist:
                d = StorageContribution.read_unf(filename, file_endian=StorageContribution.file_endian, ncol=ncol)
                if crop: d = d[ndx, :]

                if summary_fun: temp = summary_fun(d)
                else: temp = d

                try: predictions = np.concatenate((predictions, temp), axis=1)
                except: predictions = temp
        except: succeed = False

        if succeed: StorageContribution.storage_variables[varname]['predictions'] = predictions

        return succeed

    @staticmethod
    def save_contribution(filename_prefix, output_format='both', contribution_type='annual'):
        '''
        Saves storage contributions

        :param filename_prefix: (string) Prefix of output files
        :param output_format: (string) output file format. parameter value should be either 'shape', 'binary' or 'both'
        :param contribution_type: (string) contribution type. parameter value can be either 'long-term', 'annual', 'monthly'
                                or 'month-mean'
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True

        # step 1: check inputs and data
        if output_format not in ['shape', 'binary', 'both']: return False
        if contribution_type not in ['long-term', 'annual', 'monthly', 'month-mean']: return False

        # check if shape of contribution data is the same for all variables
        nrow, ncol = 0, 0
        for var_name in StorageContribution.storage_variables.keys():
            if var_name == 'totalstorage': continue

            contributions = StorageContribution.storage_variables[var_name]['contributions']
            if ncol == 0: nrow, ncol = contributions.shape
            else:
                if (nrow, ncol) != contributions.shape:
                    succeed = False
                    break

        if not succeed or nrow == 0 or ncol == 0:
            print('Contributions from different variables do not have same data-shape. Fails to create output file!')
            return False

        # check if number of data columns is in agreement with number of years considered
        start_year, end_year = StorageContribution.start_year, StorageContribution.end_year

        expncol = 0  # expncol = expected number of columns
        if contribution_type == 'long-term': expncol = 1
        elif contribution_type == 'annual': expncol = end_year - start_year + 1
        elif contribution_type == 'monthly': expncol = (end_year - start_year + 1) * 12
        elif contribution_type == 'month-mean': expncol = 12

        if ncol != expncol:
            print('Data format mismatch!! %d columns were found in contribution data while it was expecting %d columns.'% (ncol, expncol))
            return False

        # step 2: collect geo-coordinates of wghm cell vertices and wghm cell number (identifier)
        output_directory = StorageContribution.output_directory
        vertices = []

        target_cells = StorageContribution.target_cells
        if not target_cells: target_cells = range(1, GlobalGrid.get_wghm_cell_count() + 1)

        if nrow != len(target_cells):
            print('No. of grid cells is not in agreement with number of rows in the contribution dataset. Fails to create output file!')
            return False

        for cnum in target_cells:
            centroid = GlobalGrid.get_wghm_centroid(cnum)
            vertices.append(GlobalGrid.cell_vertices([centroid], degree_resolution=0.5))

        # step 3: save output
        if contribution_type == 'long-term':
            # (a) single output file containing long-term (mean) contributions of all variables
            col_names, contrib = ['cnum'], np.array([])

            for key, value in StorageContribution.storage_variables.items():
                if key == 'totalstorage': continue

                col_names.append(value['acronym'])
                temp = value['contributions']
                if contrib.shape[0] == 0: contrib = temp
                else:contrib = np.concatenate((contrib, temp), axis=1)

            records = np.concatenate((np.array(target_cells).reshape(nrow, 1), contrib), axis=1)
            if output_format in ['shape', 'both']:
                filename = os.path.join(output_directory, filename_prefix + '_long_term.shp')
                succeed = StorageContribution.save_shapefile(filename, vertices, col_names, records)

            if output_format in ['binary', 'both']:
                filename = os.path.join(output_directory, filename_prefix + '_long_term.%d.unf0'%(records.shape[1]))
                succeed = StorageContribution.save_banary_file(filename, records)

        if contribution_type == 'monthly':
            # (a) variable-specific output files containing contributions in all months
            col_names = ['cnum']
            months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            for year in range(start_year, end_year + 1): col_names += ['%d_%s'%(year, mon) for mon in months]

            for key, value in StorageContribution.storage_variables.items():
                if key == 'totalstorage': continue

                contrib = value['contributions']
                records = np.concatenate((np.array(target_cells).reshape(nrow, 1), contrib), axis=1)

                if output_format in ['shape', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_monthly_%s.shp' % key)
                    succeed = StorageContribution.save_shapefile(filename, vertices, col_names, records)

                if output_format in ['binary', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_monthly_%s.%d.unf0' % (key, records.shape[1]))
                    succeed = StorageContribution.save_banary_file(filename, records)

        if contribution_type == 'annual':
            # (a) year-specific output files containing contributions of all storage variables
            for i in range(end_year - start_year + 1):
                year = start_year + i

                col_names, contrib = ['cnum'], np.array([])
                for key, value in StorageContribution.storage_variables.items():
                    if key == 'totalstorage': continue
                    col_names.append(value['acronym'])
                    temp = value['contributions'][:,i].reshape(nrow, 1)
                    if contrib.shape[0] == 0: contrib = temp
                    else:contrib = np.concatenate((contrib, temp), axis=1)

                records = np.concatenate((np.array(target_cells).reshape(nrow, 1), contrib), axis=1)

                if output_format in ['shape', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_%d.shp' % year)
                    succeed = StorageContribution.save_shapefile(filename, vertices, col_names, records)

                if output_format in ['binary', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_%d.%d.unf0' % (year, records.shape[1]))
                    succeed = StorageContribution.save_banary_file(filename, records)

                if not succeed: break

            # (b) variable-specific output files containing contributions in all years
            col_names = ['cnum'] + [str(x) for x in range(start_year, end_year + 1)]

            for key, value in StorageContribution.storage_variables.items():
                if key == 'totalstorage': continue

                contrib = value['contributions']
                records = np.concatenate((np.array(target_cells).reshape(nrow, 1), contrib), axis=1)

                if output_format in ['shape', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_%s.shp' % key)
                    succeed = StorageContribution.save_shapefile(filename, vertices, col_names, records)

                if output_format in ['binary', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_%s.%d.unf0' % (key, records.shape[1]))
                    succeed = StorageContribution.save_banary_file(filename, records)

                if not succeed: break

        # output for each single variable with contributions in multiple years
        if contribution_type == 'month-mean':
            # (a) month-specific output files containing contributions of all storage variables
            months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

            for i in range(12):
                mon = months[i]

                col_names, contrib = ['cnum'], np.array([])
                for key, value in StorageContribution.storage_variables.items():
                    if key == 'totalstorage': continue

                    col_names.append(value['acronym'])
                    temp = value['contributions'][:,i].reshape(nrow, 1)
                    if contrib.shape[0] == 0: contrib = temp
                    else:contrib = np.concatenate((contrib, temp), axis=1)

                records = np.concatenate((np.array(target_cells).reshape(nrow, 1), contrib), axis=1)

                if output_format in ['shape', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_%s_mean.shp' % mon)
                    succeed = StorageContribution.save_shapefile(filename, vertices, col_names, records)

                if output_format in ['binary', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_%s_mean.%d.unf0' % (mon, records.shape[1]))
                    succeed = StorageContribution.save_banary_file(filename, records)

                if not succeed: break

            # (b) variable-specific output files containing contributions in all months
            col_names = ['cnum'] + months
            for key, value in StorageContribution.storage_variables.items():
                if key == 'totalstorage': continue

                contrib = value['contributions']
                records = np.concatenate((np.array(target_cells).reshape(nrow, 1), contrib), axis=1)

                if output_format in ['shape', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_monthly_mean_%s.shp' % key)
                    succeed = StorageContribution.save_shapefile(filename, vertices, col_names, records)

                if output_format in ['binary', 'both']:
                    filename = os.path.join(output_directory, filename_prefix + '_monthly_mean_%s.%d.unf0' % (key, records.shape[1]))
                    succeed = StorageContribution.save_banary_file(filename, records)

                if not succeed: break

        # export cell geo-coordinates as latitudes and longitudes
        if succeed and StorageContribution.export_cell_geo_coordinates:
            if not StorageContribution.flag_export_coordinates_done:
                try:
                    LONs, LATs = None, None
                    for i in range(len(vertices)):
                        x = [p[0] for p in vertices[i][0]]
                        y = [p[1] for p in vertices[i][0]]
                        x, y = np.array(x).reshape(1, 5), np.array(y).reshape(1, 5)
                        try: LONs, LATs = np.concatenate((LONs, x), axis=0), np.concatenate((LATs, y), axis=0)
                        except: LONs, LATs = x, y

                    filename = os.path.join(output_directory, filename_prefix + '_coordinate_X.5.unf0')
                    succeed = StorageContribution.save_banary_file(filename, LONs)

                    filename = os.path.join(output_directory, filename_prefix + '_coordinate_Y.5.unf0')
                    succeed = StorageContribution.save_banary_file(filename, LATs)
                except: succeed = False

                StorageContribution.flag_export_coordinates_done = succeed
        return succeed

    @staticmethod
    def save_banary_file(filename:str, records:np.ndarray):
        '''
        Save results into binary files

        :param filename: (string) Name of the output file
        :param records: (np.ndarray, n = 2) Contribution records. First column of the records is supposed to contain
            wghm cell number (cnum) of grid cells
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True
        # step: form data format string
        format_str = 'f'
        if StorageContribution.file_endian == FileEndian.little_endian: format_str = '<%s' % format_str
        else: format_str = '>%s' % format_str

        try:
            f = open(filename, 'wb')
            f.write(records.astype(format_str))
        except: succeed = False

        return succeed

    @staticmethod
    def save_shapefile(filename:str, vertices:list, colnames:list, records:np.ndarray):
        '''
        Saves result into shapefile.

        :param filename: (string) Name of the output file
        :param vertices: (list) List of geo-vertices of each grid cell or polygon
        :param colnames: (list) Name of attributes
        :param records: (np.ndarray) Records of each grid cell
        :return: (boolean) True on success, False otherwise
        '''
        nrow, ncol = len(vertices), len(colnames)
        if records.shape != (nrow, ncol): return False

        succeed = True
        g = shp.Writer(shp.POLYGON)

        for cname in colnames: g.field(cname, 'N', 27, 19)

        for i in range(nrow):
            g.poly(parts=vertices[i], shapeType=shp.POLYGON)
            # g.records(records[i].tolist())
            g.record(*records[i].tolist())

        g.save(filename)

        # saving projection string
        if os.path.exists(filename):
            filename = filename[:-3] + 'prj'
            try:
                f = open(filename, 'w')
                prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                f.write(prj_string)
            except: succeed = False
        else: succeed = False

        return succeed

    @staticmethod
    def read_unf(filename, file_endian=FileEndian.big_endian, ncol=-1):
        '''
        This function reads the WaterGAP binary output and returns data into numpy array.

        Parameters:
        :param filename: (string) WaterGAP binary output filename. Filename must follow the WaterGAP standard i.e
                         it should have UNF extension with a digit at the end. The digit could be either
                         one of the followings:
                                0     (indicating that the file contains 4-byte float values)
                                1     (indicating that the file contains 1-byte integer values)
                                2     (indicating that the file contains 2-byte integer values)
                            or  4     (indicating that the file contains 4-byte integer values)
        :param file_endian: (FileEndian Enum) The endianness of the binary file. Value could be 1 i.e. small endian (windows
                         system) or 2 for big endianness (UNIX system)
        :param ncol: (Integer) No of columns each rows must have. Only if ncol > 1, extracted data will be
                         divided into rows and columns; otherwise the fucntion will return 1-d array. If
                         ncol is not provided, the function will try to read the ncol from the filename.
                         ncol is specified by a number appearing in the filename before the file extension
                         with a preceding dot (.) and followed by another usual dot (for extension).
                         Example of WaterGAP file: ground_water_2018.12.UNF0; the file contains ground water
                         information of 2018. Each row contains 12 values (i.e., ncol = 12; it also mean that
                         the file contains monthly values). The values are 4-byte floating point numbers.
        :return: (2-d or 1-d) array depending on ncol value on success;
                  otherwise, an empty array

        Example:
        >>> filename = os.path.join(wgap_output_directory, 'G_TOTAL_STORAGES_km3_2003.12.UNF0')
        >>> tws_2003 = WGapOutput.read_unf(filename, FileEndian.big_endian, 12)
        >>> tws_2003.shape # assuming wghm version 2.2d
        (67420, 12)
        >>> tws_2003 = WGapOutput.read_unf(filename, ncol=12)
        >>> tws_2003.shape # assuming wghm version 2.2d
        (67420, 12)
        >>> tws_2003 = WGapOutput.read_unf(filename, file_endian=FileEndian.big_endian)
        >>> tws_2003.shape # assuming wghm version 2.2d
        (67420, 12)
        >>> tws_2003 = WGapOutput.read_unf(filename)
        >>> tws_2003.shape # assuming wghm version 2.2d
        (67420, 12)
        '''

        # step: check if file exists
        if not os.path.exists(filename): return []

        # step: find the data type in output file mentioned in as the extension of filename
        unf_type = -1
        try: unf_type = int(filename[-1])
        except: pass

        if unf_type not in [0, 1, 2, 4]: return []
        dtype = '>'
        if file_endian == FileEndian.little_endian: dtype = '<'

        if unf_type == 0: dtype += 'f'
        elif unf_type == 1: dtype += 'b'
        elif unf_type == 2: dtype += 'h'
        elif unf_type == 4: dtype += 'i'
        else: return None

        # step: find no. of columns as to data will be reshaped. If ncol is not provided,
        # try to find the ncol from the filename
        if ncol < 1:
            temp = os.path.split(filename)[-1]
            if temp.count('.') >= 2:
                try:
                    ndx1 = temp.find('.') + 1
                    ndx2 = temp[ndx1:].find('.')
                    ncol = int(temp[ndx1:ndx1 + ndx2])
                except: pass
            if ncol < 1: ncol = 1

        # step: read model output file
        d = np.fromfile(filename, dtype=dtype)

        # step: reshape data if ncol is larger than 1
        if ncol > 1:
            nrow = d.size//ncol
            d = d.reshape(nrow, ncol)

        return d

    @staticmethod
    def storage_contribution(prediction_directory:str, celllist_from_file:str, start_year:int, end_year:int, output_directory:str,
                             output_filename_prefix:str, prediction_type:str='monthly', method:str='seasonal_amplitude',
                             contribution_type:str='annual', output_format:str='both', export_cell_geo_coordinates:bool=True):
        '''
        computes contribution of storage components to a total storage property.

        :param prediction_directory: (string) Prediction directory
        :param celllist_from_file: (string) Name of the file from which target cell numbers will be read in
        :param start_year: (int) Prediction Start Year
        :param end_year: (int) Prediction End Year
        :param output_directory: (string) Directory to save outputs
        :param output_filename_prefix: (string) Filename prefix
        :param prediction_type: (string) Monthly or Daily predictions
        :param method: (string) Describe the property of TWS to be calculated
        :param contribution_type: (string)
        :param output_format: (string) Output file format. Possible values are 'shape', 'binary' or 'both'
        :param export_cell_geo_coordinates: (boolean) Flag describes whether or not cell coordinates are to be exported
        :return: (boolean) True on success, False otherwise
        '''

        succeed = True
        if prediction_type not in ['monthly', 'month', 'daily365', 'daily.365', 'daily31', 'daily.31']: return False
        if method not in ['seasonal_amplitude', 'seasonal amplitude', 'amplitude', 'seasonalamplitude']: return False
        if output_format not in ['shape', 'binary', 'both']: return False
        if contribution_type not in ['annual', 'long-term', 'both']: return False
        if not os.path.exists(prediction_directory): return False
        if not os.path.exists(output_directory): return False

        succeed = StorageContribution.set_target_cells(celllist_from_file)
        StorageContribution.set_start_year(start_year)
        StorageContribution.set_end_year(end_year)
        succeed = StorageContribution.set_prediction_type(prediction_type)
        StorageContribution.model_output_directory = prediction_directory
        StorageContribution.output_directory = output_directory
        StorageContribution.export_cell_geo_coordinates = export_cell_geo_coordinates

        succeed = StorageContribution.is_okay()
        if not succeed: return False

        if method in ['seasonal_amplitude', 'seasonal amplitude', 'amplitude', 'seasonalamplitude']:
            succeed = StorageContribution.contribution_to_seasonal_amplitude(contribution_type=contribution_type, filename_prefix=output_filename_prefix,
                                                                             output_format=output_format)
        else: succeed = False

        return succeed

    @staticmethod
    def draw_contribution_pie(lons:np.ndarray, lats:np.ndarray, contributions:np.ndarray, colors:list=[], labels:list=[], 
                              visible_coord_grid_resolution:tuple=(2, 2), figsize:tuple=(14,8), border_color:str='#9C9C9C', 
                              background_color:str='#FFFFBE', offset:float=0.5, coordsys_text:str='', author_text:str='', 
                              acknowledge_text:str='', tight_layout:bool=True, north_arrow_props:dict={}, title:str='', 
                              filename:str='', additional_text_loc:int=3, fig=None, ax=None):
        '''
        the function create contribution map as pies of storage contribution in each cell
        
        :param lons: (numpy array of shape [n, 5]) longitudes of cell vertices of each cell polygon. each row consists of
                     5 lonitude vlaues of five vertices of the target cell polygon
        :param lats: (numpy array of shape [n, 5]) latitudes of cell vertices of each cell polygon. each row consists of
                     5 latitude values of five vertices of the target cell polygon
        :param contributions: (numpy array) contribution dataset. number of rows must be same as the no. of rows of both
                     lons and lats
        :param colors: (list of python color strings or colors) list of colors for each storage variable. length must be
                     in agreement with the number of variables i.e. no. of columns of contributions dataset
        :param labels: (list of string) labels of variables. length of the list must be in agreement with variable count
        :param visible_coord_grid_resolution: (tuple of float) if value is provided, a grid will be drawn on the map with
                     specific resolution. the default rosolution is 2 by 2 degree
        :param figsize: (tuple of float) size of the figure
        :param borber_color: (python color string or color) color border of each cell polygon
        :param background_color: (python color string or color) background color of the polygon
        :param offset: (string) ofset of the visible grid. default is 0.5
        :param coordsys_text: (string) description of the coordinate system
        :param author_text: (string) author's name and data
        :param acknowledge_text: (string) any acknowledgement. text would be written in brackets i.e., []
        :param tight_layout: (boolean) a flag to describe if tight layout would be used
        :param north_arrow_props: (dict) North arrow properties. The dictionary must have the following entries
                    key name        value type      mandatory/optinal       description
                    -----------     ------------    ------------------      --------------------------------------------
                    pos_x           float           mandatory               x position of the center of the north arrow
                    pos_y           float           mandatory               y position of the center of the north arrow
                    width           float           mandatory               width of the arrow from the center to both
                                                                            directions of the x axis
                    height          float           mandatory               height of the arrow from the center to both
                                                                            directions of the y axis
                    line_width      float           optional                line width of the north arrow. default is 0.05
                    head_width      float           optional                width of arrow heads. defaults is 0.25
                    
                    note: if the property dictionary is not provided or the mandatory element is not found in the dictionary,
                    north arrow will not the drawn; no error message will be thrown.
        :param title: (string, optional) title of the figure 
        :param filename: (string, optional) name of the output file where the figure will be saved
        :param additional_text_loc: (int/string) location of additional text like coordination system or author name
        :param fig: (matplotlib figure) figure object. if not provided figure object will be created
        :param ax: (matplotlib axes) axes object. if not provided, this object will be created
        :return: (tuple of boolean, matplotlib figure and matplotlib axes) in addition to figure and subplot the function
                    returns True on sucess and False on failure
        '''
        succeed = True
        
        if not fig: fig = plt.figure(figsize=figsize)
        if not ax: ax = plt.axes()
        else: ax.cla()
        ax.set_aspect('equal')

        nrow, ncol = contributions.shape
        
        if lons.shape[0] != lats.shape[0] != nrow: succeed = False
        
        # generate color list when colors are not provided or when color list is not in agreement with variable count
        if len(colors) != ncol:
            if ncol == 5: colors = ['#A3FF73', '#FFFFFF', '#686868', '#002673', '#73B2FF']
            elif ncol == 7: colors = ['#D3FFBE', '#00E6A9', '#73DFFF', '#00A9E6', '#005CE6', '#002673', '#FFFFFF']
            else: return False
        
        # generate legend label list when labels are not provided or when list of labels is not in agreement 
        # with variable count
        if len(labels) != ncol: 
            labels = []
            for i in range(1, ncol + 1): labels.append('Storage Variable %d' % i)
        
        lon_mins, lon_maxs = lons.min(axis=1), lons.max(axis=1)
        lat_mins, lat_maxs = lats.min(axis=1), lats.max(axis=1)
        
        x_min, x_max, y_min, y_max = lon_mins.min(), lon_maxs.max(), lat_mins.min(), lat_maxs.max()
        
        # draw grid on map
        # start ...
        if visible_coord_grid_resolution:
            def dd2dms(dd:float):
                '''
                the function converts decimal degree to degree-minute-second
                
                :param dd: (float) decimal degree
                :return: (tuple) a tuple of degree, minutes and second
                '''
                mnt, sec = divmod(dd*3600, 60)
                deg, mnt = divmod(mnt, 60)
                return deg, mnt, sec
            
            def dms_str(dd:float, tp='lon'):
                '''
                the function generates degree-minute-second string from a decimal degree
                
                :param dd: (float) decimal degree
                :return: (string) a string of degree-minute-second
                '''
                
                deg, mnt, sec = dd2dms(dd)
                direction = ''
                if tp == 'lat':
                    direction = 'N'
                    if deg < 0: direction = 'S'
                elif tp == 'lon':
                    direction = 'E'
                    if deg < 0: direction = 'W'
                
                deg = abs(deg)
                return '%d°%d\'%0.f\"%s' % (deg, mnt, sec, direction)
        
            xr, yr = visible_coord_grid_resolution # x and y resolution
            cx = list(np.arange((x_min//xr) * xr, (x_max//xr + 2) * xr, xr))    # coordinates in x
            cy = list(np.arange((y_min//yr) * yr, (y_max//yr + 2) * yr, yr))    # coordinates in y
            #cx_min, cx_max, cy_min, cy_max = cx[0], cx[-1], cy[0], cy[-1]
            for p in cx: 
                try:
                    ndx1, ndx2 = np.where(lon_mins==p), np.where(lon_maxs==p)
                    
                    min1, min2 = lat_mins[ndx1].min(), lat_mins[ndx2].min()
                    cy_min = min(min1, min2) // 0.5 * 0.5
                    
                    max1, max2 = lat_maxs[ndx1].max(), lat_maxs[ndx2].max()
                    cy_max = max(max1, max2) // 0.5 * 0.5
                    
                    cy_min, cy_max = cy_min - 0.5, cy_max + 0.5
                    ax.plot([p, p], [cy_min, cy_max], color='grey', linewidth=2)
                    ax.text(p, cy_min - 0.1, dms_str(p, tp='lon'), va='top', ha='center', fontsize=8)
                    ax.text(p, cy_max + 0.1, dms_str(p, tp='lon'), va='bottom', ha='center', fontsize=8)
                except: pass
            for p in cy: 
                try:
                    ndx1, ndx2 = np.where(lat_mins==p), np.where(lat_maxs==p)
                    
                    min1, min2 = lon_mins[ndx1].min(), lon_mins[ndx2].min()
                    cx_min = min(min1, min2) //0.5 * 0.5
                    
                    max1, max2 = lon_maxs[ndx1].max(), lon_maxs[ndx2].max()
                    cx_max = max(max1, max2) // 0.5 * 0.5
                    
                    cx_min, cx_max = cx_min -  0.5, cx_max + 0.5
                    ax.plot([cx_min, cx_max], [p, p], color='grey', linewidth=2)
                    ax.text(cx_min - 0.1, p, dms_str(p, tp='lat'), rotation='vertical', va='center', ha='right', fontsize=8)
                    ax.text(cx_max + 0.1, p, dms_str(p, tp='lat'), rotation='vertical', va='center', ha='left', fontsize=8)
                except: pass
        # ... end
        
        
        xlim = (x_min - offset, x_max + offset)
        ylim = (y_min - offset, y_max + offset)
        
        centers = np.concatenate(((lon_mins+0.25).reshape(nrow, 1), (lat_mins+0.25).reshape(nrow,1)), axis=1)
        wedgeprops = {'edgecolor': border_color, 'linewidth': 0.5}
        for i in range(nrow):
            x, y = lons[i], lats[i]
            ax.plot(x, y, color=border_color, linewidth=0.5)
            ax.fill(x, y, color=background_color, linewidth=0.5)
            patches, text = ax.pie(contributions[i], labels=None, wedgeprops=wedgeprops, colors=colors, radius=0.2, 
                                    center=centers[i])
        
        legend = ax.legend(patches, labels, loc='best', title='Legend')
        plt.setp(legend.get_title(), fontweight='bold')
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        
        additional_text = ''
        if coordsys_text: additional_text = coordsys_text
        if author_text: additional_text += '\n\n' + author_text
        if acknowledge_text: additional_text += '\n' + acknowledge_text
        
        if additional_text:
            anchored_text = AnchoredText(additional_text, loc=additional_text_loc, borderpad=0.,frameon=False) #, prop=dict(fontweight="bold"))
            ax.add_artist(anchored_text)
        
        # draw north arrow
        # start ...
        def north_arrow(x:float, y:float, w:float, h:float, line_width:float, head_width:float, color:str='black'):
            '''
            the function draws a north arrow
            
            :param x: (float) postition x
            :param y: (float) position y
            :param w: (float) width of the north arrow on both sides of x axis from x, y
            :param h: (float) height of the north arrow on both sides of y axis from x, y
            :param line_width: (float) line width of the nort arrow
            :param head_width: (float) width of the head
            :param color: (python color string or color) color of the arrow
            :return: None
            '''
            
            ax.arrow(x, y, 0,+h, head_width=head_width, width=line_width, length_includes_head=True, color=color)
            ax.arrow(x, y, 0,-h, head_width=head_width, width=line_width, length_includes_head=True, color=color)
            ax.arrow(x, y, +w,0, head_width=head_width, width=line_width, length_includes_head=True, color=color)
            ax.arrow(x, y, -w,0, head_width=head_width, width=line_width, length_includes_head=True, color=color)
            
            ax.text(x, y+h, 'N', fontsize=15, fontweight='bold', color=color, ha='center')
        # end of inner function
        
        nap = north_arrow_props
        if nap and len(nap) >= 4:
            line_width=0.05
            head_width=0.25
            arrow_color='dimgrey'
            
            proceed = True
            try: pos_x, pos_y, width, height = nap['pos_x'], nap['pos_y'], nap['width'], nap['height'] 
            except: proceed = False
            
            if proceed:
                try: line_width = nap['line_width']
                except: pass
            
                try: head_width = nap['head_width']
                except: pass
            
                try: arrow_color = nap['arrow_color']
                except: pass
                
                north_arrow(pos_x, pos_y, width, height, line_width, head_width, color=arrow_color)
        # ... end
        
        if title: ax.set_title(title, fontsize=14, color='black', ha='center')
        
        if tight_layout: fig.tight_layout()
        
        if filename: fig.savefig(filename, dpi=600)
        
        return succeed, fig, ax
    
    @staticmethod
    def add_shapefile(ax, filename:str, colors:list=[], fontsize:int=20, linewidth:float=1, text_record_index:int=-1):
        '''
        this function draws shapes from a shapefile on a given axes.
        
        :param ax: (matplotlib axes) subplot on which the shapes to be drawn
        :param filename: (str) name of the shapefile
        :param colors: (list of pythor color strings or colors, optional) color for each shapes in the shapefile. length
                        of this list should be equal to the no. of shapes in the shapefile. however, if the lenth is
                        not in agreement with the no. of shapes, default 'red' would be assigned to all shape borders
        :param fontsize: (int, optional) font size of the shape name or title
        :param linewidth: (float, optional) width of the border
        :param text_record_index: (int, optional) column index of the title or name of the shape
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True
        
        if colors:
            if not type(colors) is list: colors = [colors]
        else: colors = ['red']
        
        
        try:
            sf = shp.Reader(filename)
            nShapes = len(sf.shapes())
            
            if len(colors) != nShapes: colors = colors * nShapes
            
            for i in range(nShapes):
                sp = sf.shape(i)
                pnts = np.array(sp.points)
                lons, lats = pnts[:, 0], pnts[:, 1]
                
                ax.plot(lons, lats, color=colors[i], linewidth=linewidth)
                
                if text_record_index >= 0:
                    sname = sf.record(i)[1]
                    x, y = np.mean(lons), np.mean(lats)
                    ax.text(x, y, sname, fontsize=20, color=colors[i], fontweight='bold')
            sf.close()
        except: succeed = False
        
        return succeed
    
    @staticmethod
    def get_cell_edge_coordinates_from_cellnum(cell_num_from_file:str):
        '''
        generates coordinates of cell edges from cell number file. these edge coordinateds are used to draw the cell
        
        :param cell_num_from_file: (string) cell number filename
        :return: (tuple of numpy arrays) edge longitudes, edge latitudes
        '''
        
        cell_list = []
        
        temp = GlobalGrid.read_cell_info(cell_num_from_file)
        if type(temp[0]) is list:
            for cl in temp: cell_list += cl
        else: cell_list += temp
        
        lons, lats = None, None
        for cnum in cell_list:
            centroid = GlobalGrid.get_wghm_centroid(cnum)
            temp = GlobalGrid.cell_vertices([centroid], degree_resolution=0.5)
            temp = np.array(temp[0])
            x, y = temp[:, 0].reshape(1,5), temp[:, 1].reshape(1,5)
            try: 
                lons = np.concatenate((lons, x), axis=0)
                lats = np.concatenate((lats, y), axis=0)
            except: lons, lats = x, y
        
        return lons, lats
        
    @staticmethod
    def get_cell_edge_coordinates_from_unf(filename_coord_x:str, filename_coord_y:str):
        '''
        reads the edge coordinate lists from UNF files.
        
        :param filename_coord_x: (string) filename from which longitudes will be retrieved
        :patam filename_coord_y: (string) filename from which latitudes will be retiieved
        :return: (tuple of numpy arrays) edge longitudes, edge latitudes
        '''
        lons = StorageContribution.read_unf(filename_coord_x)
        lats = StorageContribution.read_unf(filename_coord_y)
        
        if type(lons) is np.ndarray and type(lats) is np.ndarray and lons.shape == lats.shape: return lons, lats
        else: return np.array([]), np.array([])

    @staticmethod
    def contributoin_map_animation(filenames_data:list, lons:np.ndarray, lats:np.ndarray, titles:list=[], colors:list=[], 
                                      legend_labels:list=[], north_arrow_properties:dict={}, coordsys_text:str='', author_text:str='', 
                                      acknowledge_text:str='', interval=200, output_filename:str='', dpi:int=300, figsize:tuple=(14, 8), 
                                      fps:int=1, add_shapefile:str='', name_record_index:int=-1,
                                      visible_coord_grid_resolution:tuple=(), fun_dmanip:callable=None, additional_text_loc:int=3):
        '''
        the function creates animation of multiple contribution maps drawn using different data sources
        
        :param filenames_data: (list of string) data filenames
        :param lons: (numpy array of shape [n, 5]) same as draw_contribution_pie function parameter
        :param lats: (numpy array of shape [n, 5]) same as draw_contribution_pie function parameter
        :param titles: (list of string) frame titles
        :param colors: (list of python color strings or colors) same as draw_contribution_pie function parameter
        :param legend_labels: (list of string) labels of variables. length of the list must be in agreement with variable count
        :param visible_coord_grid_resolution: (tuple of float) same as draw_contribution_pie function parameter
        :param figsize: (tuple of float) same as draw_contribution_pie function parameter
        :param coordsys_text: (string) same as draw_contribution_pie function parameter
        :param author_text: (string) same as draw_contribution_pie function parameter
        :param acknowledge_text: (string) same as draw_contribution_pie function parameter
        :param north_arrow_props: (dict) same as draw_contribution_pie function parameter
        :param output_filename: (string, optional) name of the output file where the figure will be saved
        :param interval: (int) delay time in millisec between two frames
        :param dpi: (int) output resolution
        :param add_shapefile: (string, optinal) shape filename, if shapes to be drawn to the top 
        :param name_record_index: (int, optinal) index of the record field to be added in the map as text
        :param fun_dmanip: (callable, optional) data manipulation function
        :param additional_text_loc: (int/string) same as draw_contribution_pie function parameter
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True
        
        nframes = len(filenames_data)
        
        if not filenames_data: succeed = False
        elif titles and len(titles) != nframes: succeed = False
        
        if succeed:
            if not titles: titles = [''] * nframes
            
            writer=ani.ImageMagickFileWriter(fps=fps)
            
            fig = plt.figure(figsize=figsize)
            ax = plt.axes()
               
            def init(): pass # do nothing
            def update(i):
                title = titles[i]
                
                filename = filenames_data[i]
                r = StorageContribution.read_unf(filename)
                nrow, ncol = r.shape
                
                if fun_dmanip: d = fun_dmanip(r)
                else: d = np.concatenate((r[:, 1:5], r[:, 5:].sum(axis=1).reshape(nrow, 1)), axis=1)
                
                StorageContribution.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                                   offset=1.0, north_arrow_props=north_arrow_properties, coordsys_text=coordsys_text,
                                   author_text=author_text, acknowledge_text=acknowledge_text, title=title, ax=ax, fig=fig, additional_text_loc=additional_text_loc)
                if add_shapefile: StorageContribution.add_shapefile(ax, add_shapefile, colors=['red'], text_record_index=name_record_index)
                
            frames = range(nframes)
            anim = ani.FuncAnimation(fig, update, init_func=init, frames=frames, interval=interval, repeat=True)
            
            if output_filename: anim.save(output_filename, dpi=dpi, writer=writer)
            else: plt.show()
        
        return succeed

    @staticmethod
    def stddev_of_contribution_unf(directory: str, unf_prefix: str, nyears: int, nvertices: int = 5,
                                   classify: bool = False):
        '''
        Calculates standard deviation of yearly storage contributions using UNF files generated during storage contribution
        calculation.

        :param directory: (string) input directory
        :param unf_prefix: (string) filename prefix
        :param nyears: (int) number of contribution years
        :param nvertices: (int, optional) number of vertices of each cell, default is 5
        :param classify: (boolean, optional) flag for classifying std. deviation records
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True

        def get_vertices():
            '''
            Reads vertex coordinates from unf files and combines x and y coordinates.
            :return: (numpy array) combined coordinates of vertices
            '''
            flons = os.path.join(directory, '%s_coordinate_X.%d.unf0' % (unf_prefix, nvertices))
            flats = os.path.join(directory, '%s_coordinate_Y.%d.unf0' % (unf_prefix, nvertices))

            lons, lats = StorageContribution.read_unf(flons), StorageContribution.read_unf(flats)
            if not (type(lons) is np.ndarray and type(lats) is np.ndarray and lons.shape == lats.shape): return []

            nrow, ncol = lons.shape
            lons = lons.reshape(nrow, ncol, 1)
            lats = lats.reshape(nrow, ncol, 1)
            temp = np.concatenate((lons, lats), axis=2).tolist()

            vertices = []
            for v in temp: vertices.append([v])

            return vertices
        # ... end of inner function

        def record_classification(data:np.ndarray, class_breaks:list = ()):
            '''
            Classification of data various groups.

            :param data: (numpy array) data
            :param class_breaks: (list or tupple of float) class break points. default classes are 0-0.01, 0.01-0.02, 0.02-0.05,
                                0.05-0.10, 0.10-0.15, 0.15-0.20, 0.20-0.25, 0.25-0.30, 0.30+
            :return: (numpy array) class numbers
            '''
            cr = data.copy()

            cnumber = 1
            if not class_breaks: class_breaks = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]

            hi = class_breaks[0]
            ndx = np.where(data <= hi)
            cr[ndx] = cnumber

            cnumber += 1
            for i in range(len(class_breaks) - 1):
                lo = class_breaks[i]
                hi = class_breaks[i + 1]

                ndx = np.where((data > lo) & (data <= hi))
                cr[ndx] = cnumber
                cnumber += 1

            lo = class_breaks[-1]
            ndx = np.where(data > lo)
            cr[ndx] = cnumber

            return cr
        # ... end of inner function

        # step: read coordinate of vertices
        vertices = get_vertices()

        # step: read storage contributions (from unf files) and compute std. deviation
        attribs = ['cnum']
        records = np.array([])
        try:
            for key, value in StorageContribution.storage_variables.items():
                if key == 'totalstorage': continue

                attribs.append(value['acronym'])

                filename = os.path.join(directory, '%s_%s.%d.unf0' % (unf_prefix, key, nyears + 1))
                if not os.path.exists(filename): return False

                d = StorageContribution.read_unf(filename)
                nrow, ncol = d.shape
                d_std = np.std(d[:, 1:], axis=1).reshape(nrow, 1)

                try: records = np.concatenate((records, d_std), axis=1)
                except: records = np.concatenate((d[:, 0].reshape(nrow, 1), d_std), axis=1)
        except: succeed = False

        if succeed:
            # step: classify data
            if classify:
                records[:, 1:] = record_classification(records[:, 1:])
                filename = os.path.join(directory, '%s_%dyear_stdard_dev_classnum.shp' % (unf_prefix, nyears))
            else: filename = os.path.join(directory, '%s_%dyear_stdard_dev.shp' % (unf_prefix, nyears))

            # step: save records as shape file
            succeed = StorageContribution.save_shapefile(filename, vertices, attribs, records)

        return succeed

    @staticmethod
    def plot_storage_change(dS:np.ndarray, start_year:int, end_year:int, varnames:list, figsize:tuple=(20, 6),
                            yaxis_label:str=r'$km^3/month$', ylim:tuple=(), title:str='', xdate_interval:int=4,
                            filename:str=''):
        nrow, ncol = dS.shape

        if len(varnames) != ncol: return None
        hi, lo = np.zeros(nrow), np.zeros(nrow)
        x = None

        # inner function
        from calendar import monthrange
        from datetime import datetime
        def month_end_dates():
            dates = []
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    day = monthrange(year, month)[1]
                    dates.append(datetime(year, month, day))
            return np.array(dates)

        # ... end of inner function

        # inner function
        def add_bar(d:np.ndarray, label:str='', color:str=''):
            bottom = hi.copy()

            m = np.zeros(120, dtype=np.bool)

            ndx = np.where(d < 0.0)
            m[ndx] = True

            bottom[m] = lo[m]

            # update hi and lo
            lo[m] += d[m]
            hi[~m] += d[~m]

            plt.bar(x, d, bottom=bottom, color=color, width=20, label=label)

        # ... end of inner function

        colors = []
        for v in varnames: colors.append(StorageContribution.get_storage_color(v))

        # create figure
        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(111)

        x = month_end_dates()
        for i in range(ncol): add_bar(dS[:, i], label=varnames[i], color=colors[i])
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=xdate_interval))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
        fig.autofmt_xdate(rotation=90)

        ax.set_ylabel(yaxis_label, fontsize=18)
        if ylim: ax.set_ylim(ylim[0], ylim[1])

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)

        if title: ax.set_title(title, fontsize=20)

        # add legend
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='best', frameon=False, fontsize=18, ncol=ncol,
                  columnspacing=0.05)

        fig.tight_layout()
        if filename: fig.savefig(filename, dpi=600)