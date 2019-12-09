#!/usr/bin/python3

# Author: H.M. Mehedi Hasan
# Data: May, 2016

# This program creates a subset of the all stations in the station datafile and write the subset stations into an
# output file. The program is useful for selecting some stations given their geo-locations and create the station.dat
# file required for the water-gap model.
#
# # Instructions for users having no experience of python language:
# (i) work only with control variables
# (ii) in python, variables are not typed; that is, any variable can take any valid value of any type. therefore, read
# the control variable notes carefully before modifying value of any control variable
# (iii) do not change the variable names before equality sign ('=')
# (iv) python defines instruction-levels based on indentation of statements. thus, it is important that the var_definition
# of all control variables must start at the first column of new lines
# (v) python is case sensitive, 'True' is valid boolean only and only with a capital 'T'; so as 'False' with capital 'F'
# (vi) the very first line of the script is required to run this script in linux. here is the line again if in case
# you have already modified accidentally "#!/usr/bin/python3".

# 1. CONTROL VARIABLES: DEFINITION AND VALUES
station_datafile = ''#''STATIONS_ALL.DAT'                           # datafile for all stations
target_station_coordinates = [(25.25, 87.75), (25.25, 89.75)]   # target station coordinates (see note 2.1)
print_on_screen = False                                         # if the output is to be shown on screen (see note 2.2)
output_file = 'STATIONS.DAT'                                    # output filename_data

# 2. CONTROL VARIABLE: NOTES
# 2.1: target_station_coordinates
# The coordinates must be written in parentheses and latitude comes first followed by the longitude.
#
# 2.2: print_on_screen and output_file
# If on screen printing flag is ON, output will be printed on screen only. If not, output_file must be provided to store
# the output in the output file.

#---------------------------:) DO NOT CHANGE ANYTHING BELOW IF YOU ARE NOT CONFIDENT :)----------------------------------#

# IMPORT STATEMENTS
import os, sys
from utilities.fileio import FileInputOutput as io
from utilities.globalgrid import GlobalGrid
from utilities.station import Station

# STATIC VARIABLE
stations = []

# method of reading the stations from the station datafile
def read_stations(station_file=''):
    global stations, station_datafile

    if not station_file: station_file = station_datafile
    if stations: stations.clear()

    headers, temp_data = io.read_flat_file(station_file, separator='')
    if temp_data:
        for i in reversed(range(len(temp_data))):
            if len(temp_data[i]) < 3 or not (-180<=temp_data[i][1]<=180) or not (-90<=temp_data[i][2]<=90):
                temp_data.pop(i)

    if temp_data: stations += temp_data

# method of finding station id (this method was not used so far)
def find_station_id1(latitude, longitude, station_file=''):
    global stations

    if not stations: read_stations(station_file)

    station_id = 0
    for data in stations:
        if data[2] == latitude and data[1] == longitude:
            station_id = data[0]
            break

    return station_id

# method of selecting stations from the station datafile and creating a subset of the stations
def select_stations(coordinates, station_file):
    global stations

    selected_stations = []

    if not stations: read_stations(station_file)

    if stations:
        for coord in coordinates:
            for st in stations:
                if st[2] == coord[0] and st[1] == coord[1]:
                    selected_stations.append(st)
                    break

    return selected_stations


# var_definition of the main method
def main():
    global station_datafile, target_station_coordinates, print_on_screen, output_file

    # check inputs if they are provided correctly
    if not target_station_coordinates:
        message = '(Error) No station coordinate is given. Station coordinates are required!!'
        print(message)
        exit(os.EX_NOINPUT)
    # elif not station_datafile:
    #     message = '(Error) Station datafile is required but not given.'
    #     print(message)
    #     exit(os.EX_NOINPUT)
    elif not print_on_screen and not output_file:
        message = '(Error) Output config_filename is required but not given.'
        print(message)
        exit(os.EX_NOINPUT)
    else:
        #set station coordinates to the coordinates of nearest wghm grid cell centroids
        for i in range(len(target_station_coordinates)):
            row, col = GlobalGrid.find_row_column(target_station_coordinates[i][0], target_station_coordinates[i][1])
            lat, long = GlobalGrid.find_centroid(row, col, deg_resolution=0.5)
            target_station_coordinates[i] = (lat, long)

        if not station_datafile: station_datafile = Station.get_fullpath_station_file()

        selected_station = select_stations(target_station_coordinates, station_datafile)

        if selected_station:
            if print_on_screen:
                print('Selected Station(s):\n'+ 'statioin_id'.ljust(12) + 'longitude'.rjust(12) + 'latitude'.rjust(12))

                for station in selected_station:
                    print(str(station[0]).ljust(12) + str(station[1]).rjust(12) + str(station[2]).rjust(12))
            else:
                if Station.write_stations(selected_station, output_file):
                    print('Selected station(s) are stored in %s.'%output_file)
                else:
                    print('(Error) Stations could not be saved in %s.'%output_file)
                    exit(os.EX_IOERR)
        else:
            print('No station was found!!')



    print('\nThe program ends with success..')
    exit(os.EX_OK)

main()