#!/usr/bin/python3

# Author: H.M. Mehedi Hasan
# Date: May, 2016
#
# This program is written to select necessary GRDC data for target GRDC stations. First, GRDC stations will be read
# from given station file. Then regarding datafiles will be read for selected stations for the data directory for
# specified period of time. Finally, selected data will be stored in a data file.
#
# During calibration of WaterGAP model, data will be compared according to cell numbers in model grid. Thus, in the
# output data file, wghm cell number will also be appended.
#
#
# Instructions for users having no experience of python language:
# (i) work only with control variables
# (ii) in python, variables are not typed; that is, any variable can take any valid value of any type. therefore, read
# the control variable notes carefully before modifying value of any control variable
# (iii) do not change the variable names before equality sign ('=')
# (iv) python defines instruction-levels based on indentation of statements. thus, it is important that the definition
# of all control variables must start at the first column of new lines
# (v) python is case sensitive, 'True' is valid boolean only and only with a capital 'T'; so as 'False' with capital 'F'
# (vi) the very first line of the script is required to run this script in linux. here is the line again if in case
# you have already modified accidentally "#!/usr/bin/python3".





# 1. CONTROL VARIABLES: DEFINITION
station_file = 'STATIONS.DAT'                   # path of the file from where stations will be selected (see note 2.1)
grdc_data_directory = '../grdc_data'            # data directory name
start_year = 2003                               # year from which data gathering starts
end_year = 2009                                 # until which year data will be gathered
output_file = 'grdc_2646200.txt'                # output config_filename

# 2. CONTROL VARIABLES: NOTES
# 2.1 station_file
# Station file must have the same structure as the station file used by WaterGAP model.





#---------------------------:) DO NOT CHANGE ANYTHING BELOW IF YOU ARE NOT CONFIDENT :)----------------------------------#
from datetime import datetime
import os
from fileio import read_flat_file, write_flat_file
from grid import grid

# method of finding stations along with their coordinates
def find_stations_from_file(station_file):
    headers, records = read_flat_file(station_file, separator=' ', header=False)

    stations = {}       # structure: {station_id: (latitude, longitude), station_2: (latitude, longitude), ..}
    if records:
        for record in records:
            if len(record) >= 3 and -90<=record[2]<=90 and -180<=record[1]<=180:
                stations[record[0]] = (record[2], record[1])

    return stations

# main method
def main():
    global station_file, grdc_data_directory, output_file, start_year, end_year

    # generating station list from station file
    stations = {}       # structure: {station_id: (latitude, longitude), station_2: (latitude, longitude), ..}
    stations = find_stations_from_file(station_file)

    # from station coordinates find the corresponding wghm cell first and then find the wghm cell number; finally
    # replace coordinate pair with the wghm cell number in the stations list
    if stations:
        for station_id, coordinates in stations.items():
            row, col = grid.find_row_column(coordinates[0], coordinates[1], degree_resolution=0.5)
            cnum = grid.map_wghm_cell_number(row, col, base_resolution=0.5)
            if cnum : stations[station_id] = cnum
            else:
                message = 'Cell number in WGHM grid for latitude $d and longitude %d could not be retrieved. ' %coordinates
                message += 'The program will shut down.'
                print(message)
                exit(os.EX_DATAERR)
    else:
        message = 'Stations could not be retrieved from %s file. Check the station file.'%station_file
        print(message)
        exit(os.EX_DATAERR)

    # check if other required data is provided or not
    if not grdc_data_directory or not os.path.exists(grdc_data_directory):
        message = 'Data directory is required but not provided. Check control variables.'
        print(message)
        exit(os.EX_NOINPUT)
    elif not output_file:
        message = 'Output config_filename required but not given. Check control variable block.'
        print(message)
        exit(os.EX_NOINPUT)
    else:
        # if all required data is given, read target station-data

        # check consistency in start and end year
        if start_year <= 0 or start_year < 1901: start_year = 1901
        if start_year > datetime.now().year: start_year = datetime.now().year
        if end_year <= 0: end_year = datetime.now().year
        if end_year < start_year: end_year = start_year

        # find appropriate datafile from data-directory for each station, read data-file and screening data
        station_data = []
        for station_id, cnum in stations.items():
            d = grdc_data_directory
            file_list = [f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) and f.find(str(station_id))>=0]

            if not file_list:
                message = '(WARNING!!) NO DATA-FILE FOUND FOR STATION-%d'%station_id
                print(message)
            else:
                data = []
                for filename in file_list:
                    filename = os.path.join(grdc_data_directory, filename)
                    headers, temp_data = read_flat_file(filename, separator='')
                    if temp_data: data += temp_data

                if not data:
                    message = '(WARNING!!) DATA COULD NOT BE RETRIEVED FOR STATION-%d'%station_id
                    print(message)
                else:
                    # data screening
                    for i in reversed(range(len(data))):
                        if len(data[i]) != 4 or not (start_year<=data[i][0]<=end_year) or data[i][2] == -9999.0:
                            data.pop(i)
                        else: data[i] = [station_id, cnum] + data[i][:3]

                    if not data:
                        message = '(WARNING!!) NO VALID DATA FOUND FOR STATION-%d'%station_id
                        print(message)
                    else:
                        station_data += data

        if not station_data:
            message = '(Error) No valid data retrieved from following data-directory: %s'%grdc_data_directory
            print(message)
            exit(os.EX_DATAERR)
        else:
            headers = ['station', 'wcnum', 'year', 'month', 'discharge']
            if write_flat_file(output_file, station_data, headers, separator=' '):
                message = '%d data was successfully stored in %s'%(len(station_data), output_file)
                print(message)
            else:
                message = '(Error) Data was retrieved successful BUT COULD NOT BE STORED.'
                print(message)
                exit(os.EX_IOERR)

    # exit successfully
    print('The program ends successfully!!')
    exit(os.EX_OK)


main()
