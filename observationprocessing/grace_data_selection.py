#!/usr/bin/python3

# Author:  H.M. Mehedi Hasan
# Date: May, 2016
#
# The purpose of the program is to read the GRACE anomalies data for locations specified by either by WGHM cell numbers or
# geographical coordinates of Grace 1-degree cell centroids. However, if no cell reference is provided, in terms of WGHM
# cell numbers, data will be read for the whole world. The null values will not be included during data reading.
#
# The program starts with defining some control variables which specify how the read operation will behave. Setting these
# control variables users may direct reading and processing operations.
#
# Data in GRACE data-files must be organized in three columns (i.e. longitude, latitude, and anomaly value) separated by
# spaces. (The number of spaces does not matter). Data-files may contain some header lines and user may or may not
# provide the number of lines to be excluded skipped. If the number of header lines are not specified but the data-file
# contains headers, the read operation will not be terminated. Rather, it is assumed that the header lines will be
# excluded automatically during the conversion of 'text numerals' into numbers.
#
# Instructions for users having no experience of python language:
# (i) work only with control variables
# (ii) in python, variables are not typed; that is, any variable can take any valid value of any type. therefore, read
# the control variable notes carefully before modifying value of any control variable
# (iii) do not change the variable names before equality sign ('=')
# (iv) python defines instruction-levels based on indentation of statements. thus, it is important that the var_definition
# of all control variables must start at the first column of new lines
# (v) python is case sensitive, 'True' is valid boolean only and only with a capital 'T'; so as 'False' with capital 'F'
# (vi) the very first line of the script is required to run this script in linux. here is the line again if in case
# you have already modified accidentally "#!/usr/bin/python3".


# 1. CONTROL VARIABLES - DEFINITION
target_cells_only = True                    # a flag specifies if target cells are given
grace_1deg_cells = []                       # container for the GRACE 1-degree cell centroid coordinates (see note 2.1)
target_wghm_cells = []                      # container for WGHM cell numbers (see note 2.2)
read_wghm_cells_from = 'brahmaputra_bahadurbad_2646100_upstream.txt' # config_filename from which WGHM cell numbers could be generated (see note 2.3)
is_data_archived = True                     # a flag specifies if the data-files are archived into tar file
data_files = ['/media/sf_mhasan/private/GRACE/EGSIEM_DDK2.tar']# container for storing data-files (see note 2.4)
data_directories = []                       # container for storing data-directories (see note 2.5)
start_year = 2002                           # specifies the bottom limit of allowable temporal range (see note 2.6)
end_year = 2014                             # specifies the upper limit of the allowable temporal range (see note 2.6)
skip_lines = 0                              # no. of header lines to be skipped
null_value = 32767                          # null representation (see note 2.7)
output_file = 'brahmaputra_bahadurbad_2646100_EGSIEMDDK2_km3_2.csv'        # output config_filename
flag_basin_level_output = True              # a flag determines if the group average to be calculated (see note 2.8)
apply_correction_factor = True              # a flag determines whether correction factor to be applied (see note 2.9)
correction_factor_datafile = '/media/sf_mhasan/private/GRACE/LND_1x1_scalingFactor_DDK2.txt' # correction factor datafile (see note 2.9)
unit_conversion_factor = 10**-3             # unit conversion multiplier
apply_mean_shift = True                     # flag determines if current mean to be shifted to the mean between start and end year
cell_area_file = ''#'brahmaputra_area.txt'          # config_filename containing cell areas (see note 2.10)
flag_output_as_volume = True

