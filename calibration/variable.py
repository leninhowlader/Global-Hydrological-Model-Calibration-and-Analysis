__author__ = 'mhasan'

import sys, numpy as np, os
sys.path.append('..')
from calibration.enums import FileType, FileEndian, PredictionType, SortAlgorithm, CompareResult, ObjectiveFunction
from utilities.fileio import read_binary_file, read_flat_file, write_flat_file, acquire_lock, release_lock
from calibration.stats import stats
from calendar import isleap
from collections import OrderedDict
from calibration.wgapoutput import WGapOutput
from calibration.watergap import WaterGAP

class DataSource:
    def __init__(self):
        self.file_type = FileType.flat
        self.filename = ''

        # properties required for flat files
        self.separator = ','
        self.skip_lines = 0
        self.header = False
        self.data_column_num = -1
        self.data_column_name = ''
        self.data_index_column_nums = []
        self.data_index_column_names = []

        # properties required for binary files
        self.block_size = 0
        self.block_format = ''
        self.file_endian = FileEndian.little_endian

        # properties required for wghm binaries
        self.prediction_type = PredictionType.monthly

    def is_okay(self):
        if not self.filename: return False
        elif self.file_type == FileType.binary and (self.block_size == 0 or not self.block_format): return False
        else: return True

class DataCloud:
    def __init__(self):
        self.data = []                  # one dimensional array
        self.data_indices = []          # two dimensional array
        self.sorted = False
        self.__index_count = -1

    def is_okay(self):
        if not self.data: return False
        elif self.data_indices:
            try:
                index_count = len(self.data_indices[0])
                for i in range(1, len(self.data_indices)):
                    if len(self.data_indices[i]) != index_count: return False
            except: return False

        return True

    def data_length(self): return len(self.data)

    def index_count(self):
        if self.__index_count == -1:
            if not self.data_indices: self.__index_count = 0
            else:
                self.__index_count = 99999
                for i in range(len(self.data_indices)):
                    if len(self.data_indices[i]) < self.__index_count: self.__index_count = len(self.data_indices[i])
                if self.__index_count == 99999: self.__index_count = 0
        return self.__index_count

    def sort(self, algorithm=SortAlgorithm.bubble_sort):
        if not self.sorted:
            if algorithm == SortAlgorithm.bubble_sort: self.bubble_sort()
            else: self.heap_sort()

            self.sorted = True

    def heap_sort(self):
        n = self.data_length()
        if n > 0:
            for k in range(n//2, -1, -1): self.shift_down(k, n)
            while (n-1) > 0:
                self.swap_data(n-1, 0)
                self.shift_down(0, n-1)
                n -= 1
            return True
        else: return False

    def shift_down(self, k, n):
        while k * 2 + 1 < n:
            child = 2 * k + 1
            if ((child + 1 < n) and self.compare_data(child, child + 1) == CompareResult.smaller): child += 1
            if (self.compare_data(k, child) == CompareResult.smaller):
                self.swap_data(child, k)
                k = child
            else: break

    def bubble_sort(self):
        n = len(self.data)
        while True:
            swap_count = 0
            for i in range(n-1):
                for j in range(i+1, n):
                    if self.compare_data(i, j) == CompareResult.larger:
                        self.swap_data(i, j)
                        swap_count += 1
            if swap_count == 0: break

    def swap_data(self, index1, index2):
        temp = self.data[index1]
        self.data[index1] = self.data[index2]
        self.data[index2] = temp

        if self.index_count():
            temp = self.data_indices[index1]
            self.data_indices[index1] = self.data_indices[index2]
            self.data_indices[index2] = temp

    def compare_data(self, index1, index2):
        if self.index_count():
            for i in range(self.__index_count):
                if self.data_indices[index1][i] > self.data_indices[index2][i]: return CompareResult.larger
                elif self.data_indices[index1][i] < self.data_indices[index2][i]: return CompareResult.smaller
            return CompareResult.equal
        else:
            if self.data[index1] > self.data[index2]: return CompareResult.larger
            elif self.data[index1] < self.data[index2]: return CompareResult.smaller
            else: return CompareResult.equal

    def crop(self, indices, values):
        if indices and values and len(indices) == len(values):
            data = []
            ndc = range(len(indices))       # placement of range() function here is just to reduce execution time
            for i in range(len(self.data_indices)):
                for j in ndc:
                    if self.data_indices[i][indices[j]] != values[j]: break
                else: data.append(self.data[i])
            return data
        else: return []

    @staticmethod
    def compare_among_clouds(cloud1, index1, cloud2, index2):
        try:
            index_count1, index_count2 = cloud1.index_count(), cloud2.index_count()
            if index_count1 == index_count2:
                if index_count1 == 0:
                    dp1, dp2 = cloud1.data[index1], cloud2.data[index2]
                    if dp1 == dp2: return CompareResult.equal
                    elif dp1 > dp2: return CompareResult.larger
                    else: return CompareResult.smaller
                elif index_count1 > 0:
                    dn1, dn2 = cloud1.data_indices[index1], cloud2.data_indices[index2]
                    for i in range(index_count1):
                        if dn1[i] > dn2[i]: return CompareResult.larger
                        elif dn1[i] < dn2[i]: return CompareResult.smaller
                    return CompareResult.equal
            else: return CompareResult.incompatible
        except: return CompareResult.incompatible

    @staticmethod
    def cloud_coupling(cloud1, cloud2):
        dt1, dt2 = [], []

        ndx1, ndx2 = 0, 0
        dlen1, dlen2 = cloud1.data_length(), cloud2.data_length()

        while ndx1 < dlen1 and ndx2 < dlen2:
            result = DataCloud.compare_among_clouds(cloud1, ndx1, cloud2, ndx2)
            if result == CompareResult.equal:
                dt1.append(cloud1.data[ndx1])
                dt2.append(cloud2.data[ndx2])
                ndx1 += 1
                ndx2 += 1
            elif result == CompareResult.smaller: ndx1 += 1
            else: ndx2 += 1

        return dt1, dt2

    @staticmethod
    def mathop_between_clouds(cloud1, cloud2, fun='+'):
        succeed = False
        dt1, dt2, ndc = [], [], []

        ndx1, ndx2 = 0, 0
        dlen1, dlen2 = cloud1.data_length(), cloud2.data_length()

        while ndx1 < dlen1 and ndx2 < dlen2:
            result = DataCloud.compare_among_clouds(cloud1, ndx1, cloud2, ndx2)
            if result == CompareResult.equal:
                dt1.append(cloud1.data[ndx1])
                dt2.append(cloud2.data[ndx2])
                ndc.append(cloud1.data_indices[ndx1])
                ndx1 += 1
                ndx2 += 1
            elif result == CompareResult.smaller:
                ndx1 += 1
            else:
                ndx2 += 1

        cloud = DataCloud()
        if dt1:
            dt1 = np.array(dt1)
            dt2 = np.array(dt2)

            d = []
            try:
                if fun == '+': d = dt1 + dt2
                elif fun == '-': d = dt1 - dt2
                elif fun == '*': d = dt1 * dt2
                elif fun == '/': d = dt1 / dt2
                elif fun == '**': d = dt1 ** dt2
            except: pass

            if len(d):
                cloud.data = list(d)
                cloud.data_indices = ndc
                cloud.sorted = True
                succeed = True

        return succeed, cloud

    @staticmethod
    def mathop_within_cloud(operand1, operand2, fun='+'):
        #one, and only one, of the operands must be a cloud object

        succeed, cloud, operand = True, None, 0.0
        if type(operand1) is DataCloud:
            cloud = operand1
            try: operand = float(operand2)
            except: succeed = False
        elif type(operand2) is DataCloud:
            cloud = operand2
            try: operand = float(operand1)
            except: succeed = False
        else: succeed = False

        if succeed:
            d = np.array(cloud.data)

            if len(d):
                try:
                    if fun == '+': d = d + operand
                    elif fun == '-': d = d - operand
                    elif fun == '*': d = d * operand
                    elif fun == '/': d = d / operand
                    elif fun == '**': d = d ** operand
                except: pass

                if len(d):
                    nds = cloud.data_indices
                    cloud = DataCloud()
                    cloud.data = list(d)
                    cloud.data_indices = nds
        else: cloud = None

        return succeed, cloud

    def group_stat(self, group_by, funs):
        ndx_count = self.index_count()
        if not (funs and group_by and ndx_count > 0): return []
        for by in group_by:
            if not (type(by) is int and by < ndx_count): return []

        groups = OrderedDict()
        for i in range(self.data_length()):
            ndx = []
            for x in group_by: ndx.append(self.data_indices[i][x])
            ndx = tuple(ndx)
            try: groups[ndx].append(self.data[i])
            except: groups[ndx] = [self.data[i]]

        for key in groups.keys(): groups[key] = stats.multiple_statistics(groups[key], funs)

        return groups

    def print_data(self, filename, append=True, separator=','):
        succeed = False
        d = []
        for i in range(self.data_length()):
            d.append(self.data_indices[i]+[self.data[i]])
        if d: succeed = write_flat_file(filename, d, separator=separator, append=append)
        return succeed

class Variable:
    def __init__(self):
        self.varname = ''
        self.data_source = DataSource()
        self.data_cloud = DataCloud()
        self.data_obtained = False

    def is_okay(self):
        if not self.varname or not self.data_source.is_okay(): return False
        elif self.data_obtained and not self.data_cloud.is_okay(): return False
        else: return True

class ObsVariable(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.counter_variable = ''
        self.function = ObjectiveFunction.not_specified

    def get_function_name(self):
        return ObjectiveFunction.get_function_name(self.function)

    def is_okay(self):
        if not Variable.is_okay(self) or not self.counter_variable or self.function == ObjectiveFunction.not_specified: return False
        else: return True

    @staticmethod
    def read_variables(lines):
        variables = []

        var = None
        while lines:
            try:
                line = lines.pop(0).strip()
                if line:
                    temp = line.split()
                    temp[0] = temp[0].strip().lower()
                    if temp[0] == 'end': return variables
                    elif temp[0] == '@@':
                        if var: variables.append(var)
                        var = None
                    elif temp[0] == '@': var = ObsVariable()
                    elif var:
                        temp = line.split('=')
                        for i in range(len(temp)): temp[i] = temp[i].strip()
                        if len(temp) >= 2:
                            key, value = temp[0], temp[1]
                            if key in ['var_name', 'varname', 'var name', 'variable_name', 'variable name']: var.varname = value
                            elif key in ['data_column_name', 'data column name']: var.data_source.data_column_name = value
                            elif key in ['data_column_number', 'data column number']:
                                num = -1
                                try: num = int(value.strip())
                                except: pass
                                var.data_source.data_column_num = num
                            elif key in ['index_column_names', 'index column names']:
                                temp = value.strip().split(',')
                                for i in reversed(range(len(temp))):
                                    temp[i] = temp[i].strip()
                                    if not temp[i]: temp.pop(i)
                                var.data_source.data_index_column_names = temp
                            elif key in ['index_column_numbers', 'index column numbers']:
                                temp = value.strip().split(',')
                                for i in reversed(range(len(temp))):
                                    try: temp[i] = int(temp[i].strip())
                                    except: temp.pop(i)
                                var.data_source.data_index_column_nums = temp
                            elif key in ['data_file', 'data file', 'data config_filename']: var.data_source.filename = value
                            elif key in ['data_file_type', 'data file type']:
                                value = value.lower()
                                if value in ['csv', 'text', 'flat', 'flatfile', 'flat file']: var.data_source.file_type = FileType.flat
                                else: var.data_source.file_type = FileType.binary
                            elif key in ['separator', 'seperator']:
                                if value: var.data_source.separator = value
                                else: var.data_source.separator = ' '
                            elif key == "header":
                                value = value.lower()
                                if value in ['yes', 'y', 'true', 't', '1']: var.data_source.header = True
                                else: var.data_source.header = False
                            elif key in ['skip_lines', 'skip lines']:
                                count = 0
                                try: count = int(value)
                                except: pass
                                var.data_source.skip_lines = count
                            elif key in ['chunk_size', 'chunk size', 'block_size', 'block size']:
                                size = 0
                                try: size = int(value)
                                except: pass
                                var.data_source.block_size = size
                            elif key in ['chunk_format', 'chunk format', 'block_format', 'block format']:
                                var.data_source.block_format = value
                            elif key in ['counter_simvar', 'counter_var', 'counter simvar', 'counter var', 'counter obsvar', 'counter variable', 'counter_variable']:
                                var.counter_variable = value
                            elif key in ['function', 'evaluation function', 'objective function', 'evaluation_function', 'objective_function']:
                                var.function = ObjectiveFunction.find_function(value)
            except: return None

    @staticmethod
    def data_collection(obs_vars):
        succeed = True

        # find distinct data-sources
        dsources = []
        try:
            for var in obs_vars:
                add = True
                for ds in dsources:
                    if (var.data_source.file_type == ds.file_type and var.data_source.filename == ds.filename and
                        var.data_source.data_column_name == ds.data_column_name and
                        var.data_source.data_column_num == ds.data_column_num):
                        add = False
                        break
                if add: dsources.append(var.data_source)
        except: succeed = False

        # read data from sources
        data = []
        if succeed and dsources:
            try:
                for ds in dsources:
                    dt = []
                    if ds.data_column_num > 0 or ds.data_column_name:
                        if ds.file_type == FileType.flat:
                            headers, dt = read_flat_file(ds.filename, ds.separator, ds.header, ds.skip_lines)
                            column_nums = []
                            column_names = []
                            if ds.data_column_num > 0:
                                ds.data_column_num -= 1
                                column_nums.append(ds.data_column_num)
                            else:
                                for i in range(len(headers)):
                                    if headers[i].strip().lower() == ds.data_column_name.lower():
                                        ds.data_column_num = i
                                        column_nums.append(ds.data_column_num)
                                        break

                            if ds.data_index_column_nums:
                                for num in ds.data_index_column_nums: column_nums.append(num-1)
                            elif ds.data_index_column_names:
                                for name in ds.data_index_column_names: column_names.append(name.strip())

                            if column_names:
                                for name in column_names:
                                    for i in range(len(headers)):
                                        header = headers[i].strip()
                                        if name.lower() == header.lower():
                                            column_nums.append(i)
                                            break
                                ds.data_index_column_nums = column_nums[1:]
                            # print(column_nums)
                            # for i in reversed(range(len(dt[0]))):
                            #     if i not in column_nums:
                            #         for d in dt: d.pop(i)
                            #         if i < ds.data_column_num: ds.data_column_num -= 1
                            #         if ds.data_index_column_nums:
                            #             for j in range(len(ds.data_index_column_nums)):
                            #                 if i < ds.data_index_column_nums[j]: ds.data_index_column_nums[j] -= 1
                        elif ds.file_type == FileType.binary:
                            print('(Caution) This option has not been implemented!')
                    else:
                        print('(Error) Data column number or column name required!')

                    data.append(dt)
            except: succeed = False

        # post-processing
        if succeed:
            try:
                for var in obs_vars:
                    for i in range(len(dsources)):
                        ds = dsources[i]
                        if (var.data_source.file_type == ds.file_type and var.data_source.filename == ds.filename and
                            (var.data_source.data_column_name == ds.data_column_name or
                            var.data_source.data_column_num == ds.data_column_num + 1)):
                            cnum, ndx_cnums = ds.data_column_num, ds.data_index_column_nums
                            var.data_source.data_column_num = cnum
                            var.data_source.data_index_column_nums = ds.data_index_column_nums
                            dt = data[i]
                            for d in dt:
                                var.data_cloud.data.append(d[cnum])
                                if ndx_cnums:
                                    ndces = []
                                    for n in ndx_cnums: ndces.append(d[n])
                                    var.data_cloud.data_indices.append(ndces)
                            var.data_obtained = True
            except: succeed = False

        return succeed

class SimVariable(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.data_source.file_type = FileType.wghm_binary
        self.cell_groups = []           # two-dimensional array
        self.group_stats = False
        self.compute_anomaly = False
        self.cell_weights = []          # two-dimensional array

    def is_okay(self):
        if not Variable.is_okay(self): return False
        elif self.group_stats:
            if not self.cell_groups: return False
            else:
                for i in range(len(self.cell_groups)):
                    if not self.cell_groups[i] and type(self.cell_groups[i]) is not list: return False
        return True

    def compute_anomalies(self):
        if self.compute_anomaly: self.data_cloud.data = stats.compute_anomalies(self.data_cloud.data)

    @staticmethod
    def read_variables(lines):
        variables = []

        var = None
        while lines:
            try:
                line = lines.pop(0).strip()
                if line:
                    temp = line.split()
                    temp[0] = temp[0].strip().lower()
                    if temp[0] == 'end': return variables
                    elif temp[0] == '@@':
                        if var: variables.append(var)
                        var = None
                    elif temp[0] == '@': var = SimVariable()
                    elif var:
                        temp = line.split('=')
                        for i in range(len(temp)): temp[i] = temp[i].strip()
                        if len(temp) >= 2:
                            key, value = temp[0], temp[1]
                            if key in ['var_name', 'varname', 'var name', 'variable_name', 'variable name']: var.varname = value
                            elif key in ['data_file', 'data file', 'data config_filename']: var.data_source.filename = value
                            elif key in ['value_type', 'value type', 'data_type', 'data type', 'prediction_type', 'prediction_type']:
                                value = value.lower()
                                if value in ['monthly', 'month']: var.data_source.prediction_type = PredictionType.monthly
                                elif value in ['yearly', 'annual', 'year']: var.data_source.prediction_type = PredictionType.yearly
                                elif value in ['daily', 'day']: var.data_source.prediction_type = PredictionType.daily
                            elif key in ['zonal_average', 'zonal average', 'zone flag', 'zone_flag', 'group stats', 'group_stats']:
                                value = value.lower()
                                if value in ['yes', 'y', '1', 'true', 't']: var.group_stats = True
                                else: var.group_stats = False
                            elif key in ['target_grid_cells', 'target_cells', 'target cells', 'target grid cells']:
                                if value.find(':') > 0:
                                    temp = value.split(':')
                                    for i in range(len(temp)): temp[i] = temp[i].strip()
                                    if len(temp) == 2 and temp[0].lower() == 'filename':
                                        filename, temp_str = temp[1], ''

                                        fs = None
                                        try:
                                            fs = open(filename, 'r')
                                            for l in fs.readlines(): temp_str += l
                                        except: temp_str = None
                                        finally:
                                            try: fs.close()
                                            except: pass

                                        if temp_str:
                                            var.cell_groups = SimVariable.read_groups(temp_str, type='int')
                                            temp_str = None
                                else: var.cell_groups = SimVariable.read_groups(value, type='int')
                            elif key in ['compute anomalies', 'compute anomaly' , 'anomaly', 'anomalies', 'calculate anomalies',
                                         'calculate anomaly']:
                                value = value.lower()
                                if value in ['yes', 'y', '1', 'true', 't']: var.compute_anomaly = True
                                else: var.compute_anomaly = False
                            elif key in ['weights', 'cell weights', 'cell_weights']:
                                if value.find(':') > 0:
                                    temp = value.split(':')
                                    for i in range(len(temp)): temp[i] = temp[i].strip()
                                    if len(temp) ==2 and temp[0].lower() == 'filename':
                                        filename, temp_str = temp[1], ''

                                        fs = None
                                        try:
                                            fs = open(filename, 'r')
                                            for l in fs.readlines(): temp_str += l
                                        except: temp_str = None
                                        finally:
                                            try: fs.close()
                                            except: pass

                                        if temp_str:
                                            var.cell_weights = SimVariable.read_groups(temp_str)
                                            temp_str = None
                                else: var.cell_weights = SimVariable.read_groups(value)
            except: return None

    @staticmethod
    def read_groups(groups_str, type='float'):
        groups = groups_str.strip().split(']')
        for i in reversed(range(len(groups))):
            groups[i] = groups[i].strip('[, ').split(',')
            for j in reversed(range(len(groups[i]))):
                try: groups[i][j] = float(groups[i][j].strip('\n '))
                except: groups[i].pop(j)
            if len(groups[i]) == 0: groups.pop(i)

        if type == 'int':
            for i in range(len(groups)):
                for j in range(len(groups[i])): groups[i][j] = int(groups[i][j])

        return groups # 2-D array


    @staticmethod
    def data_collection_old(sim_vars, start_year, end_year): # function can be deleted once the new one becomes functional
        succeed = True

        # collection of distinct data-sources
        data_sources = []
        try:
            for var in sim_vars:
                add = True
                for ds in data_sources:
                    if (var.data_source.file_type == ds.file_type and var.data_source.prediction_type == ds.prediction_type
                        and var.data_source.filename == ds.filename and var.data_source.file_endian == ds.file_endian):
                        add = False
                        break
                if add: data_sources.append(var.data_source)
        except: succeed = False

        # read (collect data from) each distinct data-source
        year_count = end_year - start_year + 1
        data = []
        if succeed:
            try:
                for ds in data_sources:
                    ds_data = []
                    if ds.file_type == FileType.wghm_binary: # which is always true for simulation variables
                        block_format, block_size = '', 0
                        if ds.file_endian == FileEndian.big_endian: block_format += '>'
                        else: block_format += '<'

                        if ds.prediction_type == PredictionType.daily:
                            for i in range(365): block_format += 'f'
                            block_size = 365 * 4
                        elif ds.prediction_type == PredictionType.monthly:
                            for i in range(12): block_format += 'f'
                            block_size = 12 * 4
                        elif ds.prediction_type == PredictionType.yearly:
                            for i in range(365): block_format += 'f'
                            block_size = 365 * 4

                        if block_size and block_format:
                            for year in range(start_year, end_year+1):
                                file_name = ds.filename
                                ndx = file_name.lower().find('[year]')
                                if ndx > 0:
                                    file_name = file_name[:ndx] + str(year) + file_name[ndx+6:]
                                    dt = read_binary_file(file_name, block_size, block_format)
                                    ds_data.append(dt)

                    data.append(ds_data)
            except:
                print('(Error) Failed to read simulation output!')
                succeed = False

        # (post) processing of collected data
        if succeed and data and len(data) == len(data_sources):
            try:
                for var in sim_vars:
                    ndx_ds = -1
                    for i in range(len(data_sources)):
                        ds = data_sources[i]
                        if (var.data_source.file_type == ds.file_type and var.data_source.prediction_type == ds.prediction_type
                            and var.data_source.filename == ds.filename and var.data_source.file_endian == ds.file_endian):
                            ndx_ds = i
                            break

                    if ndx_ds >= 0:
                        dt = data[ndx_ds]
                        if dt and len(dt) == year_count:
                            for i in range(year_count):
                                year_dt = dt[i]
                                year = start_year + i
                                if var.data_source.prediction_type == PredictionType.yearly:
                                    if var.cell_groups:
                                        if var.group_stats or len(var.cell_groups) > 1:
                                            group_ndx = 1 # starts from 1
                                            for group in var.cell_groups:
                                                group_dt = []
                                                for cell in group: group_dt.append(year_dt[cell-1])
                                                d = stats.mean(group_dt)
                                                var.data_cloud.data.append(d)
                                                var.data_cloud.data_indices.append([group_ndx, year])
                                                group_ndx += 1
                                        else:
                                            group = var.cell_groups[0]
                                            for cell in group:
                                                var.data_cloud.data.append(year_dt[cell-1])
                                                var.data_cloud.data_indices.append([cell, year])
                                    else:
                                        for j in range(len(year_dt)):
                                            var.data_cloud.data.append(year_dt[j])
                                            var.data_cloud.data_indices.append([j, year])
                                elif var.data_source.prediction_type == PredictionType.monthly:
                                    if var.cell_groups:
                                        if var.group_stats or len(var.cell_groups) > 1:
                                            group_ndx = 1
                                            for group in var.cell_groups:
                                                group_dt = []
                                                for cell in group: group_dt.append(year_dt[cell-1])

                                                weights = []
                                                if var.cell_weights: weights = var.cell_weights[group_ndx - 1]

                                                for j in range(12):
                                                    month = j + 1
                                                    month_dt = []
                                                    for k in range(len(group)): month_dt.append(group_dt[k][j])
                                                    if weights: var.data_cloud.data.append(stats.weighted_mean(month_dt, weights))
                                                    else: var.data_cloud.data.append(stats.mean(month_dt))
                                                    var.data_cloud.data_indices.append([group_ndx, year, month])
                                                group_ndx += 1
                                        else:
                                            group = var.cell_groups[0]
                                            for cell in group:
                                                for j in range(12):
                                                    month = j + 1
                                                    var.data_cloud.data.append(year_dt[cell-1][j])
                                                    var.data_cloud.data_indices.append([cell, year, month])
                                    else:
                                        for j in range(12):
                                            month = j + 1
                                            for i in range(len(year_dt)):
                                                var.data_cloud.data.append(year_dt[i][j])
                                                var.data_cloud.data_indices.append([i, year, month])
                                elif var.data_source.prediction_type == PredictionType.daily:
                                    is_leap_year = isleap(year)
                                    if var.cell_groups:
                                        if var.group_stats or len(var.cell_groups) > 1:
                                            group_ndx = 1
                                            for group in var.cell_groups:
                                                group_dt = []
                                                for cell in group: group_dt.append(year_dt[cell-1])

                                                weights = []
                                                if var.cell_weights: weights = var.cell_weights[group_ndx - 1]

                                                day = 0
                                                for j in range(59):
                                                    day += 1
                                                    month_dt = []
                                                    for k in range(len(group)): month_dt.append(group_dt[k][j])
                                                    if weights: var.data_cloud.data.append(stats.weighted_mean(month_dt, weights))
                                                    else: var.data_cloud.data.append(stats.mean(month_dt))
                                                    var.data_cloud.data_indices.append([group_ndx, year, day])

                                                if is_leap_year: day += 1

                                                for j in range(59, 365):
                                                    day += 1
                                                    month_dt = []
                                                    for k in range(len(group)): month_dt.append(group_dt[k][j])
                                                    if weights: var.data_cloud.data.append(stats.weighted_mean(month_dt, weights))
                                                    else: var.data_cloud.data.append(stats.mean(month_dt))
                                                    var.data_cloud.data_indices.append([group_ndx, year, day])

                                                group_ndx += 1
                                        else:
                                            group = var.cell_groups[0]
                                            for cell in group:
                                                day = 0

                                                for j in range(59):
                                                    day += 1
                                                    var.data_cloud.data.append(year_dt[cell-1][j])
                                                    var.data_cloud.data_indices.append([cell, year, day])

                                                if is_leap_year: day += 1

                                                for j in range(59, 365):
                                                    day += 1
                                                    var.data_cloud.data.append(year_dt[cell-1][j])
                                                    var.data_cloud.data_indices.append([cell, year, day])

                                    else:
                                        day = 0

                                        for j in range(59):
                                            day += 1
                                            for k in range(len(year_dt)):
                                                var.data_cloud.data.append(year_dt[k][j])
                                                var.data_cloud.data_indices.append([k, year, day])

                                        if is_leap_year: day += 1

                                        for j in range(59, 365):
                                            day += 1
                                            for k in range(len(year_dt)):
                                                var.data_cloud.data.append(year_dt[k][j])
                                                var.data_cloud.data_indices.append([k, year, day])
            except:
                print('(Error) Simulation Output post-processing failed!')
                succeed = False

        return succeed

    @staticmethod
    def data_collection(sim_vars, start_year, end_year):
        succeed = True

        # collection of distinct data-sources
        data_sources = []
        try:
            for var in sim_vars:
                add = True
                for ds in data_sources:
                    if (
                                    var.data_source.file_type == ds.file_type and var.data_source.prediction_type == ds.prediction_type
                        and var.data_source.filename == ds.filename and var.data_source.file_endian == ds.file_endian):
                        add = False
                        break
                if add: data_sources.append(var.data_source)
        except:
            succeed = False

        # read (collect data from) each distinct data-source
        year_count = end_year - start_year + 1
        data = []
        if succeed:
            try:
                for ds in data_sources:
                    ds_data = []
                    if ds.file_type == FileType.wghm_binary:  # which is always true for simulation variables
                        for year in range(start_year, end_year + 1):
                            file_name = ds.filename
                            ndx = file_name.lower().find('[year]')
                            if ndx > 0:
                                file_name = file_name[:ndx] + str(year) + file_name[ndx + 6:]
                                year_dt = WGapOutput.read_unf(file_name, file_endian=ds.file_endian)

                                if year_dt:
                                    for var in sim_vars:
                                        if (var.data_source.file_type == ds.file_type and var.data_source.prediction_type == ds.prediction_type
                                            and var.data_source.filename == ds.filename and var.data_source.file_endian == ds.file_endian):
                                            if var.group_stats:
                                                if var.cell_groups:
                                                    group_ndx = 1
                                                    for j in range(len(var.cell_groups)):
                                                        basin = var.cell_groups[j]
                                                        weights = []
                                                        if var.cell_weights: weights = var.cell_weights[j]

                                                        summary = WGapOutput.summarize(year_dt, basin=basin, weights=weights)

                                                        group_ndx = j + 1
                                                        data_indices = var.data_cloud.data_indices
                                                        if len(summary) == 365:  # that is data is comming from a daily output file (.365 format)
                                                            # add indices
                                                            for day in range(1, 60): data_indices.append([group_ndx, year, day])

                                                            plus_one_day = 0
                                                            if isleap(year): plus_one_day += 1

                                                            for day in range(60 + plus_one_day, 366): data_indices.append([group_ndx, year, day])

                                                            # add data
                                                            var.data_cloud.data += summary
                                                        elif len(summary) == 12:  # that is we are dealing with monthly data
                                                            # add indices
                                                            for month in range(1, 13): data_indices.append([group_ndx, year, month])

                                                            # add data
                                                            var.data_cloud.data += summary
                                                        elif len(summary) == 1:  # yearly data
                                                            # add data
                                                            var.data_cloud.data.append(summary[0])

                                                            # add indices
                                                            var.data_cloud.data_indices.append([group_ndx, year])
                                                else:  # no basin info available
                                                    data_indices = var.data_cloud.data_indices
                                                    summary = WGapOutput.summarize(year_dt)
                                                    if len(summary) == 365:  # daily data
                                                        # add indices
                                                        for day in range(1, 60): data_indices.append([year, day])

                                                        plus_one_day = 0
                                                        if isleap(year): plus_one_day += 1

                                                        for day in range(60 + plus_one_day, 366): data_indices.append([year, day])

                                                        # add data
                                                        var.data_cloud.data += summary
                                                    elif len(summary) == 12:  # that is we are dealing with monthly data
                                                        # add indices
                                                        for month in range(1, 13): data_indices.append([year, month])

                                                        # add data
                                                        var.data_cloud.data += summary
                                                    elif len(summary) == 1:  # yearly data
                                                        # add data
                                                        var.data_cloud.data.append(summary[0])

                                                        # add indices
                                                        var.data_cloud.data_indices.append([year])
                                            else:
                                                clist = []
                                                if var.cell_groups:
                                                    for cgroup in var.cell_groups:
                                                        for c in cgroup:
                                                            if c not in clist: clist.append(c)

                                                if not clist: clist = list(range(1, len(year_dt) + 1))

                                                data_indices = var.data_cloud.data_indices
                                                if len(year_dt[0]) == 365:
                                                    for c in clist:
                                                        cdt = year_dt[c-1]

                                                        for day in range(1, 60): data_indices.append([c, year, day])

                                                        plus_one_day = 0
                                                        if isleap(year): plus_one_day = 1

                                                        for day in range(60 + plus_one_day, 366): data_indices.append([c, year, day])

                                                        var.data_cloud.data += cdt
                                                elif len(year_dt[0]) == 12:
                                                    for c in clist:
                                                        cdt = year_dt[c - 1]
                                                        for month in range(1, 13): data_indices.append([c, year, month])
                                                        var.data_cloud.data += cdt
                                                elif len(year_dt[0]) == 1:
                                                    for c in clist:
                                                        data_indices.append([c, year])
                                                        var.data_cloud.data.append(year_dt[c - 1])

            except:
                print('(Error) Failed to read simulation output!')
                succeed = False

        return succeed

    def dump_time_series_from_model_prediction(self, start_year, end_year, dumping_directory='', additional_attributes=[]):
        '''
        This function will read model predictions and (usually) calculates basin average time-series. Finally
        the timeseries will be dumped as binary files. To avoid unnecessary dumping of large data, the function
        demands data (cell numbers) in its cell_group list. If cell_group is empty, the function returns an
        unsuccessful operation signal.

        If group function i.e., the aggregation function is specified, predictions will be aggregated for each
        group of cell (or basin) and a group id will be assigned. If weights are available in the weights list,
        these weights will be applied during applying aggregation function. The anomaly option will be ignored
        in this operation. Furthermore, the operation will only be performed if the data type is a model output.

        dump format: all values will be formatted/changed to data type 'float' and the file endian type specified
        in data source will be followed. If additional attributes are provided, they will be placed in the beginning
        of each row. If group operation is performed a group id will be added after the the additional attributes;
        then an id for time period (e.g., year or year or month number etc) will be added. Finally, (time-specific)
        values will be placed in the remaining places of the row.

        An example of a row of monthly predictions would look like:
            [add. attrib1, add. attrib2, ...., group id/cell id, year, value of jan, value of feb, .... , value of dec]

        Row sizes of dumped files:
            (1) For monthly output files (...[YEAR].UNF*):
                    len of additional attribute + 1 (for cell/group id) + 1 (for year) + 12 (for each month)
            (2) For daily dot365 output files (not implemented):
                    len of additional attribute + 1 (for cell/group id) + 1 (for year) + 365 (for each day)
            (3) For daily dot12.31 ourput files (not implemented): unknown

        Parameters:
        :param start_year: (int) start year of prediction
        :param end_year: (int) end year of prediction
        :param dumping_directory: (string; optional) path where data to be dumped
        :param additional_attributes: (list of numbers; optional) additional attributes to be dumped
        :return: (bool) True on success,
                        False Otherwise
        '''

        # step: check presence of target cells
        ncell = 0
        for group in self.cell_groups: ncell += len(group)
        if ncell == 0: return False

        # step: check if data source object is okay
        if not self.data_source.is_okay(): return False
        if not self.data_source.file_type == FileType.wghm_binary: return False

        # step: form data format string
        format_str = 'f'
        if self.data_source.file_endian == FileEndian.little_endian: format_str = '<%s'%format_str
        else: format_str = '>%s'%format_str

        # step: for each year from start year to end year read model predictions
        succeed = True
        prediction_filename = self.data_source.filename
        ndx = prediction_filename.lower().find('[year]')
        for year in range(start_year, end_year + 1):
            file_name = prediction_filename[:ndx] + str(year) + prediction_filename[ndx + 6:]
            file_name = os.path.join(WaterGAP.home_directory, WaterGAP.dir_info.output_directory, file_name)
            pred = WGapOutput.read_unf(file_name, file_endian=self.data_source.file_endian)

            if self.group_stats:
                for i in range(len(self.cell_groups)):
                    basin_id = i + 1
                    basin = np.array(self.cell_groups[i])
                    data = pred[basin]

                    if self.cell_weights:
                        weights = self.cell_weights[i]
                        if data.ndim == 1: data = data * weights
                        else: data = data * weights[:, None]

                        data = np.sum(data, axis=0) / np.sum(weights)
                    else: data = np.sum(data, axis=0)

                    # step: append additing attributes and time data (time info i.e., year, month, day etc.)
                    additional_attributes += [basin_id, year]
                    if data.ndim == 1: data = np.append(additional_attributes, data)
                    else:
                        ncol = len(additional_attributes)
                        nrow = data.shape[0]
                        additional_attributes = np.array(additional_attributes * nrow).reshape(nrow, ncol)
                        data = np.concatenate((additional_attributes, data), axis=0)

                    # step: dump data into file
                    ncol = 0
                    if data.ndim == 1: ncol = data.size
                    else: ncol = data.shape[1]

                    dump_filename = self.varname + '.%d.unf0' % (ncol)
                    if dumping_directory: dump_filename = os.path.join(dumping_directory, dump_filename)

                    succeed = self.dump_data_into_file(dump_filename, data.astype(format_str), self.varname)
            else:
                cells = []
                for group in self.cell_groups: cells += group
                data = pred[cells]


        return succeed

    def dump_data_into_file(self, filename, data_bytes, lock_name=''):
        '''
        This function dumps data into specified file in binary (4-byte float) format. Lock will be used to avoid
        conflicts in case of parallel runs, if lock name is provided.

        Parameters:
        :param filename: (string) name of the file
        :param data: (bytes) binary data (as bytes) to be dumped into file
        :param lock_name: (string; optional) name of lockfile. Lock will only be applied if provided
        :return: (bool) True on success,
                        False otherwise
        '''
        succeed = True

        f = None
        if lock_name:
            fd = open(lock_name, 'w')
            if acquire_lock(fd, lock_name):
                try:
                    f = open(filename, 'ab')
                    f.write(data_bytes)
                except: succeed = False
                finally:
                    try: f.close()
                    except: pass
                    release_lock(fd)
            fd.close()
        else:
            try:
                f = open(filename, 'ab')
                f.write(data_bytes)
            except: succeed = False
            finally:
                try: f.close()
                except: pass

        return succeed

class DerivedVariable(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.data_source = None
        self.equation = ''
        self.equ_evaluated = False
        self.compute_anomaly = False

    def is_okay(self):
        if not self.varname or not self.equation: return False
        else: return True

    def evaluate_equation(self, simvars=[], obsvars=[]):
        if not self.equ_evaluated:
            okay = True

            if simvars or obsvars:
                varnames = []
                for v in simvars:
                    if v.varname not in varnames: varnames.append(v.varname)
                for v in obsvars:
                    if v.varname not in varnames: varnames.append(v.varname)

                temp = self.equation.split('+')
                for i in range(len(temp)):
                    temp[i] = temp[i].strip()
                    if temp[i] not in varnames:
                        okay = False
                        break
            else: okay = False

            self.equ_evaluated = okay
            return okay
        else: return True

    def derive_data(self, simvars=[], obsvars=[]):
        succeed = True

        if self.evaluate_equation(simvars, obsvars):
            temp = self.equation.split('+')
            for i in range(len(temp)): temp[i] = temp[i].strip()

            try:
                cloud1 = self.find_variable(temp[0], simvars, obsvars).data_cloud

                for i in range(1, len(temp)):
                    cloud2 = self.find_variable(temp[i], simvars, obsvars).data_cloud
                    succeed, cloud1 = DataCloud.mathop_between_clouds(cloud1, cloud2, fun='+')
                    if not succeed: break

                if succeed: self.data_cloud = cloud1
            except: succeed = False
        else: succeed = False

        return succeed

    def compute_anomalies(self):
        if self.compute_anomaly: self.data_cloud.data = stats.compute_anomalies(self.data_cloud.data)

    def find_variable(self, varname, variables, additional_variables=[]):
        var = None

        for v in variables:
            if v.varname == varname:
                var = v
                break

        if not var:
            for v in additional_variables:
                if v.varname == varname:
                    var = v
                    break
        return var

    @staticmethod
    def read_variables(lines):
        variables = []

        var = None
        while lines:
            try:
                line = lines.pop(0).strip()
                if line:
                    temp = line.split()
                    temp[0] = temp[0].strip().lower()
                    if temp[0] == 'end': return variables
                    elif temp[0] == '@@':
                        if var: variables.append(var)
                        var = None
                    elif temp[0] == '@': var = DerivedVariable()
                    elif var:
                        temp = line.split('=')
                        for i in range(len(temp)): temp[i] = temp[i].strip()
                        if len(temp) >= 2:
                            key, value = temp[0], temp[1]
                            if key in ['var_name', 'varname', 'var name', 'variable_name', 'variable name']:
                                var.varname = value
                            elif key in ['equation']:
                                var.equation = value
                            elif key in ['compute anomalies', 'compute anomaly' , 'anomaly', 'anomalies', 'calculate anomalies',
                                         'calculate anomaly']:
                                value = value.lower()
                                if value in ['yes', 'y', '1', 'true', 't']: var.compute_anomaly = True
                                else: var.compute_anomaly = False
            except: return None
