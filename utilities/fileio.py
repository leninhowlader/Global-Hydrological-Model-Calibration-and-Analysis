# Author: H. M. Mehedi Hasan
# Date: April, 2016

# This script provides supplementary functions for reading and writing files.

#---------------------------:) DO NOT CHANGE ANYTHING BELOW IF YOU ARE NOT CONFIDENT :)----------------------------------#

from datetime import datetime
import struct, time

# method for reading flat file
def read_flat_file(filename, separator=' ', header=False, skiplines=0):
    headers, data = [], []      #here headers is one dimensional and data is two dimensional array

    obs_file = None
    try:
        obs_file = open(filename, 'r')

        # step-01: skip lines
        if skiplines > 0:
            for i in range(skiplines): line = obs_file.readline()

        # step-02: read header names
        if header:
            line = obs_file.readline().strip()
            if line:
                temp = line.strip().split(separator)
                for i in range(len(temp)):
                    temp[i] = temp[i].strip().strip('"').strip('\'')
                    if temp[i]: headers.append(temp[i])

        # step-03: read data
        for line in obs_file.readlines():
            line = line.strip()
            if line:
                if separator:  temp = line.split(separator)
                else: temp = line.split()

                if temp:
                    for i in reversed(range(len(temp))):
                        temp[i] = temp[i].strip()
                        if temp[i]:
                            try: temp[i] = int(temp[i])
                            except:
                                try: temp[i] = float(temp[i])
                                except:
                                    try: temp[i] = datetime.strptime(temp[i], '%Y-%m-%d')
                                    except: pass
                        else: temp.pop(i)
                if temp: data.append(temp)
    except: return None, None
    finally:
        try: obs_file.close()
        except: pass

    return headers, data

# method for writing a flat file
def write_flat_file(filename, data, data_headers=[], header_lines=[], separator=',', append=False):
    ret_val = True

    f = None
    try:
        if append: f = open(filename, 'a')
        else: f = open(filename, 'w')

        if header_lines:
            for line in header_lines: f.write(line + '\n')

        if data_headers and len(data[0]) == len(data_headers):
            line = separator.join(str(x) for x in data_headers)
            f.write(line + '\n')

        for d in data:
            line = separator.join(str(x) for x in d)
            f.write(line + '\n')
    except: ret_val = False
    finally:
        try: f.close()
        except: pass

    return ret_val

# method for reading binary file
def read_binary_file(filename, chunk_size, chunk_format):
    list_of_record = []

    f = None
    try:
        f = open(filename, "rb")
        while True:
            block = f.read(chunk_size)
            if block:
                b = struct.unpack(chunk_format, block)
                list_of_record.append(list(b))
            else: break
    except:
        print('%s does not exist!'%filename)
    finally:
        try: f.close()
        except: pass

    return list_of_record

def read_UNF_file(filename, endian='big-endian', unf_type=-1, ncol=1):
    succeed = True

    if ncol <= 0:
        if filename.count('.') > 2:
            ndx1 = filename.find('.')
            ndx2 = filename.find('.', ndx1+1)

            temp = filename[ndx1+1: ndx2]
            try: ncol = int(temp)
            except: pass

        if not ncol> 0: succeed = False

    if succeed and unf_type not in [0,1,2,4]:
        try:
            unf_type = int(filename.strip()[-1])
            if unf_type not in [0,1,2,4]: succeed = False
        except: succeed = False

    d = None
    if succeed:
        format_str = ''
        if endian == 'big-endian': format_str += '>'
        elif endian == 'little-endian': format_str += '<'
        else: format_str += '@'

        block_size = 0
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

        if d and ncol == 1:
            tmp = []
            for t in d: tmp.append(t[0])
            d = tmp
    return d

def write_UNF_file(data, filename, endian='big-endian', unf_type=-1): return True
def acquire_lock(fd, sleep_time=0.1): return True
def release_lock(fd, sleep_time=0.1): return True
def print_on_screen(message): return True
def print_on_file(lines, filename, lockname, sleep_time=0.1): return True

# acquire lock
# def acquire_lock(fd, sleep_time=0.1):
#     while True:
#         try:
#             fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
#             return True
#         except: time.sleep(sleep_time)
#
# def release_lock(fd, sleep_time=0.1):
#     while True:
#         try:
#             fcntl.lockf(fd, fcntl.LOCK_UN)
#             return True
#         except: time.sleep(sleep_time)
#
# def print_on_screen(message):
#     f = open('_SCRNOUT.LOCK', 'w')
#     if acquire_lock(f):
#         print(message)
#         release_lock(f)
#     f.close()
#
# def print_on_file(lines, filename, lockname, sleep_time=0.1):
#     fd = open(lockname, 'w')
#     if acquire_lock(fd, sleep_time):
#         f = None
#         try:
#             f = open(filename, 'a')
#             for line in lines:
#                 f.write(line + '\n')
#         except: pass
#         finally:
#             f.close()
#             release_lock(fd)
#     fd.close()

