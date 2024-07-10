__author__ = 'mhasan'

import sys, pandas as pd
# from utilities.fileio import FileInputOutput as io

class Parameter:
    """
    Class to represent the Parameter objects.

    Attributes:
    parameter_name: str
        the name of the parameter (as used in the json parameter file)
    lower_bound: float
        the lower limit of the parameter
    upper_bound: float
        the upper limit of the parameter
    parameter_value: float (or list of floats)
        current value of the parameter. if the attribute contains a float 
        value, the single value is applied to all cells mentioned in the 
        cell_list variable or to all cells of the globe when cell_list is
        empty. If however parameter_value contains list of float, each value
        of the list corresponds to the value of respective cells in the 
        cell_list, either a single cell or a group of cells.
    logarithmic_scale: bool
        determines whether the value of the parameter is in 10-based log scale.
        if the attribute is set true, a transformation of the parameter value
        has to be performed before assigne the value to a cell
    cell_list: list of integers
        the cell numbers of the WaterGAP model cell. The numbers are according
        to the GCRC numbers. If the cell_list container is empty, the parameter
        value is applied to all global cells. If the cell_list contains, lists
        of cell numbers of many basins and if parameter_value contains list of 
        values, for each basin the parameter value will be mapped from the 
        parameter_value list. The cell_list may also contain only cell numbers,
        instead of list of cell number, to represent the cells and if the 
        parameter_value has the same length as of the length of cell_list,
        cell specific value has to be assigned.
    cell_level_representation: bool
        the flag, if true, indicates that cell level value should be enforced in 
        especially calibration experiments. in case of cell level calibration,
        the number of actual parameters would depend on the number of grid cells
        listed in the cell_list array. this option should only be used in single
        problem calibration.
    precision_level: integer
        represents the level of precision i.e., how many significant digits
        should be consided after the decimal point.

    single_value_flag: bool (will be deprecated soon)
        indicate if the parameter value to be applied for all cells globally
       
        
    Methods:
    is_okay()
        Checks consistencies of the Parameter object. If a parameter has a 
        name and a proper domain, the object will pass the consistency check.
    
    Remarks: the documentation style followed from 
    https://realpython.com/documenting-python-code/
    """
    def __init__(self, pname='', lbound=None, ubound=None):
        self.parameter_name = pname
        self.lower_bound = lbound
        self.upper_bound = ubound
        self.parameter_value = -9999
        self.logarithmic_scale = False

        self.cell_list = []
        self.single_value_flag = True
        self.precision_level = -1
        self.cell_level_representation = False

    def is_okey(self):
        if not self.parameter_name: return False
        elif self.upper_bound <= self.lower_bound: return False
        else: return True

    def set_parameter_name(self, param_name): self.parameter_name = param_name
    def set_lower_bound(self, bound): self.lower_bound = bound
    def set_upper_bount(self, bound): self.upper_bound = bound
    def set_parameter_value(self, value): 
        if self.precision_level > 0:
            self.parameter_value = round(value, self.precision_level)

    def get_parameter_name(self): return self.parameter_name
    def get_lower_bound(self): return self.lower_bound
    def get_upper_bound(self): return self.upper_bound

    def get_unit_count(self, basin_no=-1):
        """
        finds the number of units that the parameter object represents. the 
        function is particularly useful for cell-level calibration when the cell 
        level representation flag is set true 

        Parameter:
        basin_no: int (optional)
            if provided, number of represented units for the concerned basin is
            returned by the function. this parameter can potentially be used in
            the case of multi-problem configurations
            Caution: the basin_no might be different from problem-no as the same
            parameter might not have influential effect in all the basins!

        Returns:
        int
            No. of unit represented by the parameter object
        """
        
        if self.cell_level_representation:
            if basin_no == -1:
                count = 0
                for l in self.cell_list:
                    if type(l) is list: count += len(l)
                    else: count += 1
                return count
            else:
                l = self.cell_list[basin_no]
                if type(l) is list:
                    return len(l)
                else: return 1
        else: return 1


    def get_parameter_value(self):
        if not self.logarithmic_scale:
            if self.precision_level > 0:
                if type(self.parameter_value) is list:
                    temp = []
                    for v in self.parameter_value:
                        temp.append(round(v, self.precision_level))
                    return temp
                else:
                    return round(self.parameter_value, self.precision_level)
            else: return self.parameter_value
        else:
            if self.precision_level > 0:
                if type(self.parameter_value) is list:
                    temp = []
                    for v in self.parameter_value: 
                        temp.append(round(10**v, self.precision_level))
                    return temp
                else:
                    return round(10**self.parameter_value, self.precision_level)
            else: 
                if type(self.parameter_value) is list:
                    temp = []
                    for v in self.parameter_value:
                        temp.append(10**v)
                    return temp
                else:
                    return 10**self.parameter_value

    def set_cell_list(self, cell_list): self.cell_list = cell_list
    def set_single_value_flag(self, flag): self.single_value_flag = flag
    def set_precision_level(self, level): self.precision_level = level
    def get_cell_list(self): return self.cell_list
    def get_single_value_flag(self): return self.single_value_flag
    def get_precision_level(self): return self.precision_level

    def has_multiple_cells(self):
        if self.cell_list: return True
        else: return False

    def add_unit_parameter_value(self, value):
        """
        This function add (append) parameter value for a unit (e.g., a basin, 
        CDA unit, or a single cell) to the list of parameter values (i.e., 
        parameter_value). If the parameter_value is not a list, a new list will
        be assigned to parameter_value variable, and then new value will be 
        appended. This fuction is used only when parameter values for multiple
        units to be stored 

        Parameter:
        value: float
            parameter value for a unit 
        """
        try:
            self.parameter_value.append(value)
        except: self.parameter_value = [value]

    def add_unit_extent_cellnums(self, list_of_cellnums):
        """
        This function add (append) cell number list defining the extent of an
        unit (e.g., a basin, CDA unit, or even a single cell)

        Paramter:
        list_of_cellnum: list
            a list of cell numbers. The cell numbers should be according to the
            WaterGAP GCRC number system.
        """
        self.cell_list.append(list_of_cellnums)
    
    def clear_cellnumber_list(self):
        """
        The function clears the list of cell numbers that describes the extent 
        of all the units.
        """
        self.cell_list.clear()

    @staticmethod
    def read_parameter_list(filename):
        param_list = []

        df_param_info = pd.read_csv(filename)
        param_names = df_param_info['param_name'].values.flatten()
        lower_bounds = df_param_info['lower_bound'].values.flatten()
        upper_bounds = df_param_info['upper_bound'].values.flatten()

        for i in range(len(param_names)):
            p = Parameter(param_names[i], lower_bounds[i], upper_bounds[i])
            param_list.append(p)

        return param_list

    @staticmethod
    def read_parameters(lines):
        parameters = []

        param = None
        while lines:
            line = lines.pop(0).strip()
            if line:
                temp = line.strip().split()
                temp[0] = temp[0].strip().lower()
                if temp[0] == 'end': return parameters
                elif temp[0] == '@@':
                    if param: parameters.append(param)
                    param = None
                elif temp[0] == '@': param = Parameter()
                elif param:
                    temp = line.split('=')
                    for i in range(len(temp)): temp[i] = temp[i].strip()
                    if len(temp) == 2:
                        key, value = temp[0], temp[1]
                        if key in ['param_name', 'param name', 'name', 'parameter name', 'parameter_name']:
                            param.set_parameter_name(value)
                        elif key in ['upper_bound', 'ubound', 'upper bound']:
                            try: param.set_upper_bount(float(value))
                            except: param.set_upper_bount(None)
                        elif key in ['lower_bound', 'lbound', 'lower bound']:
                            try: param.set_lower_bound(float(value))
                            except: param.set_lower_bound(None)
                        elif key in ['target cells', 'target_cells', 'target_grid_cells', 'target grid cells',  'cell num',
                                     'cell_num', 'cell nums', 'cell_nums', 'cell list', 'cell_list', 'cell number', 'cell_number']:
                            if value.lower().find(':') > 0:
                                temp = value.split(':')
                                if len(temp) >= 2 and temp[0].strip().lower() == 'filename':
                                    filename = temp[1].strip()
                                    values = Parameter.values_from_file(filename)
                                    if values: param.set_cell_list(values)
                            else:
                                temp = value.split(',')
                                for i in reversed(range(len(temp))):
                                    try: temp[i] = int(temp[i].replace('[', '').replace(']','').strip())
                                    except: temp.pop(i)
                                if temp: param.set_cell_list(temp)
                        elif key in ['single_value_flag', 'single_value_for_all', 'single value flag']:
                            if value.lower() in ['n', 'no', 'false', 'f', '0']: param.set_single_value_flag(False)
                            else: param.set_single_value_flag(True)
                        elif key in ['precision', 'precision_level', 'precision level', 'level of precision',
                                     'parameter precision', 'parameter_precision']:
                            try: param.set_precision_level(int(value))
                            except: param.set_precision_level(4)
                        elif key in ['logarithmic_scale', 'logarithmic scale', 'log_scale', 'log scale']:
                            value = value.lower()
                            if value in ['y', 'yes', 'true', 't', '1']: param.logarithmic_scale = True
                            else: param.logarithmic_scale = False
        return []

    @staticmethod
    def values_from_file(filename, fun=int):
        values = []

        f = None
        try:
            line_txt = ''
            f = open(filename, 'r')
            for line in f.readlines(): line_txt += line
            temp = line_txt.split(']')

            for i in range(len(temp)):
                temp[i] = temp[i].strip().strip(',').strip().strip('[')
                if temp[i]:
                    group_items = temp[i].split(',')

                    for j in reversed(range(len(group_items))):
                        try: group_items[j] = fun(group_items[j])
                        except: group_items.pop(j)

                    if group_items: values.append(group_items)
        except: return []
        finally:
            try: f.close()
            except: pass

        return values
    
    def __write_description_into_file(self, file):
        succeed = True
        
        text_lines = []
        text_lines.append('@')

        keyword = 'parameter_name'
        value = self.parameter_name
        if not value: value = '[not provided]'
        text_lines.append('%s = %s'%(keyword, value))

        keyword = 'lower_bound'
        value = self.lower_bound
        text_lines.append('%s = %f'%(keyword, value))

        keyword = 'upper_bound'
        value = self.upper_bound
        text_lines.append('%s = %f'%(keyword, value))

        keyword = 'logarithmic_scale'
        value = self.logarithmic_scale
        if value: text_lines.append('%s = %s'%(keyword, 'true'))

        keyword = 'precision_level'
        value = self.precision_level
        if value > 0 : text_lines.append('%s = %d'%(keyword, value))

        text_lines.append('@@')

        try:
            _ = file.write('\n'.join(text_lines))
        except: succeed = False

        return succeed

    @staticmethod
    def write_parameter_description(parameter_list, file):
        succeed = True

        try: _ = file.write('BEGIN PARAMETER\n')
        except: succeed = False

        for param in parameter_list:
            succeed &= param.__write_description_into_file(file)

        try: _ = file.write('END PARAMETER\n')
        except: succeed &= False

        return succeed