# 2. CONTROL VARIABLES - SPECIAL NOTES
#
# 2.1 grace_1deg_cells
# centroid coordinates of a target GRACE 1-degree cells must be provided either as python-list,
# e.g [85.5, -123.5] or as python-tupple, e.g. (85.5, -123.5). In either case, latitude of the centroid must be identified
# first followed by the longitude.
# This container is a two-dimensional container of the cell coordinates. Thus, each cell must be a member of any group.
# That means, even if physical group does not exist, cells must be provided in single-member groups.
# Groups must be represented in python list and must be separated with commas. Group members must also be separated
# by commas.
# example: Cell belonging in no physical group
# grace_1deg_cells =  [  [(85.5, -123.5)] , [(84.5, -123.5)] ]
# example: Cell belonging in groups
# grace_1deg_cells =  [  [ (85.5, -123.5), (84.5, -123.5) ] , [(84.5, -123.5)] ]
#
# 2.2 target_wghm_cells
# WGHM cell reference numbers must be provided in one-dimensional comma-separated list. This variable is only used if
# GRACE 1-degree cell centroids are not provided. PLEASE, ALSO NOTE THAT WGHM CELLS NEEDS TO BE MAPPED WITH THE EXACT
# GEOGRAPHICAL LOCATION COORDINATES. THE MAPPING INFORMATION IS PROVIDED THROUGH wghm_grid.csv FILE. MAKE SURE THAT THE
# MAPPING FILE EXISTS IN THE HOME DIRECTORY OF THIS SCRIPT.
# example: target_wghm_cells = [ 23, 235, 2345, 6 ]

# 2.3 read_wghm_cells_from
# In case of large cell WGHM cell reference numbers, numbers can be written in a separate file. The cell numbers must be
# separated by commas. Cell numbers can be presented in groups using a pair of brackets i.e., [ ]. In this case, a group
# contains multiple 0.5-degree WGHM grid cell reference numbers that are located in one 1-degree grid cell. Usually, the
# grouping will be done during another process called 'upstream detection' and the groups will be saved into a text file.
# The same file can be used here for referencing WGHM cell numbers. Each group may contain 4 member cells at maximum and
# the current program only takes the first member for mapping purpose. However, this file will only be read if cell lists
# (i.e. grace_1deg_cells and target_wghm_cells) are found empty.
# example: read_wghm_cells_from = 'target_cell.txt'
# (inside target_cell.text: only cell number)
#     23, 235, 2345, 6...
# (inside target_cell.text: cell numbers with grouping)
#    [23, 24, 25], [235], [2345, 2346], [6] ....
#
# 2.4 data_files
# The file-names in the list can be either absolute or relative from the home-output_directory of the program. Data-files contain
# monthly data and the reference month and year information is read from the config_filename. Therefore, IT IS VERY IMPORTANT TO
# NOTE THAT FILENAMES MUST FOLLOW THE FOLLOWING FORMAT: some_name_[year]_[month].3character_extension. IF THE YEAR AND
# MONTH INFORMATION CANNOT BE GENERATED FROM THE FILENAME, THE FILE WILL NOT BE READ IN.
# example: data_files = [ 'data_file_2003_01.txt', 'data_file_2003_02.txt' ]
#
# 2.5 data_directories
# In case of many data-files, files can be stored in directories and the output_directory-addresses can be proving in this
# list container. This list becomes useful only if the data file list is found empty. If the archive flag is set on,
# only the .tar files will be considered and added to the data file list; otherwise, all files in the target output_directory
# will be added. The output_directory-paths can be absolute or relative to the home output_directory of this program.
# example: data_directories = [ '../GRACE/AIUB', '../GRACE/GFZ' ]
#
# 2.6 start_year and end_year
# If the variable are not set, the default value for start year would be set to 2003 and end year will be set to the
# current year. If start year is found greater than end year, start year will be reset to the end year.
#
# 2.7 null_value
# The default null value representation is 32767. ALL DIFFERENT DATA-FILES MUST HAVE SAME DEFAULT REPRESENTATIONS.
#
# 2.8 flag_basin_level_output
# If this flag is set TRUE, group averages will be calculated. In this case, cell coordinates will be omitted in the
# output file and group number (positional number starting from 1) will be added.
#
# 2.9 apply_correction_factor and correction_factor_datafile
# apply_correction_factor flag determines whether or not the correction factors will be applied to the grace data. If
# the flag is set 'True', correction factor datafile must be specified. Correction datafile must have 6 header lines,
# that will be skipped during reading the file, followed by data rows in three columns. The first column must be the
# longitude of 1-degree grid centroid, the second one should be the latitude of the centroid and the final column must
# contain the correction factor value. The value 32767 will be considered as null representation.
# Datafile must contain values for all specified target cells, otherwise, the program will stop with error.
#
# 2.10 cell_area_file
# If cell area file is provided, cell area will be taken from the file and instead of computing the group average, weighting
# averages will be computed. However, if the structure and length of areas in the area file does not match with provided
# cell numbers, the program will terminate with an error.


