__author__ = 'mhasan'

import sys, os
sys.path.append('..')
from utilities.fileio import read_flat_file, write_flat_file

class Station:
    station_datafile = 'data/ALLSTATIONS.DAT'
    stations = []

    @staticmethod
    def get_default_station_file(): return os.path.join(os.path.dirname(os.path.realpath(__file__)), Station.station_datafile)

    # method of reading stations [from a file]
    @staticmethod
    def read_stations(station_file=''):
        stations = []
        if station_file == '':
            if Station.stations: return Station.stations
            else:
                if Station.station_datafile: stations = Station.read_stations(Station.get_default_station_file())

                if stations: Station.stations = stations
        else:
            h, stations = read_flat_file(station_file, separator=' ', header=False)
            if stations:
                for i in reversed(range(len(stations))):
                    if len(stations[i]) < 3 or not (-180 <= stations[i][1] <= 180) or not (
                            -90 <= stations[i][2] <= 90): stations.pop(i)
                    else: stations[i] = tuple(stations[i][:-3])
            else: stations = []

        return stations

    # method of finding station id (this method was not used so far)
    @staticmethod
    def find_station_id(latitude, longitude, station_file=''):
        stations = Station.read_stations(station_file)

        station_id = None
        if stations:
            for s in stations:
                if s[2] == latitude and s[1] == longitude:
                    station_id = s[0]
                    break

        return station_id

    # method of selecting stations from the station datafile and creating a subset of the stations
    @staticmethod
    def select_stations(coordinates, station_file='', lat_first=True):
        stations = Station.read_stations(station_file)

        selected_stations = []
        if stations:
            if lat_first:
                for coord in coordinates:
                    for st in stations:
                        if st[2] == coord[0] and st[1] == coord[1]:
                            selected_stations.append(st)
                            break
            else:
                for coord in coordinates:
                    for st in stations:
                        if st[1] == coord[0] and st[2] == coord[1]:
                            selected_stations.append(st)
                            break

        return selected_stations

    @staticmethod
    def write_stations(stations, filename):
        succeed = False

        data = []
        for s in stations: data.append(list(s) + [-99] * (6 - len(s)))
        if data: succeed = write_flat_file(filename, data, separator=' ')

        return succeed