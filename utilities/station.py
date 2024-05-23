__author__ = 'mhasan'

import sys, os, numpy as np, pandas as pd

from utilities.fileio import FileInputOutput as io
from utilities.globalgrid import GlobalGrid as gg
from utilities.basininfo import BasinInfo

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
    def read_stations(filename='', unique_only:bool=True):
        '''
        Reads station info from file

        :param filename: (string) filename
        :param unique_only: (bool) a flag determines whether or not duplicate stations, if any, would be excluded
        :return: None
        '''
        # set station filename when applicable
        if filename and os.path.exists(filename) and Station.station_datafile != filename:
            Station.station_datafile = filename

        # generate full pathname of station datafile, if filename is not provided explicitly
        if not filename: filename = Station.get_fullpath_station_file()

        # read stations from the file
        stations = np.array([])
        if os.path.exists(filename):
            d = np.loadtxt(filename, skiprows=0, ndmin=2)
            # d = pd.read_csv(filename, header=None, sep=' ').values
            if len(d) > 0: stations = d[:,:3]
            # if unique_only: stations = np.unique(stations, axis=0)

        # assign stations into class variable
        Station.stations = stations

    @staticmethod
    def get_stations(filename:str='', rowcol_only=False):
        '''
        Returns all stations

        :param filename: (string) station filename
        :param rowcol_only: (bool) a flag determining if only row and col index of corresponding station cell would be
                            returned as output
        :return: (2-d numpy array) list of all stations
        '''

        if len(Station.stations) == 0 or len(filename) > 0: Station.read_stations(filename)

        if rowcol_only:
            rowcol = []
            for s in Station.stations: rowcol.append(gg.find_row_column(s[2], s[1]))
            return np.array(rowcol)
        else: return Station.stations

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
    def write_stations(stations, filename, id_as_integer=True):
        succeed = False
        
        data = []
        for s in stations: data.append(list(s) + [-99] * (6 - len(s)))
                
        if data:
            df = pd.DataFrame(data=data)
            if id_as_integer: df.iloc[:,0] = df.iloc[:0].astype(int)

            df.to_csv(filename, header=False, index=False, sep='\t')
            succeed = True            

        return succeed

    class GlobalCDA:
        @staticmethod
        def create_STATION_DAT_1509(filename):
            filename_station_info = os.path.join(
                'D:/mhasan/Experiments/POC_WB_II/data',
                'streamflow_stations_1509.txt'
            )
            
            df = pd.read_csv(filename_station_info)
            df = df.loc[:, ['ID_1', 'Lon_ddm30', 'Lat_ddm30']]
            df['a1'] = -99
            df['a2'] = -99
            df['a3'] = -99
            
            filename = os.path.join(
                'D:/mhasan/Code&Script/ProjectWGHM',
                'utilities/data/STATIONS1509.DAT'
            )
            df.to_csv(filename, header=False, index=False, sep='\t')
            
        @staticmethod
        def create_watergap_station_file_FGB(
            filename_out:str,
            basin_names=(), 
            entire_basin=True
        ):
            succeed = True

            excluded_basins = ['vilaine', 'adour']

            basins = {}
            if entire_basin:
                basins = BasinInfo.GlobalCDA.GermanFrenchBasin_Entire()
            else:
                basins = BasinInfo.GlobalCDA.GermanFrenchBasin_Level0()

            if basin_names:
                excluded_basins += list(set(basins.keys()) - set(basin_names))
                
            for b in excluded_basins:
                try: t = basins.pop(b)
                except: pass

            station_data = []
            curr_id = 0
            for k, v in basins.items():
                row = []
                if int(v['station_id']) < 0: 
                    curr_id += 1
                    row.append('%d'%curr_id)
                else: row.append(v['station_id'])

                row.append(v['lon'])
                row.append(v['lat'])
                
                station_data.append(row)

            succeed = Station.write_stations(
                stations=station_data, 
                filename=filename_out
            )

            return succeed