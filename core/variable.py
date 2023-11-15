__author__ = 'mhasan'

import sys, os, numpy as np, pandas as pd
from datetime import datetime

from utilities.enums import FileType, FileEndian, PredictionType, SortAlgorithm, CompareResult, ObjectiveFunction
from utilities.fileio import FileInputOutput as io
from core.stats import stats
from calendar import isleap
from collections import OrderedDict
from wgap.wgapio import WaterGapIO

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
        self.file_endian = FileEndian.big_endian

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
        self.lower_bound = np.empty(0)
        self.upper_bound = np.empty(0)

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

    def index_count(self): return self.data_indices.shape[1]

    # def sort(self, algorithm=SortAlgorithm.bubble_sort):
    #     if not self.sorted:
    #         if algorithm == SortAlgorithm.bubble_sort: self.bubble_sort()
    #         else: self.heap_sort()

    #         self.sorted = True

    def sort(self):
        if not self.sorted:
            n = self.data_indices.shape[1]
            ii = np.lexsort([self.data_indices[:,i] for i in reversed(range(n))])
            self.data_indices = self.data_indices[ii]
            self.data = self.data[ii]

            if self.lower_bound.shape[0] > 0:
                self.lower_bound = self.lower_bound[ii]
            
            if self.upper_bound.shape[0] > 0: 
                self.upper_bound = self.upper_bound[ii]

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
    def cloud_coupling_old(cloud1, cloud2):
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
    def cloud_coupling(cloud1, cloud2):
        dt1, dt2, lb, ub = np.empty(0), np.empty(0), np.empty(0), np.empty(0)

        ii, jj = DataCloud.index_coupling(cloud1, cloud2)
        dt1 = cloud1.data[ii]
        dt2 = cloud2.data[jj]

        if cloud1.lower_bound.shape[0] > 0:
            lb = cloud1.lower_bound[ii]
            ub = cloud2.lower_bound[ii]
        
        elif cloud2.lower_bount.shape[0] > 0:
            lb = cloud1.lower_bound[jj]
            ub = cloud2.lower_bound[jj]
        
        return dt1, dt2, lb, ub

    @staticmethod
    def index_coupling(cloud1, cloud2):
        def compare(x1, x2):
            for i in range(len(x1)):
                if x1[i] > x2[i]: return 1
                elif x1[i] < x2[i]: return 2    
            return 0
        
        ii, jj = [], []

        cloud1.sort()
        cloud2.sort()

        indices1, indices2 = cloud1.data_indices, cloud2.data_indices

        i, j = 0, 0
        n1, n2 = indices1.shape[0], indices2.shape[0]
        if indices1.shape[1] != indices2.shape[1]: 
            return np.empty(0), np.empty(0)

        while i < n1 and j < n2:
            r = compare(indices1[i], indices2[j])
            if r == 0:
                ii.append(i)
                jj.append(j)
                
                i += 1
                j += 1
            elif r == 1: j += 1
            else: i += 1
        
        return np.array(ii), np.array(jj)

    @staticmethod
    def arithmetic_operation(cloud1, cloud2, func='+'):
        cloud = DataCloud()
        
        try:
            ii, jj = DataCloud.index_coupling(cloud1, cloud2)
            cloud.data_indices = cloud1.data_indices[ii].copy()
            if func == '+':
                cloud.data = cloud1.data[ii] + cloud2.data[jj]
            elif func == '-':
                cloud.data = cloud1.data[ii] - cloud2.data[jj]
            elif func == '*':
                cloud.data = cloud1.data[ii] * cloud2.data[jj]
            elif func == '/':
                cloud.data = cloud1.data[ii] / cloud2.data[jj]
            
            ## decision to be made regarding the uncertainty bound if present.
            ##

            cloud.sorted = True
        except: pass

        return cloud

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
        if d: succeed = io.write_flat_file(filename, d, separator=separator, append=append)
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
    __optionnames = {}
    __optionnames['varname'] = [
        'var_name', 'varname', 'var name', 'variable_name', 'variable name'
    ]
    __optionnames['data_column_name'] = ['data_column_name', 'data column name']
    __optionnames['data_column_number'] = [
        'data_column_number', 'data column number'
    ]

    __optionnames['index_column_names'] = [
        'index_column_names', 'index column names'
    ]
    __optionnames['index_column_numbers'] = [
        'index_column_numbers', 'index column numbers'
    ]
    __optionnames['filename'] = ['data_file', 'data file', 'filename']
    __optionnames['file_type'] = ['data_file_type', 'data file type']

    def __init__(self):
        Variable.__init__(self)
        self.counter_variable = ''
        self.function = ObjectiveFunction.not_specified
        self.epsilon = 0.05

        self.is_multiset = False
        self.multiset_data_column_names = []
        self.multiset_data_column_nums = []

        self.has_uncertainty_bound = False
        self.lower_bound_column_name = ''
        self.upper_bound_column_name = ''

    def get_function_name(self):
        return ObjectiveFunction.get_function_name(self.function)
    
    def get_epsilon(self): return self.epsilon

    def is_okay(self):
        if (not Variable.is_okay(self) 
            or not self.counter_variable 
            or self.function == ObjectiveFunction.not_specified
        ): return False
        else: return True

    @staticmethod
    def read_variables(lines):
        optionnames = ObsVariable.__optionnames

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
                            if key in optionnames['varname']: 
                                var.varname = value
                            elif key in optionnames['data_column_name']:
                                if value.find(',') >= 0:
                                    temp = value.split(',')
                                    for i in range(len(temp)): temp[i].strip()
                                    for i in reversed(range(len(temp))):
                                        if temp[i] == '': temp.pop(i)
                                    
                                    if len(temp) > 0: 
                                        var.is_multiset = True
                                        var.data_source.data_column_name = temp
                                else:
                                    var.data_source.data_column_name = value
                            elif key in optionnames['data_column_number']:
                                
                                if value.find(',') >= 0:
                                    temp=value.split(',')
                                    for i in reversed(range(len(temp))):
                                        try: temp[i] = int(temp[i])
                                        except: temp.pop(i)
                                    
                                    if len(temp) > 0:
                                        var.is_multiset = True
                                        var.data_source.data_column_num = temp
                                else:
                                    num = -1
                                    try: num = int(value.strip())
                                    except: pass
                                    var.data_source.data_column_num = num
                            elif key in ['lower_bound_column_name']:
                                var.lower_bound_column_name = value
                            elif key in ['upper_bound_column_name']:
                                var.upper_bound_column_name = value
                            elif key in optionnames['index_column_names']:
                                temp = value.strip().split(',')
                                for i in reversed(range(len(temp))):
                                    temp[i] = temp[i].strip()
                                    if not temp[i]: temp.pop(i)
                                var.data_source.data_index_column_names = temp
                            elif key in optionnames['index_column_numbers']:
                                temp = value.strip().split(',')
                                for i in reversed(range(len(temp))):
                                    try: temp[i] = int(temp[i].strip())
                                    except: temp.pop(i)
                                var.data_source.data_index_column_nums = temp
                            elif key in optionnames['filename']: 
                                var.data_source.filename = value
                            elif key in optionnames['file_type']:
                                value = value.lower()
                                if value in ['csv', 'text', 'flat', 'flatfile', 'flat file']: 
                                    var.data_source.file_type = FileType.flat
                                else: var.data_source.file_type = FileType.binary
                            elif key in ['separator', 'seperator']:
                                if value: var.data_source.separator = value
                                else: var.data_source.separator = ' '
                            elif key == "header":
                                value = value.lower()
                                if value in ['yes', 'y', 'true', 't', '1']: 
                                    var.data_source.header = True
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
                            elif key in [
                                'borg_epsilon', 'borg epsilon', 'epsilon'
                            ]: 
                                try: var.epsilon = float(value)
                                except: pass
            except: return None

    @staticmethod
    def read_observations(obs_variables):
        succeed = True
        
        for var in obs_variables:
            succeed = False

            file_type = var.data_source.file_type
            if file_type == FileType.flat:
                filename = var.data_source.filename
                separator = var.data_source.separator
                header = var.data_source.header
                skiplines = var.data_source.skip_lines

                if not header: header=None
                else: header = 'infer'

                df = pd.read_csv(
                    filename, sep=separator, skiprows=skiplines, header=header
                )
                if df.shape[0] > 0: succeed = True
                
                # get data from the data frame
                if succeed:
                    colname = var.data_source.data_column_name
                    try:
                        var.data_cloud.data = df.loc[:, colname].values
                    except: pass
                    
                    if len(var.data_cloud.data) == 0:
                        if var.is_multiset:
                            colnum = []
                            for x in var.data_source.data_column_num: 
                                colnum.append(x-1)
                        else: colnum = var.data_source.data_column_num - 1
                        
                        try: 
                            var.data_cloud.data = df.iloc[:, colnum].values
                        except: pass
                    
                    if len(var.data_cloud.data) == 0: succeed = False
                ##

                # read indices
                if succeed:
                    colnames = var.data_source.data_index_column_names
                    try:
                        var.data_cloud.data_indices = df.loc[:, colnames].values
                    except: pass

                    if len(var.data_cloud.data_indices) == 0:
                        colnums = var.data_source.data_index_column_nums
                        colnums = [(x-1) for x in colnums]
                        try:
                            indices = df.iloc[:, colnums].values 
                            var.data_cloud.data_indices = indices
                        except: succeed = False

                    if len(var.data_cloud.data_indices) == 0: succeed = False
                ##

                ## read uncertainty bounds
                if succeed:
                    lb, ub = np.empty(0), np.empty(0)
                    if var.lower_bound_column_name:
                        colname = var.lower_bound_column_name
                        lb = df.loc[:, colname].values

                    if var.upper_bound_column_name:
                        colname = var.upper_bound_column_name
                        ub = df.loc[:, colname].values 
                    
                    if lb.shape[0] > 0 and lb.shape == ub.shape:
                        var.data_cloud.lower_bound = lb
                        var.data_cloud.upper_bound = ub
                        var.has_uncertainty_bound = True
                ###

            if succeed: var.data_cloud.sort()
            else: break
        
        return succeed   

    @staticmethod
    def data_collection2(obs_vars):
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
                            headers, dt = io.read_flat_file(ds.filename, ds.separator, ds.header, ds.skip_lines)
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
    """
    Class of Simulation Variable objects that describes the WaterGAP output
    variables

    Attributes/Properties:
    (attributes inherited from the superclass)
    varname: str
        name of the simulation variable
    data_source: DataSource
        data source object that describe the source file name and format (see
        description of DataSource class [yet to be added])
    data_cloud: DataCloud
        a container to hold data of the variable object. (see description of 
        DataCloud class [yet to be added])
    data_obtained: bool
        a flag describing whether or not data of the variable has been read in
    (attributes of the current class)
    basin_cell_list: list of integer, list of those list (perferred), or mixed
        cell numbers of all cell within each basin. each list element represents
        one basin. However, in only integer is given as element (but not an 
        array or list), the element represent one cell (usually a basin outlet
        cell)
    spatial_scale, __spatial_scale: str
        describe the spatial scale to be considered for the cells present in 
        basin_cell_list. the domain of the attribute is {'cell', 'basin', 
        'mixed'}
    group_stats: bool
        the flag indicates whether or not data aggregation necessary. in 
        general, data aggregation is always done (as a default) for basins.
        if the spatial scale is not basin, this attribute will be set to false
    cell_area_as_weight, __cell_area_as_weight: bool
        the flag describe whether or not the cell area has to be used for 
        weighting the cell values during basin level aggregation. if the weights
        in the cell_weights are not provided and the cell_area_as_weight flag
        is set true, the area of each cell has to be computed and the cell
        areas of the corresponds cells in basin_cell_list should be stored in
        cell_weights variable
    compute_anomaly: bool
        a flag determines whether the anomalies would be computed or not
    __reference_period_for_mean: tuple of integer
        a tuple of start and end year of reference period for computing means
        while anomaly computation is done 
    conversion_factor, __conversion_factor: float
        conversion factor. conversion factor will be applied before the data has
        been aggregated and anomalies have been computed (when applicable).
    
    (attribute to be removed in the future)
    basin_outlets_only, __basin_outlets_only: bool
        a flag that describe whether the cellnumbers in the cell list represent
        basin outlets or basin cells
    boo_consider_super_basins, __boo_consider_super_basins: bool
        when the 'basin outlet only' (boo) flag is turned on, this flag 
        indicates that entire super basin i.e., all upstream area (from the 
        most downstream cell ?!!) should be considered
    
    (internal attributes)
    __optionnames: dict
        names and their alternatives in the configuration file to describe a 
        simulation variable objects 
    __has_aggregated: bool
        the flag describes whether or not the aggregation step been completed
    __has_anomaly_computed: bool
        the flag describes if the anomaly has already been computed or not
    __has_conversion_applied: bool
        the flag indicates whether the conversion factor has already been 
        applied or not
    __allow_insertion_of_cellnum_list: bool
        A flag that determines whether insertion of basin extent (or extent of 
        an unit) as list of cell numbers is possible at a later stage or not. If
        cell list is provided in the configuration file either as list of 
        numbers or through an external file, modification of basin cell list at
        later stage is prihibitted by setting the flag 'false'
    
    Methods:
    is_okay()
        Checks consistency and integrity of the objects and its components.

    
    """

    __optionnames = {
        'varname': (
            'var_name', 'varname', 'var name', 'variable_name', 
            'variable name'
        ),
        'filename': (
            'filename', 'data_file', 'data file', 
            'data config_filename'
        ),
        'temporal_resolution': (
            'temporal_resolution', 'value_type', 'value type', 'data_type', 
            'data type', 'prediction_type', 'prediction_type'
        ),
        'spatial_aggregation': (
            'spatial_aggregation', 'spatial aggregation', 'zonal_average', 
            'zonal average', 'zone flag',  'zone_flag', 'group stats', 
            'group_stats', 'aggregation'
        ),
        'cellnums': (
            'target_grid_cells', 'target_cells', 'target cells', 
            'target grid cells'
        ),
        'compute_anomaly': (
            'anomaly_computation', 'compute anomalies', 'compute anomaly' , 
            'anomaly', 'anomalies', 'calculate anomalies', 'calculate anomaly',
            'compute_anomaly'
        ),
        'weights': ('weights', 'cell weights', 'cell_weights'),
        'area_as_weight': (
            'area_as_weight', 'cell_area_as_weight', 'use cell areas for weights'
        ),
        'basin_outlets_only': (
            'basin_outlets_only', 'basin outlets only', 'basin_outlet_only', 
            'basin outlet only'
        ),
        'spatial_scale': ('spatial_scale', 'scale'),
        'conversion_factor': (
            'conversion_factor', 'conversion factor', 'unit conversion factor',
            'unit_conversion_factor'
        ),
        'reference_period': (
            'reference_period', 'reference period', 'reference period for mean',
            'reference_period_for_mean'
        ),
        
    }

    def __init__(self):
        Variable.__init__(self)
        self.data_source.file_type = FileType.wghm_binary
        self.__basin_outlets_only = False
        # self.__boo_consider_super_basins = False     # only if basin_outlets_only flag is true

        # spatial scale: cell, basin, mixed (or empty)
        self.__spatial_scale = ''
        self.basin_cell_list = []           # two-dimensional array
        self.group_stats = False
        self.compute_anomaly = False
        self.__reference_period_for_mean = ()
        self.__cell_area_as_weight = False
        self.cell_weights = []              # two-dimensional array

        self.__has_aggregated = False
        self.__has_anomaly_computed = False

        self.__conversion_factor = 1
        self.__has_conversion_applied = True

        self.__allow_insertion_of_cellnum_list = True
        
    @property
    def conversion_factor(self): return self.__conversion_factor
    @conversion_factor.setter
    def conversion_factor(self, factor): self.__conversion_factor = factor

    @property
    def cell_area_as_weight(self): return self.__cell_area_as_weight
    @cell_area_as_weight.setter
    def cell_area_as_weight(self, flag:bool): self.__cell_area_as_weight = flag

    @property
    def basin_outlets_only(self): return self.__basin_outlets_only
    @basin_outlets_only.setter
    def basin_outlets_only(self, flag:bool): self.__basin_outlets_only = flag

    # @property
    # def boo_consider_super_basins(self): return self.__boo_consider_super_basins
    # @boo_consider_super_basins.setter
    # def boo_consider_super_basins(self, flag:bool): self.__boo_consider_super_basins = flag

    @property
    def spatial_scale(self): return self.__spatial_scale
    @spatial_scale.setter
    def spatial_scale(self, value):
        if value in ['cell', 'basin', 'mixed']: self.__spatial_scale = value
        else: self.__spatial_scale = ''

    def add_unit_extent_cellnums(self, list_of_cellnums):
        """
        The function adds (appends) cell numbers of the extent of an unit (e.g.,
        of a basin, CDA unit, or even a single cell) to the list of basin cell
        numbers. allowed only if the falg __allow_insertion_of_cellnum_list is 
        set true.
        
        Parameters:
        list_of_cellnums: list (preferrably) or integer
            a list of cell numbers that define an unit. cell numbers must be
            according to the WaterGAP GCRC numbers. A single integer number 
            might be passed to indicate the unit to be a single-cell unit.
        """
        
        if self.__allow_insertion_of_cellnum_list:
            self.basin_cell_list.append(list_of_cellnums)

    def is_okay(self):
        if not Variable.is_okay(self): return False

        # step: validity check of basin cell list
        if self.basin_cell_list:
            nunits = len(self.basin_cell_list)
            for i in range(nunits):
                if not (type(self.basin_cell_list[i]) is list or
                    type(self.basin_cell_list[i]) is np.ndarray): return False

                for j in range(len(self.basin_cell_list[i])):
                    if type(self.basin_cell_list[i][j]) is not int: return False
        # end [step]

        if self.__spatial_scale == 'cell': self.group_stats = False

        # step: validity check of aggregation options
        if self.group_stats:
            if not self.basin_cell_list: return False

            if self.cell_weights:
                nunits = len(self.basin_cell_list)
                if len(self.cell_weights) != nunits: return False

                for i in range(nunits):
                    if len(self.cell_weights[i]) != len(self.basin_cell_list[i]):
                        return False
        # end [step]

        return True

    # def compute_anomalies(self):
    #     if self.compute_anomaly: 
    #         self.data_cloud.data = stats.compute_anomalies(self.data_cloud.data)

    @staticmethod
    def read_variables(lines):
        variables = []

        options = SimVariable.__optionnames
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
                            if key in options['varname']: var.varname = value
                            elif key in options['filename']: 
                                var.data_source.filename = value
                            elif key in options['temporal_resolution']:
                                value = value.lower()
                                if value in ['monthly', 'month']: 
                                    var.data_source.prediction_type \
                                    = PredictionType.monthly
                                elif value in ['yearly', 'annual', 'year']: 
                                    var.data_source.prediction_type \
                                    = PredictionType.yearly
                                elif value in ['daily', 'day']: 
                                    var.data_source.prediction_type \
                                    = PredictionType.daily
                            elif key in options['spatial_aggregation']:
                                value = value.lower()
                                if value in ['yes', 'y', '1', 'true', 't']: 
                                    var.group_stats = True
                                else: var.group_stats = False
                            elif key in options['cellnums']:
                                if value.find(':') > 0:
                                    temp = value.split(':')
                                    for i in range(len(temp)): 
                                        temp[i] = temp[i].strip()

                                    if (len(temp) == 2 and 
                                        temp[0].lower() == 'filename'):
                                        filename, temp_str = temp[1], ''

                                        fs = None
                                        try:
                                            fs = open(filename, 'r')
                                            for l in fs.readlines(): 
                                                temp_str += l
                                        except: temp_str = None
                                        finally:
                                            try: fs.close()
                                            except: pass
                                        
                                        if temp_str:
                                            var.basin_cell_list \
                                            = SimVariable.read_groups(
                                                temp_str, type='int'
                                            )
                                            temp_str = None
                                else: 
                                    var.basin_cell_list \
                                    = SimVariable.read_groups(value, type='int')
                                
                                if len(var.basin_cell_list) > 0:
                                    var.__allow_insertion_of_cellnum_list = \
                                    False

                            elif key in options['compute_anomaly']:
                                value = value.lower()
                                if value in ['yes', 'y', '1', 'true', 't']: 
                                    var.compute_anomaly = True
                                else: var.compute_anomaly = False
                            
                            elif key in options['reference_period']:
                                temp = value.strip('()').split(',')
                                for i in reversed(range(len(temp))):
                                    try: temp[i] = int(temp[i])
                                    except: _ = temp.pop(i)
                                
                                if len(temp) == 0:
                                    temp = value.strip('()').split('-')
                                    for i in reversed(range(len(temp))):
                                        try: temp[i] = int(temp[i])
                                        except: _ = temp.pop(i)
                                        
                                if len(temp) == 2: 
                                    var.__reference_period_for_mean \
                                    = tuple(temp)

                            elif key in options['weights']:
                                if value.find(':') > 0:
                                    temp = value.split(':')
                                    for i in range(len(temp)):
                                        temp[i] = temp[i].strip()
                                    
                                    if (len(temp) ==2 and 
                                        temp[0].lower() == 'filename'):
                                        filename, temp_str = temp[1], ''

                                        fs = None
                                        try:
                                            fs = open(filename, 'r')
                                            for l in fs.readlines(): 
                                                temp_str += l
                                        except: temp_str = None
                                        finally:
                                            try: fs.close()
                                            except: pass

                                        if temp_str:
                                            var.cell_weights \
                                            = SimVariable.read_groups(temp_str)
                                            temp_str = None
                                else: 
                                    var.cell_weights \
                                    = SimVariable.read_groups(value)

                            elif key in options['area_as_weight']:
                                value = value.lower()
                                if value in ['yes', 'y', '1', 'true', 't']: 
                                    var.cell_area_as_weight = True
                                else: var.cell_area_as_weight = False
                            elif key in options['basin_outlets_only']:
                                value = value.lower()
                                if value in ['yes', 'y', '1', 'true', 't']: 
                                    var.basin_outlets_only = True
                                else: var.basin_outlets_only = False
                            # elif key in ['consider_super_basins', 'consider super basins']:
                            #     # NB: this option will only be used when basin_outlets_only flag is set true
                            #     value = value.lower()
                            #     if value in ['yes', 'y', '1', 'true', 't']: 
                            #         var.boo_consider_super_basins = True
                            #     else: var.boo_consider_super_basins = False
                            elif key in options['spatial_scale']:
                                var.spatial_scale = value.lower()
                            elif key in options['conversion_factor']:
                                try: 
                                    var.conversion_factor = float(value)
                                    var.__has_conversion_applied = False
                                except: pass

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
    def data_collection_asof_20181115(sim_vars, start_year, end_year):
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
                                year_dt = WaterGapIO.read_unf(file_name, file_endian=ds.file_endian)

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

                                                        summary = WaterGapIO.summarize(year_dt, basin=basin, weights=weights)

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
                                                    summary = WaterGapIO.summarize(year_dt)
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

    def data_collection(self, start_year, end_year, prediction_directory=''):
        '''
        This function reads model predictions, processes predictions as required and stores the processed data into
        the data container (data cloud) of the variable instance.

        :param start_year: (int) start year of prediction
        :param end_year:  (int) end year of prediction
        :param prediction_directory: (string) directory path for prediction output files
        :return: (bool) True on success,
                        False otherwise
        '''
        succeed = True

        if self.data_source.file_type == FileType.wghm_binary:
            if self.data_source.prediction_type == PredictionType.monthly:
                # try:
                    filename = self.data_source.filename
                    file_endian = self.data_source.file_endian

                    ndx = filename.lower().find('[year]')
                    for year in range(start_year, end_year + 1):
                        # step: read predictions
                        file_name = filename[:ndx] + str(year) + filename[ndx + 6:]
                        if prediction_directory: file_name = os.path.join(prediction_directory, file_name)

                        data = WaterGapIO.read_unf(file_name, file_endian=file_endian)

                        if not type(data) is np.ndarray: return False

                        # step: if group statistics to be calculated, process data for each basin
                        if self.group_stats and not self.basin_outlets_only:
                            if not self.basin_cell_list: return False

                            # step: crop data for each basin
                            for i in range(len(self.basin_cell_list)):
                                basin_id = i + 1
                                basin = np.array(self.basin_cell_list[i])
                                basin_data = data[basin-1]                                # notice -1 is used to convert 1-based
                                                                                    # indexing to 0-based indexing

                                # step: apply weights if application and compute aggregate values
                                if self.cell_weights:
                                    weights = np.array(self.cell_weights[i])
                                    if basin_data.ndim == 1: basin_data = basin_data * weights
                                    else: basin_data = basin_data * weights[:, None]

                                    basin_data = np.sum(basin_data, axis=0) / np.sum(weights)
                                else: basin_data = np.sum(basin_data, axis=0)

                                # step: create indices for data
                                basin_ndx = np.array([basin_id] * 12).reshape(12, 1)
                                year_ndx = np.array([year] * 12).reshape(12, 1)
                                month_ndx = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]).reshape(12, 1)
                                data_ndx = np.concatenate((basin_ndx, year_ndx, month_ndx), axis=1).tolist()

                                # step: store data and indices into data cloud object
                                self.data_cloud.data_indices += data_ndx
                                self.data_cloud.data += basin_data.flatten().tolist()
                        else:
                            cell_list = []

                            if self.basin_outlets_only:
                                # calculate discharges for outlets (explanation needed!!!!)
                                d = []
                                for outlets in self.basin_cell_list:
                                    outlets = np.array(outlets) - 1
                                    temp = data[outlets]

                                    for i in range(1, len(temp)): temp[0] -= temp[i]
                                    d.append(temp[0])
                                data = np.array(d)
                            else:
                                # step: generate cell list
                                for group in self.basin_cell_list: cell_list += group

                                # step: crop data if cell_list is not empty
                                if cell_list:  data = data[np.array(cell_list)-1]       # notice -1 is used to convert 1-based
                                                                                        # indexing to 0-based indexing

                            # step: create indices for data
                            ncells = data.shape[0]
                            if not cell_list: cell_list = list(range(1, ncells +1))

                            cell_ndx = []
                            for cid in cell_list: cell_ndx += [cid] * 12

                            nrow = ncells * 12
                            cell_ndx = np.array(cell_ndx).reshape(nrow, 1)
                            year_ndx = np.array([year] * nrow).reshape(nrow, 1)
                            month_ndx = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] * ncells).reshape(nrow, 1)

                            data_ndx = np.concatenate((cell_ndx, year_ndx, month_ndx), axis=1).tolist()

                            # step: store data and indices  in data cloud
                            self.data_cloud.data_indices += data_ndx
                            self.data_cloud.data += data.flatten().tolist()
                # except: succeed = False
            elif self.data_source.prediction_type == PredictionType.daily: # yet to be implemented
                succeed = False
            elif self.data_source.prediction_type == PredictionType.yearly: # yet to be implemented
                succeed = False
            else: succeed = False
        else: # yet to be implemented
            succeed = False

        return succeed

    def dump_time_series_from_model_prediction(
            self,
            start_year,
            end_year,
            additional_attributes=[],
            dumping_directory='',
            prediction_directory='',
            prefix_filename='',
            use_lock=False):
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
        :param additional_attributes: (list of numbers; optional) additional attributes to be dumped
        :param dumping_directory: (string; optional) path where data to be dumped
        :param prediction_directory: (string; optional) path of model output directory
        :param prefix_filename: (string; optional; default = '') prefix/postfix of output filename
        :return: (bool) True on success,
                        False Otherwise
        '''

        # step: check presence of target cells
        ncell = 0
        for group in self.basin_cell_list: ncell += len(group)
        if ncell == 0: return False

        # step: check if data source object is okay
        if not self.data_source.is_okay(): return False
        if not self.data_source.file_type == FileType.wghm_binary: return False

        # step: form data format string
        format_str = 'f'
        if self.data_source.file_endian == FileEndian.little_endian: format_str = '<%s'%format_str
        else: format_str = '>%s'%format_str

        succeed = True
        if self.data_source.prediction_type == PredictionType.monthly:
            prediction_filename = self.data_source.filename
            ndx = prediction_filename.lower().find('[year]')

            # step: for each year from start year to end year read model predictions
            for year in range(start_year, end_year + 1):
                file_name = prediction_filename[:ndx] + str(year) + prediction_filename[ndx + 6:]
                if prediction_directory: file_name = os.path.join(prediction_directory, file_name)

                pred = WaterGapIO.read_unf(file_name, file_endian=self.data_source.file_endian)
                if not type(pred) is np.ndarray or len(pred) == 0: return False

                if self.group_stats and not self.basin_outlets_only:
                    # step: for each basin collect values for each cell and aggregate data
                    for i in range(len(self.basin_cell_list)):
                        basin_id = i + 1
                        basin = np.array(self.basin_cell_list[i]) - 1     # reducing the cell number by 1 is necessary,
                                                                    # because cell numbers have a 1-based indexing
                        data = pred[basin]

                        if self.cell_weights:
                            weights = np.array(self.cell_weights[i])
                            if data.ndim == 1: data = data * weights
                            else: data = data * weights[:, None]

                            data = np.sum(data, axis=0) / np.sum(weights)
                        else: data = np.sum(data, axis=0)

                        # step: append additing attributes and time data (time info i.e., year, month, day etc.)
                        additional_cols = additional_attributes + [basin_id, year]
                        if data.ndim == 1: data = np.append(additional_cols, data)
                        else:
                            ncol = len(additional_cols)
                            nrow = data.shape[0]
                            additional_cols = np.array(additional_cols * nrow).reshape(nrow, ncol)
                            data = np.concatenate((additional_cols, data), axis=1)

                        # step: dump data into file
                        if data.ndim == 1: ncol = data.size
                        else: ncol = data.shape[1]

                        if prefix_filename:
                            dump_filename = self.varname + '.%s.%d.unf0' % (prefix_filename, ncol)
                        else: dump_filename = self.varname + '.%d.unf0' % ncol

                        if dumping_directory: dump_filename = os.path.join(dumping_directory, dump_filename)

                        if use_lock:
                            if prefix_filename:
                                lock_file = '_%s.%s.LOCK' % (self.varname.upper(), prefix_filename)
                            else: lock_file = '_%s.LOCK' % self.varname.upper()
                        else: lock_file = ''

                        succeed = self.dump_data_into_file(dump_filename, data.astype(format_str), lock_file)

                        if not succeed: break
                else:
                    if self.basin_outlets_only:
                        # step: gather outlet discharges and compute actual discharge (i.e., deduct sub-basin discharges)
                        data = []
                        for outlets in self.basin_cell_list:
                            outlets = np.array(outlets) - 1
                            temp = pred[outlets]

                            # if a basin has sub-basins in the upstream, river
                            # discharge of the upstream sub-basin will be
                            # deducted from the discharge of the outlet cell
                            # of the current basin
                            for i in range(1, len(temp)): temp[0] -= temp[i] 

                            data.append(temp[0])
                        data = np.array(data)

                        # step: append additional attributes and time info to data
                        nrow = len(self.basin_cell_list)
                        time_info = np.array([year] * nrow).reshape(nrow, 1)
                        basin_ids = np.arange(1, nrow+1, dtype=np.int32).reshape(nrow, 1)
                        data = np.concatenate((basin_ids, time_info, data), axis=1)

                        if additional_attributes:
                            ncol = len(additional_attributes)
                            additional_cols = np.array(additional_attributes * nrow).reshape(nrow, ncol)
                            data = np.concatenate((additional_cols, data), axis=1)

                    else:
                        # step: gather cell numbers in all basins and crop data for those cells
                        cells = []
                        for group in self.basin_cell_list: cells += group
                        cells = np.array(cells)
                        data = pred[cells-1]

                        # step: append additional attributes and time info into the data
                        nrow = len(cells)
                        time_info = np.array([year] * nrow).reshape(nrow, 1)
                        cells = cells.reshape(nrow, 1)
                        data = np.concatenate((cells, time_info, data), axis=1)

                        if additional_attributes:
                            ncol = len(additional_attributes)
                            additional_cols = np.array(additional_attributes * nrow).reshape(nrow, ncol)
                            data = np.concatenate((additional_cols, data), axis=1)

                    # step: dump data into file
                    if data.ndim == 1: ncol = data.size
                    else: ncol = data.shape[1]

                    if prefix_filename:
                        dump_filename = self.varname + '.%s.%d.unf0' % (prefix_filename, ncol)
                    else: dump_filename = self.varname + '.%d.unf0' % ncol
                    if dumping_directory: dump_filename = os.path.join(dumping_directory, dump_filename)

                    if use_lock:
                        if prefix_filename:
                            lock_file = '_%s.%s.LOCK'% (self.varname.upper(), prefix_filename)
                        else: lock_file = '_%s.LOCK'% self.varname.upper()
                    else: lock_file = ''

                    succeed = self.dump_data_into_file(dump_filename, data.astype(format_str), lock_file)

                if not succeed: break

        return succeed

    def dump_data_into_file(self, filename, data_bytes, lock_name):
        '''
        This function dumps data into specified file in binary (4-byte float) format. Lock will be used to avoid
        conflicts in case of parallel runs, if lock name is provided.

        Parameters:
        :param filename: (string) name of the file
        :param data: (bytes) binary data (as bytes) to be dumped into file
        :param lock_name: (string) name of lockfile. Lock will only be applied if provided
        :return: (bool) True on success,
                        False otherwise
        '''
        succeed = True

        f = None
        if lock_name:
            fd = open(lock_name, 'w')
            sleep_time = round(np.random.uniform(0.1, 0.3), 3)
            if io.acquire_lock(fd, sleep_time=sleep_time):
                try:
                    f = open(filename, 'ab')
                    f.write(data_bytes)
                except: succeed = False
                finally:
                    try: f.close()
                    except: pass
                    io.release_lock(fd)
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

    def cell_level_predicted_time_series(
        self,
        start_year,
        end_year,
        prediction_directory
    ):
        '''
        This function will read model predictions and transform cell-level
        prediction time-series. As convention no aggregation will be preformed.

        Parameters:
        :param start_year: (int) start year of prediction
        :param end_year: (int) end year of prediction
        :param prediction_directory: (string) path of model output
                                                        directory
        :return: (np.ndarray) cell-level time-series

        Notes:
            dimension of output dataset = nrow x ncol;
            where, nrow = number of months and
                   ncol = id columns (cell number, year, month) + number of cell
        '''

        # step-01: validate inputs
        if start_year < 1901 or end_year > 2019: return False
        if not os.path.exists(prediction_directory): return False

        if start_year > end_year: end_year = start_year
        # end [step-01]

        # step-02: gather all cell numbers into one single list
        cell_list = []
        for basin_cells in self.basin_cell_list: cell_list += basin_cells
        if len(cell_list) == 0: return False

        cell_list = np.array(cell_list, dtype=int)
        ii_cell = cell_list - 1      # 0-based cell indices
        # end [step-02]

        # step-03: validate data-source object of current variable
        if not self.data_source.is_okay(): return False
        if not self.data_source.file_type == FileType.wghm_binary: return False
        # end [step-03]

        # step-04: read monthly prediction output
        d_out = np.empty(0)
        for year in range(start_year, end_year + 1):
            # step-4.1: generate prediction filename
            ndx = self.data_source.filename.lower().find('[year]')
            filename_in = os.path.join(
                prediction_directory,
                self.data_source.filename[:ndx] + str(year) +
                self.data_source.filename[ndx + 6:]
            )
            # end [step-4.1]

            # step-4.2: read prediction from UNF file
            d_pred =  WaterGapIO.read_unf(
                filename_in,
                file_endian=self.data_source.file_endian
            )

            if not type(d_pred) is np.ndarray or len(d_pred) == 0:
                return False
            # end [step-4.2]

            # step-4.3: identify cell-level predictions and store then into
            # output dataset
            try: d_out = np.concatenate((d_out, d_pred[ii_cell].T), axis=0)
            except: d_out = d_pred[ii_cell].T
            # end [step-4.3]
        # end [step-04]

        # step-05: add data indices and store predictions into data cloud
        indices = np.empty(0)
        if self.data_source.prediction_type == PredictionType.monthly:
            if d_out.shape != ((end_year - start_year + 1) * 12, cell_list.size):
                return False
        
            yy = np.repeat(np.arange(start_year, end_year + 1), 12).reshape(-1, 1)
            mm = np.repeat(np.arange(1, 12 + 1)[np.newaxis, :],
                            (end_year - start_year + 1), axis=0).reshape(-1, 1)
            indices = np.concatenate((yy, mm), axis=1)

        elif self.data_source.prediction_type == PredictionType.daily:
            if d_out.shape != ((end_year - start_year + 1) * 365, cell_list.size):
                return False
            
            yy = np.repeat(np.arange(start_year, end_year + 1), 365).reshape(-1, 1)
            dd = np.repeat(np.arange(1, 365 + 1)[np.newaxis, :],
                            (end_year - start_year + 1), axis=0).reshape(-1, 1)
            indices = np.concatenate((yy, dd), axis=1)
        else: return False

        self.data_cloud.data_indices = indices
        self.data_cloud.data = d_out

        # set data manipulation flags to their defaults
        self.__has_aggregated = False
        self.__has_anomaly_computed = False
        # end [step-05]

        return True

    def aggregate_prediction_at_spatial_scale(self):
        if self.__basin_outlets_only: return True
        if not self.group_stats: return True
        if self.__has_aggregated: return True

        # step: convert data and indices into np.ndarray
        self.data_cloud.data = np.array(self.data_cloud.data)
        self.data_cloud.data_indices = np.array(self.data_cloud.data_indices)
        # end [step]

        nunits = len(self.basin_cell_list)   # no. of units or basins
        start_index, end_index = 0, 0

        d_out = np.empty(0)
        for i in range(nunits):
            end_index += len(self.basin_cell_list[i])
            d = self.data_cloud.data[:, start_index:end_index]
            if d.ndim == 1: d = d[:, None]

            weights = np.empty(0)
            if self.cell_weights:
                weights = np.array(self.cell_weights[i])
                d = (d * weights[None,:]).sum(axis=1) / weights.sum()
            else: d = d.sum(axis=1)

            try: d_out = np.concatenate((d_out, d[:, None]), axis=1)
            except: d_out = d[:, None]

            start_index = end_index

        if d_out.shape[1] != nunits: return False
        else:
            self.data_cloud.data = d_out
            self.__has_aggregated = True

        return True

    def do_anomaly_computation(self):
        if self.compute_anomaly and not self.__has_anomaly_computed:
            self.data_cloud.data = np.array(self.data_cloud.data)
            
            if len(self.__reference_period_for_mean) == 2:
                start_year, end_year = self.__reference_period_for_mean
                x = self.data_cloud.data_indices[:,0]
                ii = (x>=start_year)&(x<=end_year)

                reference_means = self.data_cloud.data[ii].mean(
                                                        axis=0).reshape(1,-1)
                self.data_cloud.data -= reference_means
            else:    
                self.data_cloud.data -= self.data_cloud.data.mean(
                                                        axis=0).reshape(1, -1)
            self.__has_anomaly_computed = True

        return True

    def apply_conversion_factor(self):
        if (self.conversion_factor != 1 and not self.__has_conversion_applied):
            self.data_cloud.data *= self.conversion_factor
            self.__has_conversion_applied = True

    def dump_data_into_binary_file(
            self,
            directory_out,
            additional_filename_identifier='',
            additional_attributes=[]
        ):
        if (len(self.data_cloud.data) > 0 and
            len(self.data_cloud.data) == len(self.data_cloud.data_indices)):

            dd = np.array(self.data_cloud.data)
            ii = np.array(self.data_cloud.data_indices)
            d_out = np.concatenate((ii, dd), axis=1)

            if additional_attributes:
                attribs = np.array(additional_attributes)
                attribs = np.repeat(attribs[None,:], d_out.shape[0], axis=0)

                d_out = np.concatenate((attribs, d_out), axis=1)

            if additional_filename_identifier:
                f_out = '%s_%s.%d.unf0' % (self.varname.lower(),
                                           additional_filename_identifier,
                                           d_out.shape[1])
            else: f_out = '%s.%d.unf0' % (self.varname.lower(), d_out.shape[1])
            f_out = os.path.join(directory_out, f_out)

            return WaterGapIO.write_unf(filename=f_out, data=d_out, append=True)

        return False

class DerivedVariable(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.data_source = None
        self.equation = ''
        self.equ_evaluated = False
        self.compute_anomaly = False
        self.__reference_period_for_mean = ()
        self.__has_anomaly_computed = False

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
        succeed = self.evaluate_equation(simvars, obsvars)

        if succeed:
            temp = self.equation.split('+')
            for i in range(len(temp)): temp[i] = temp[i].strip()

            try:
                
                cloud1 = self.find_variable(temp[0], simvars, obsvars).data_cloud

                for i in range(1, len(temp)):
                    cloud2 = self.find_variable(temp[i], simvars, obsvars).data_cloud
                    cloud1 = DataCloud.arithmetic_operation(cloud1, cloud2, func='+')
                    
            except: succeed = False

            if succeed: self.data_cloud = cloud1

        return succeed

    # def compute_anomalies(self):
    #     if self.compute_anomaly: 
    #         self.data_cloud.data -= self.data_cloud.data.mean()

    def do_anomaly_computation(self):
        if self.compute_anomaly and not self.__has_anomaly_computed:
            self.data_cloud.data = np.array(self.data_cloud.data)
            
            if len(self.__reference_period_for_mean) == 2:
                start_year, end_year = self.__reference_period_for_mean
                x = self.data_cloud.data_indices[:,0]
                ii = (x>=start_year)&(x<=end_year)

                reference_means = self.data_cloud.data[ii].mean(
                                                        axis=0).reshape(1,-1)
                self.data_cloud.data -= reference_means
            else:
                self.data_cloud.data -= self.data_cloud.data.mean(
                                                        axis=0).reshape(1, -1)

            self.__has_anomaly_computed = True
    
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
                            elif key in [
                                'reference_period', 'reference period', 
                                'reference period for mean',
                                'reference_period_for_mean'
                            ]:
                                temp = value.strip('()').split(',')
                                for i in reversed(range(len(temp))):
                                    try: temp[i] = int(temp[i])
                                    except: _ = temp.pop(i)
                                
                                if len(temp) == 0:
                                    temp = value.strip('()').split('-')
                                    for i in reversed(range(len(temp))):
                                        try: temp[i] = int(temp[i])
                                        except: _ = temp.pop(i)

                                if len(temp) == 2: 
                                    var.__reference_period_for_mean \
                                    = tuple(temp)
                            
            except: return None