#---------------------------:) DO NOT CHANGE ANYTHING BELOW IF YOU ARE NOT CONFIDENT :)----------------------------------#

# IMPORT STATEMENTS
import sys, tarfile, os
sys.path.extend('..')
from utilities.grid import grid
from datetime import datetime
from utilities.fileio import write_flat_file, read_flat_file

# 3. FUNCTION TO READ THE ARCHIVED DATA-FILES
def read_grace_tar_archive(filename, start_year=2003, end_year=2016, skip_lines=0, null_value=32767, target_cell=[]):
    # target cell must be represented by its centroid latitude and longitude e.g. (89.5, -179.5)

    records = []
    headers = ['year', 'month', 'longitude', 'latitude', 'anomaly']

    tar_archive = None
    try:
        # open the archive
        tar_archive = tarfile.open(filename, 'r')

        # for each archived file extract the content in memory and read the virtual
        # file content by lines. however, before further processing, find year and
        # month from the archived file and continue only if the year is withing the
        # specified range
        for tf in tar_archive:
            f = tar_archive.extractfile(tf)

            year = int(tf.name[-11:-7])
            month = int(tf.name[-6:-4])
            if not (start_year<=year<=end_year): continue

            # if target cells are specified, while reading the data file line by line
            # check if latitude and longitude for a point is included inside cell list.
            # if the point is included, add the record if the anomaly value is not null.
            # however, if target cells are not specified, only check if the value is not
            # null.
            month_record = []
            if target_cell:
                for line in f.readlines()[skip_lines:]:
                    temp = line.split()

                    try:
                        temp[0] = float(temp[0])
                        temp[1] = float(temp[1])
                        if (temp[1], temp[0]) not in target_cell: continue
                        temp[2] = float(temp[2])
                        if temp[2] != null_value: month_record.append([year, month] + temp)
                    except: pass
            else:
                for line in f.readlines()[skip_lines:]:
                    temp = line.split()

                    try:
                        temp[0] = float(temp[0])
                        temp[1] = float(temp[1])
                        temp[2] = float(temp[2])
                        if temp[2] != null_value: month_record.append([year, month] + temp)
                    except: pass

            records += month_record
    except: return None
    finally:
        try: tar_archive.close()
        except: pass

    return headers, records

#4. FUNCTION TO READ THE FLAT DATA-FILE
def read_grace_unzipped_file(filename, start_year=2003, end_year=2016, skip_lines=0, null_value=32767, target_cell=[]):
    # target cell must be represented by its centroid latitude and longitude e.g. (89.5, -179.5)

    records = []
    headers = ['year', 'month', 'longitude', 'latitude', 'anomaly']

    f = None
    try:
        # find year and month and check if the year is within valid range
        year = int(filename[-11:-7])
        month = int(filename[-6:-4])

        if not (start_year<=year<=end_year): return None

        # open data file
        f = open(filename, 'r')

        # if target cells are specified, while reading the data file line by line
        # check if latitude and longitude for a point is included inside cell list.
        # if the point is included, add the record if the anomaly value is not null.
        # however, if target cells are not specified, only check if the value is not
        # null
        if target_cell:
            for line in f.readlines()[skip_lines:]:
                temp = line.split()

                try:
                    temp[0] = float(temp[0])
                    temp[1] = float(temp[1])
                    if (temp[1], temp[0]) not in target_cell: continue
                    temp[2] = float(temp[2])
                    if temp[2] != null_value: records.append([year, month] + temp)
                except: pass
        else:
            for line in f.readlines()[skip_lines:]:
                temp = line.split()

                try:
                    temp[0] = float(temp[0])
                    temp[1] = float(temp[1])
                    temp[2] = float(temp[2])
                    if temp[2] != null_value: records.append([year, month] + temp)
                except: pass
    except: return None
    finally:
        # close data file
        try: f.close()
        except: pass

    return headers, records

