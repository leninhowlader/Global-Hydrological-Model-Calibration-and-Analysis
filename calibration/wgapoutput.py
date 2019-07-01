import sys, numpy as np, os
sys.path.append('..')
from calibration.enums import FileEndian
from utilities.fileio import read_binary_file

class WGapOutput:
    @staticmethod
    def read_unf(filename, file_endian=FileEndian.big_endian, ncol=-1):
        '''
        This function read the WaterGAP binary output and returns data into numpy array.

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
        >>> tws_2003.shape
        (66740, 12)
        >>> tws_2003 = WGapOutput.read_unf(filename, ncol=12)
        >>> tws_2003.shape
        (66740, 12)
        >>> tws_2003 = WGapOutput.read_unf(filename, file_endian=FileEndian.big_endian)
        >>> tws_2003.shape
        (66740, 12)
        >>> tws_2003 = WGapOutput.read_unf(filename)
        >>> tws_2003.shape
        (66740, 12)
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
    def read_unf_old(filename, file_endian=FileEndian.big_endian, ncol=0):
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

        data = np.array(data, dtype=np.float64)

        if basin:
            basin = np.array(basin)-1
            data = data[basin]
            data = np.nan_to_num(data)

        if weights:
            weights = np.array(weights)
            if data.ndim == 1: data = data * weights
            else: data = data * weights[:, None]

            data = np.sum(data, axis=0) / np.sum(weights)
        else: data = np.sum(data, axis=0)

        return data.tolist()