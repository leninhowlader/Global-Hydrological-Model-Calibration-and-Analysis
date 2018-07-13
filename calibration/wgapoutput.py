import sys, numpy as np, os
sys.path.append('..')
from calibration.enums import FileEndian
from utilities.fileio import read_binary_file

class WGapOutput:
    @staticmethod
    def read_unf(filename, file_endian=FileEndian.big_endian, ncol=0):
        if not os.path.exists(filename): return []

        unf_type = -1
        try: unf_type = int(filename[-1])
        except: pass

        if unf_type  not in [0, 1, 2, 4]: return []

        if not ncol > 0:
            temp = os.path.split(filename)[-1]
            if temp.count('.') >= 2:
                try:
                    ndx1 = temp.find('.') + 1
                    ndx2 = temp[ndx1:].find('.')
                    ncol = int(temp[ndx1:ndx1+ndx2])
                except: pass

            if not ncol > 0: return []

        format_str = ''
        if file_endian == FileEndian.big_endian: format_str += '>'
        elif file_endian == FileEndian.little_endian: format_str += '<'
        else: format_str += '@'

        if unf_type == 0:
            format_str += 'f' * ncol
            block_size = 4 * ncol
        elif unf_type == 1:
            format_str += 'b' * ncol
            block_size = 1 * ncol
        elif unf_type == 2:
            format_str += 'h' * ncol
            block_size = 2 * ncol
        else:
            format_str += 'i' * ncol
            block_size = 4 * ncol

        d = read_binary_file(filename, block_size, format_str)

        if ncol == 1:
            for i in range(len(d)): d[i] = d[i][0]

        return d

    @staticmethod
    def summarize(data, basin=[], weights=[]):
        if basin and weights and len(weights) != len(basin): return []

        data = np.array(data)

        if basin:
            basin = np.array(basin)-1
            data = data[basin]

        if weights:
            weights = np.array(weights)
            if data.ndim == 1: data = data * weights
            else: data = data * weights[:, None]

            data = np.sum(data, axis=0) / np.sum(weights)
        else: data = np.sum(data, axis=0)

        return data.tolist()