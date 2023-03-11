# Author: H. M. Mehedi Hasan
# Date: April, 2016

# This script provides supplementary functions for reading and writing files.
import os
from datetime import datetime
import struct, time

try: import fcntl
except:
    class fcntl:
        LOCK_EX = False
        LOCK_NB = False
        LOCK_UN = False

        @staticmethod
        def lockf(*args): pass

class FileInputOutput:
    __on_screen_lock = '_SCRNOUT.LOCK'

    @staticmethod
    def set_on_screen_lock(lockfile):
        FileInputOutput.__on_screen_lock = lockfile

    @staticmethod
    def delete_lock_file(lockname=''):
        if not lockname: lockname = FileInputOutput.__on_screen_lock
        
        try: os.remove(lockname)
        except: pass

    @staticmethod
    def read_flat_file(
            filename,
            separator=' ',
            header=False,
            skiplines=0):
        '''
        sequentially read flat file.

        :param filename: (string) filename to be read
        :param separator: (string) delimiter or separator character. default
                        value is ' ' i.e., single space
        :param header: (boolean) specifies the presence of column names. default
                        value is false
        :param skiplines: (int) No. of lines to be skipped. default value is 0
        :return: (tuple of header and data) headers (1-d array) contains name of
                        columns; data (2-d array) contains data rows
        '''
        headers, data = [], []

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
                                        try: temp[i] = datetime.strptime(
                                                            temp[i], '%Y-%m-%d')
                                        except: pass
                            else: temp.pop(i)
                    if temp: data.append(temp)
        except: return None, None
        finally:
            try: obs_file.close()
            except: pass

        return headers, data

    @staticmethod
    def write_flat_file(
            filename,
            data,
            data_headers=[],
            header_lines=[],
            separator=',',
            append=False):
        '''
        writes flat files.

        :param filename: (string) name of the output file
        :param data: (2-d array of any kind) data to be written in file
        :param data_headers: (1-d array of string, optional) name of the columns
        :param header_lines: (1-d array of string, optional) lines to be written
                        at the beginning of the output file.
        :param separator: (string) a character that is used to separate data in
                        each rows. default value is ','
        :param append: (boolean) a flag specifies whether or not existing file
                        would be overwritten. if the value is true, data will be
                        written at the end of output file
        :return: (boolean) True on success; False otherwise
        '''

        succeed = True

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
        except: succeed = False
        finally:
            try: f.close()
            except: pass

        return succeed

    @staticmethod
    def read_binary_file(
            filename,
            chunk_size,
            chunk_format):
        '''
        Reads data from binary files.

        :param filename: (string) name of the file
        :param chunk_size: (int) size of each chunk in bytes
        :param chunk_format: (string) format of each chunk
        :return: (2-d array of records) data as list of rows. each row is
                        derived from a chunk of data
        '''
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

    @staticmethod
    def acquire_lock(fd, sleep_time=0.1):
        '''
        acquire exclusive lock on a file. [this method is only operational in
        unix operating systems]

        :param fd: (FILE) file descriptor
        :param sleep_time: (float) time in seconds. default value is 0.1 second.
        :return: (boolean) always returns True
        '''

        while True:
            try:
                fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except: time.sleep(sleep_time)

    @staticmethod
    def release_lock(fd, sleep_time=0.1):
        '''
        releases an acquired lock. [this method is only operational in unix
        based operating systems]

        :param fd: (FILE) file descriptor
        :param sleep_time: (float) sleep time in seconds. default value is 0.1
                        seconds
        :return: (boolean) always returns True
        '''

        while True:
            try:
                fcntl.lockf(fd, fcntl.LOCK_UN)
                return True
            except: time.sleep(sleep_time)

    @staticmethod
    def readwrite_unique_id(lockname):
        unique_id = 0
        fd = open('%s.LOCK' % lockname, 'w')
        if FileInputOutput.acquire_lock(fd):

            f = None
            try:
                f = open('%s.VALUE' % lockname, 'r')
                temp = f.readline().strip()
                unique_id = int(temp)
            except: pass
            finally:
                try: f.close()
                except: pass

            try:
                f = open('%s.VALUE' % lockname, 'w')
                f.write(str(unique_id + 1))
            except: unique_id = -9999
            finally:
                try: f.close()
                except: pass

            FileInputOutput.release_lock(fd)
        else: unique_id = -9999

        return unique_id

    @staticmethod
    def print_on_screen(message):
        '''
        prints a message on screen with sharing an exclusive lock among multiple
        processes.

        :param message: (string) message to be printed
        :return: None
        '''
        lockfile = FileInputOutput.__on_screen_lock

        f = open(lockfile, 'w')
        if FileInputOutput.acquire_lock(f):
            if type(message) is str: print(message)
            
            if type(message) is list:
                for m in message: print(m)

            FileInputOutput.release_lock(f)
        
        f.close()

    @staticmethod
    def print_on_file(
            lines,
            filename,
            lockname,
            sleep_time=0.1):
        '''
        write messages on a shared file.

        :param lines: (1-d list of string) list of messages. each message will
                        be written in separate line
        :param filename: (string) name of the target file where message will be
                        written
        :param lockname: (string) name of the lockfile that will be created and
                        shared among different processes for writing messages
                        on target file
        :param sleep_time: (float) sleep time in seconds. default is 0.1 sec
        :return: None
        '''

        fd = open(lockname, 'w')
        if FileInputOutput.acquire_lock(fd, sleep_time):
            f = None
            try:
                f = open(filename, 'a')
                for line in lines:
                    f.write(line + '\n')
            except: pass
            finally:
                f.close()
                FileInputOutput.release_lock(fd)
        fd.close()

