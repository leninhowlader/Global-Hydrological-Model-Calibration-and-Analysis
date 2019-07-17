__author__ = 'mhasan'

import sys, os, numpy as np
sys.path.append('..')
from utilities.fileio import read_flat_file, write_flat_file

class Station:
    station_datafile = 'data/ALLSTATIONS.DAT'
    stations = []

    @staticmethod
    def get_fullpath_station_file():
        '''
        Generates the full path of station data file

        :return: (string) full path of station data file
        '''
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), Station.station_datafile)

    @staticmethod
    def set_station_filename(filename):
        '''
        Sets station filename
        :param filename: (string) station filename
        :return: None
        '''

        if filename: Station.station_datafile = filename

    @staticmethod
    def read_stations(filename=''):
        '''
        Reads station info from file

        :param filename: (string) filename
        :return: None
        '''
        # set station filename when applicable
        if filename and not os.path.exists(filename) and Station.station_datafile != filename:
            Station.station_datafile = filename
            filename = ''

        # generate full pathname of station datafile, if filename is not provided explicitly
        if not filename: filename = Station.get_fullpath_station_file()

        # read stations from the file
        stations = np.array([])
        if os.path.exists(filename):
            d = np.loadtxt(filename, skiprows=0, ndmin=2)
            if len(d) > 0: stations = d[:,:3]

        # assign stations into class variable
        Station.stations = stations

    @staticmethod
    def get_stations():
        '''
        Returns all stations

        :return: (2-d numpy array) list of all stations
        '''
        if len(Station.stations) == 0: Station.read_stations()

        return Station.stations

    @staticmethod
    def find_station_id(latitude, longitude):
        '''
        Finds station id of the station specified with its geolocation.

        :param latitude: (float) latitude of a given station
        :param longitude: (float) longitude of a given station
        :return: (int) station id
        '''

        stations = Station.get_stations()

        station_id = None
        if len(stations) > 0:
            ndx = np.where((stations[:,1]==longitude) & (stations[:,2]==latitude))
            station_id = stations[ndx][0,0].astype(int)


        return station_id

    @staticmethod
    def find_stations(coordinates, first_column_as_latitude=True):
        '''
        Finds stations by their location coordinates from the station list

        :param coordinates: (list of tuples or list) longitude and latitude of target stations
        :param first_column_as_latitude: (boolean, optional, default = True) a flag to indicate that the first column of
                                    the geo-coordinates are latitude. If the flag is set false, the first column will
                                    be taken as latitudes of target stations
        :return: (2-d numpy array) list of selected stations
        '''
        stations = Station.get_stations()

        if first_column_as_latitude: coordinates = np.array(coordinates)[:, [1,0]]
        else: coordinates = np.array(coordinates)

        selected_stations = None
        for station_coord in coordinates:
            ndx = np.where((stations[:, 1] == station_coord[0]) & (stations[:, 2] == station_coord[1]))
            temp = stations[ndx]

            try: selected_stations = np.concatenate((selected_stations, temp), axis=0)
            except: selected_stations = temp

        return selected_stations

    @staticmethod
    def write_stations(stations, filename):
        succeed = False

        data = []
        for s in stations: data.append(list(s) + [-99] * (6 - len(s)))
        if data: succeed = write_flat_file(filename, data, separator=' ')

        return succeed