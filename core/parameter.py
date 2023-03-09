__author__ = 'mhasan'

import sys

from utilities.fileio import FileInputOutput as io

class Parameter:
    def __init__(self, pname='', lbound=None, ubound=None):
        self.parameter_name = pname
        self.lower_bound = lbound
        self.upper_bound = ubound
        self.parameter_value = -9999
        self.logarithmic_scale = False

        self.cell_list = []
        self.single_value_flag = True
        self.cell_specific_values = []
        self.precision_level = -1

    def is_okey(self):
        if not self.parameter_name: return False
        elif self.upper_bound <= self.lower_bound: return False
        else: return True

    def set_parameter_name(self, param_name): self.parameter_name = param_name
    def set_lower_bound(self, bound): self.lower_bound = bound
    def set_upper_bount(self, bound): self.upper_bound = bound
    def set_parameter_value(self, value): self.parameter_value = round(value, self.precision_level)
    def get_parameter_name(self): return self.parameter_name
    def get_lower_bound(self): return self.lower_bound
    def get_upper_bound(self): return self.upper_bound

    def get_parameter_value(self):
        if not self.logarithmic_scale:
            if self.precision_level > 0:
                return round(self.parameter_value, self.precision_level)
            else: return self.parameter_value
        else:
            if self.precision_level > 0:
                return round(10**self.parameter_value, self.precision_level)
            else: return 10**self.parameter_value

    def set_cell_list(self, cell_list): self.cell_list = cell_list
    def set_single_value_flag(self, flag): self.single_value_flag = flag
    def set_cell_specific_values(self, values): self.cell_specific_values = values
    def set_precision_level(self, level): self.precision_level = level
    def get_cell_list(self): return self.cell_list
    def get_single_value_flag(self): return self.single_value_flag
    def get_cell_specific_values(self): return self.cell_specific_values
    def get_precision_level(self): return self.precision_level

    def has_multiple_cells(self):
        if self.cell_list: return True
        else: return False


    @staticmethod
    def read_parameter_list(filename, separator=',', header=False, skip_lines=0):
        param_list = []

        headers, data = io.read_flat_file(filename, separator, header, skip_lines)

        if data:
            nndx, lndx, undx = 0, 1, 2
            for d in data:
                p = Parameter(d[nndx], d[lndx], [undx])
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