# method of finding correction factors from correction datafile
def read_correction_factors(correction_datafile, target_cells=[]):
    correction_factors = {}

    headers, temp = read_flat_file(correction_datafile, separator='', skiplines=6)
    if temp:
        for i in reversed(range(len(temp))):
            if len(temp[i]) != 3 or temp[i][2] == 32767.0:
                temp.pop(i)

        if temp:
            if target_cells:
                for tcell in target_cells:
                    for cfd in temp:
                        if cfd[0] == tcell[1] and cfd[1] == tcell[0]:
                            correction_factors[(tcell[0], tcell[1])] = cfd[2]
                            break
            else:
                for cfd in temp: correction_factors[(cfd[1], cfd[0])] = cfd[2]

    return correction_factors


# 5 MAIN FUNCTION
def main():
    global target_cells_only, target_wghm_cells, read_wghm_cells_from, grace_1deg_cells
    global is_data_archived, data_files, data_directories, start_year, end_year
    global skip_lines, null_value, output_file, flag_basin_level_output
    global apply_correction_factor, correction_factor_datafile
    global unit_conversion_factor, apply_mean_shift, cell_area_file
    global flag_output_as_volume

    succeed = False
    areas = []
    notes = []

    print('Checking necessary inputs ....')
    print('\t>> target cells ... '.ljust(50, ' '), end='', flush=True)
    if target_cells_only:
        if grace_1deg_cells:
            # check if grace cell list is readily available
            # clean ill-formated data if any
            for cgroup in grace_1deg_cells:
                for i in reversed(range(len(cgroup))):
                    if (len(cgroup[i]) != 2 or not (-90<=cgroup[i][0]<=90)
                        or not (-180<=cgroup[i][1]<=180)):
                        cgroup.pop(i)

            # check if the grace cell list is not empty after cleaning
            if grace_1deg_cells: succeed = True

        # if grace cell list is not provided, try to generate list of grace cells
        # either from wghm cell numbers or reading from the file where wghm cell
        # number could be found
        if not succeed:
            # if target wghm cell numbers are not provided, read cell numbers
            # from file, if file path is given
            if not target_wghm_cells and read_wghm_cells_from:
                target_wghm_cells = grid.read_groupfile(read_wghm_cells_from)

            if target_wghm_cells:
                # for each group of wghm cells, delete duplicate wghm cells if any
                for i in range(len(target_wghm_cells)):
                    for j in reversed(range(1, len(target_wghm_cells[i]))):
                        for k in range(j):
                            if target_wghm_cells[i][j] == target_wghm_cells[i][k]:
                                target_wghm_cells[i].pop(j)
                                break

                # clearing grace cell list; required in case of ill-formatted data
                grace_1deg_cells.clear()

                # read the cell-centroid (latitude, longitude) for each wghm 0.5-deg cell in each group and
                # find the corresponding cell-centroids for grace 1.0-deg cell.
                for basin in target_wghm_cells:
                    temp = []
                    for cnum in basin:
                        centroid_lat, centroid_lng = grid.map_centroid_from_wghm_cell_number(cnum)
                        grace_row, grace_col = grid.find_row_column(centroid_lat, centroid_lng, 1.0)
                        centroid_lat, centroid_lng = grid.find_centroid(grace_row, grace_col, 1.0)
                        if 90>=centroid_lat>=-90 and 180>=centroid_lng>=-180: temp.append((centroid_lat, centroid_lng))
                    if len(temp) == len(basin): grace_1deg_cells.append(temp)
                    else: break
                else: succeed = True
        # if grace cell list is still empty, exit with an error message.
        if not succeed:
            message = '[Error]\n\t\ttarget cells flag has been set but inforamtion regarding cell number(s) could not be generated!'
            print(message)
            exit(os.EX_DATAERR)
        else: print('[okay]')
    else: print('[not required]')


    # if the data file list is empty, try to generate file list from output_directory list if provided
    print('\t>> grace data-file/file list ...'.ljust(50, ' '), end='', flush=True)
    if not data_files:
        # if output_directory list is not empty, for each output_directory find file list (flist).  add files
        # in the data file list if data files are not archived (i.e. archived flag is False).
        # otherwise, check each file by its name to find if the file is a tar archive and add
        # only the archive files in the data file list
        if data_directories:
            for directory in data_directories:
                flist = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
                if is_data_archived:
                    for f in flist:
                        if f[-3:].lower() == 'tar': data_files.append(os.path.join(directory, f))
                else: data_files += flist

        # if data file list is still empty, exit with error
        if not data_files:
            message = '[Error]\n\t\tno data file has been specified!'
            print(message)
            exit(os.EX_NOINPUT)
    print('[okay]')


    # when the correction flag is set ON, check if correction factor datafile is available
    print('\t>> correction faction data-file ...'.ljust(50, ' '), end='', flush=True)
    if apply_correction_factor:
        if (not correction_factor_datafile) or (not os.path.exists(correction_factor_datafile)):
            message = '[Error]\n\t\tdatafile for correction factors is required but not provided.'
            print(message)
            exit(os.EX_NOINPUT)
        else: print('[okay]')
    else: print('[not required]')

    # Cell area is required for Basin Level Output. Thus, if basin level output flag is set TRUE, check if cell areas
    # can be generated using the cell area data-file or (if wghm cell numbers are available) using wghm cell number
    print('\t>> cell area ...'.ljust(50, ' '), end='', flush=True)
    if flag_basin_level_output or flag_output_as_volume:
        succeed = False
        if target_wghm_cells:
            for basin in target_wghm_cells:
                temp = []
                for cnum in basin:
                    row = grid.find_row_number(grid.map_centroid_from_wghm_cell_number(cnum)[0])
                    temp.append(grid.find_wghm_cellarea(row))
                areas.append(temp)
            succeed = True

        message = ''
        if not succeed and cell_area_file and os.path.exists(cell_area_file):
            temp = grid.read_groupfile(cell_area_file, data_type='float')

            if len(temp) != len(grace_1deg_cells):
                message = '[Error]\n\t\tnumber of groups in cell area file is inconsistent with the number of target groups.'
            else:
                for i in range(len(temp)):
                    if len(temp[i]) != len(grace_1deg_cells[i]):
                        print(len(temp[i]), len(grace_1deg_cells[i]))
                        message = '[Error]\n\t\tnumber of cell does not match in area file.'
                        break
                else:
                    areas = temp
                    succeed = True

        if not succeed:
            if message: print(message)
            else: print('[not okay]')
            exit(os.EX_DATAERR)
        else: print('[okay]')
    else: print('[not required]')

    # check and correct other control variables
    print('\t>> Others (start year, end year etc) ...'.ljust(50, ' '), end='', flush=True)
    if skip_lines < 0: skip_lines = 0
    if start_year == -1: start_year = 2003
    if end_year == -1: end_year = datetime.now().year
    if start_year > end_year: start_year = end_year
    print('[okay]')

    # if all required inputs are provided, start reading grace data.

    # ATTENTION:
    # it is expected that the datafiles contains monthly data with three columns (i.e. longitude,
    # latitude, and anomaly in the exact order). Also, year and month information is expected to
    # be included in the names of the datafiles in the following format: SOMEDATA_[year]_[mon].txt.

    # if datafiles are archived, it is expected that tar archiving format is used

    print('\nThe program has started retrieving data..')

    #convert 2-D grace_1deg_cells into 1-D list of grace cells
    clist_1D = []
    for cgroup in grace_1deg_cells:
        for c in cgroup:
            if c not in clist_1D: clist_1D.append(c)

    records = {}
    if is_data_archived:
        for filename in data_files:
            print('\t>> reading data from file "%s"..' %filename, end='', flush=True)
            headers, temp = read_grace_tar_archive(filename, start_year, end_year, skip_lines, null_value, clist_1D)
            if temp:
                for r in temp:
                    try: records[(r[3], r[2])].append([r[0], r[1], r[4]])
                    except: records[(r[3], r[2])] = [[r[0], r[1], r[4]]]
            print('[success]')
    else:
        for filename in data_files:
            print('\t>> reading data from file "%s"..' %filename, end='', flush=True)
            headers, temp = read_grace_unzipped_file(filename, start_year, end_year, skip_lines, null_value, clist_1D)
            if temp:
                for r in temp:
                    try: records[(r[3], r[2])].append([r[0], r[1], r[4]])
                    except: records[(r[3], r[2])] = [[r[0], r[1], r[4]]]
            print('[success]')

    record_count = 0
    for key in records.keys(): record_count += len(records[key])
    print ('\tTotal %d records retrieved.' %record_count)

    # apply further processing and save records in output file if data read was successful
    if records:
        print('\nPre-processing has started...')
        # applying correction factor if the correction flag is ON
        if apply_correction_factor:
            print('\t>> applying correction factor..', end='', flush=True)
            correction_factors = read_correction_factors(correction_factor_datafile, clist_1D)

            if not correction_factors:
                message = '[Error] \n\tcorrection factors could not be retrieved from the datafile - %s.'%correction_factor_datafile
                print(message)
                exit(os.EX_DATAERR)
            elif len(correction_factors) != len(clist_1D):
                message = '[Error] \n\tcorrection factors for some target cells are missing. Please check the correction datafile.'
                print(message)
                exit(os.EX_DATAERR)
            else:
                for key in records.keys():
                    rs = records[key]
                    cf = correction_factors[key]
                    for r in rs: r[2] *= cf

                print('[success]')


        # calculate group average
        if flag_basin_level_output:
            print('\t>> calculating basin statistic ..', end='', flush=True)
            idfun = lambda x, i: i + 1
        else:
            print('\t>> reorganizing and preparing output ..', end='', flush=True)
            idfun = lambda x, i: x[0]

            reshape_cells = []
            reshape_areas = []
            for i in range(len(grace_1deg_cells)):
                temp = {}
                for j in range(len(grace_1deg_cells[i])):
                    try: temp[grace_1deg_cells[i][j]].append(areas[i][j])
                    except: temp[grace_1deg_cells[i][j]] = [areas[i][j]]

                for key, value in temp.items():
                    reshape_cells.append([key])
                    reshape_areas.append([sum(value)])

            grace_1deg_cells = reshape_cells
            areas = reshape_areas


        data = {}
        if flag_output_as_volume: fun = lambda x, y: sum(x)
        else: fun = lambda x, y: sum(x)/y

        for i in range(len(grace_1deg_cells)):
            bid = idfun(grace_1deg_cells[i], i)                 # basin ID
            basin = grace_1deg_cells[i]
            barea = 0                   # basin area
            bdata = {}

            for j in range(len(basin)):
                cell = basin[j]
                cdata = records[cell]
                carea = areas[i][j]
                barea += carea

                for d in cdata:
                    try: bdata[(d[0], d[1])].append(d[2] * carea)
                    except: bdata[(d[0], d[1])] = [d[2] * carea]

            if bdata and barea > 0:
                keys = list(bdata.keys())
                keys.sort()

                for key in keys:
                    temp = bdata[key]
                    if len(temp) == len(basin):
                        bval = fun(temp, barea)
                        try: data[bid].append([key[0], key[1], bval])
                        except: data[bid] = [[key[0], key[1], bval]]

        if data:
            records = data
            print('[success]')
        else:
            print('[Error]\n\t\taverage calculation was unsuccessful.')
            exit(os.EX_DATAERR)

        # shift mean in anomaly data
        if apply_mean_shift:
            print('\t>> shifting mean ..', end='', flush=True)

            for key in records.keys():
                rs = records[key]
                temp = []
                for r in rs: temp.append(r[2])
                if temp:
                    mean = sum(temp)/len(temp)
                    for r in rs: r[2] -= mean

            print('[success]')

        #convert unit if require
        if records and unit_conversion_factor != 1.0:
            print('\t>> unit conversion ..', end='', flush=True)
            for key in records.keys():
                ds = records[key]
                for d in ds: d[2] *= unit_conversion_factor
            print('[success]')

        #saving file
        if records and output_file:
            print('\nSaving data into %s..' % output_file, end='', flush=True)
            header, data = [], []
            if flag_basin_level_output:
                headers = ['group_num', 'year', 'month', 'anomaly']
                keys = list(records.keys())
                keys.sort()
                for key in keys:
                    ds = records[key]
                    for d in ds: data.append([key] + d)
            else:
                # # check if wghm cell number is readily available, if not generate wghm cell number
                # check_success = True
                #
                # if not target_wghm_cells: check_success = False
                # elif len(grace_1deg_cells) != len(target_wghm_cells): check_success = False
                # else:
                #     for i in range(len(grace_1deg_cells)):
                #         if len(grace_1deg_cells[i]) != target_wghm_cells[i]:
                #             check_success = False
                #             break
                #
                # if not check_success:
                #     for cgroup in grace_1deg_cells:
                #         temp = []
                #
                #         for cell in cgroup:
                #             row, col = grid.find_row_column(cell[0], cell[1], degree_resolution=0.5)
                #             cnum = grid.map_wghm_cell_number(row, col, base_resolution=0.5)
                #             temp.append(cnum)
                #
                #         if len(temp) == len(cgroup): target_wghm_cells.append(temp)
                #         else:
                #             print('[Error]\n\t\tWGHM cell number could not be generated.')
                #             exit(os.EX_DATAERR)
                #
                headers = ['cell_num', 'longitude', 'latitude', 'year', 'month', 'anomaly']
                keys = list(records.keys())
                keys.sort()
                for key in keys:
                    ds = records[key]
                    r, c = grid.find_row_column(key[0], key[1], degree_resolution=0.5)
                    cnum = grid.map_wghm_cell_number(r, c, base_resolution=0.5)
                    if cnum:
                        for d in ds: data.append([cnum, key[1], key[0]] + d)

            if data and headers:
                # write data into files
                if write_flat_file(output_file, data, headers, separator=','):
                    print('[success]')
                else:
                    message = '[Error]\n\t\tdata could not be saved. Check weather the output config_filename is correct.'
                    print(message)
                    exit(os.EX_IOERR)
        else:
            message = '(Error) Output config_filename was not provided.'
            print(message)
            exit(os.EX_CONFIG)
    else:
        message = '(Error) Either the data-files could not be found or data-files are ill-formatted.'
        print(message)
        exit(os.EX_CONFIG)

    # exit success
    print('\nProgram exits normally.Thank you for using this program!')
    exit(os.EX_OK)

if __name__ == '__main__':
    main()