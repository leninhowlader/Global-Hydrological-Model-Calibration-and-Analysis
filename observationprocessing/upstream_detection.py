#!/usr/bin/python3

# Author: H.M. Mehedi Hasan
# Date: May 2016
#
# This program can finds the upstream cells for given geo-locations using the 0.5 degree flow-direction data set. The
# flow-direction datafile must have the same structure as the direction file used in WaterGAP model program.  The
# output upstream cells can either be represented as centroid coordinates or as WGHM cell number. If cells are to be
# represented as WGHM cell numbers, a mapping data file is required.
#
# The 0.5-degree upstream cells can be grouped according to 1.0-degree grid cells. In this case the grouping flag must
# set 'True'.
#
# The areas of the upstream cells can also be produced as output if the corresponding flag is set 'True'. However, for
# finding area, a data-file is area datafile is required. This area mapping file must have similar structure as the area
# file used in WaterGAP model.
#
# Output can be printed on screen on in files. In case of printing output in files, user must set the 'on screen output'
# flag 'False'. The output of upstream cells and area of cells will be printed in separate files.
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

# 1. CONTROL VARIABLES: DEFINITION AND VALUES
flow_direction_file = ''# 'flow-direction.asc'      # flow-direction file
stations = []#, (26.25, 91.75), (27.25, 92.75)]                                       # geo-coordinates of the stations (see note 2.1)
station_file = 'input/STATIONS_BRH.DAT'                       # name of the station file from where stations can be read in (see note 2.2)
make_1deg_group = False                             # a flag determines if the result cells would be grouped (see note 2.3)
output_as_wghm_cellnum = True                       # a flag determines if the output cell will be represented as wghm cell number (see note 2.4)
wghm_cell_number_mapping_datafile = ''              # 'wghm_grid.csv' # cell number mapping file (see note 2.4)
output_cell_area = True                             # a flag determines if the area of associated will be printed in output (see note 2.5)
area_mapping_datafile = ''#''GAREA.UNF0'            # datafile for mapping wghm cell area (see note 2.5)
show_output_on_screen = False                       # a flag determines if the results will be printed on screen or in file(s) (see note 2.6)
create_station_wise_output_file = False
output_file_upstream = 'output/ganges_upstreams_hardinge_bridge.txt'               # output file for upstream cells (see note 2.6)
output_file_area = 'output/ganges_areas_hardinge_bridge.txt'                       # output file for cell area (see note 2.6)

# 2. CONTROL VARIABLE: NOTES
# 2.1 stations
# The geo-location of the stations must be provided either as python-lists e.g. [ -21.75, 44.25 ] or as python-tuples e.g.
# ( -21.75, 44.25 ) and they shall be comma separated. In either case, latitude must be the first element followed by
# longitude.
# example: stations = [ ( -21.75, 44.25 ) , ( -17.25 47.25 ) ]
#
# 2.2 station_file
# Station file will only be used if stations are not given. Station file must follow the same format as the WGHM station
# file. Both absolute or relative path can be used for station file. In case of relative path the path must be relative to
# the home directory of this program. NOTE THAT UNDER LINUX ENVIRONMENT PATH IS CASE SENSITIVE.
# example: station_file = '../WaterGAP/control/STATIONS.DAT'
#
# 2.3 make_1deg_group
# If the flag is set 'True', upstream cells will be grouped according to their positions in 1-degree grid cells.
#
# 2.4 output_as_wghm_cellnum and wghm_cell_number_mapping_datafile
# The output_as_wghm_cellnum flag determines if the output is written as WGHM cells or not. If the flag is set 'False',
# the cells will be represented by the centroid coordinates; the latitude comes first in the representation. If the flag
# is set 'True', wghm cell numbers will be written as output. Finding cell numbers required mapping data which
# must be specified in the mapping datafile name. However, if datafile name is not provided, the program will try to read
# the file from the default mapping datafile. If the default datafile does not exist, an empty result-set will be
# produced.
#
# 2.5 output_cell_area and area_mapping_datafile
# output_cell_area is a flag that determines whether or not the area of upstream cells will be printed as output. If
# this flag is set 'True', a datafile is required for finding area of a given upstream cell. The datafile can be
# specified in area_mapping_datafile variable. However, if the mapping file is not provided, the program will try
# to load the mapping data from a default file i.e. 'GAREA.UNF0' and the default file must be present in the home
# directory of this program
#
# 2.6 show_output_on_screen, output_file_upstream, output_file_area
# If the show_output_on_screen flag is set 'True', output will only be printed on the screen; otherwise, output will be
# written in files specified in output_file_upstream and output_file_area. Cell area will only be calculated when
# output_cell_area (see note 2.5) is set 'True', thus output_file_area is only effective the former is set ON ('True').



#---------------------------:) DO NOT CHANGE ANYTHING BELOW IF YOU ARE NOT CONFIDENT :)----------------------------------#


# IMPORT STATEMENTS
import os, sys
sys.path.append('..')
from utilities.globalgrid import GlobalGrid
from utilities.fileio import FileInputOutput as io
from utilities.upstream import Upstream


# STATIC VARIABLES
# flow_direction_data = []
# directions = [1, 2, 4, 8, 16, 32, 64, 128]


# setting wghm cell-number and area mapping data files, if applicable
if output_as_wghm_cellnum and wghm_cell_number_mapping_datafile:
    GlobalGrid.__wghm_grid_lookup_table_filename = wghm_cell_number_mapping_datafile

if output_cell_area and area_mapping_datafile: GlobalGrid.__wghm_cell_area_file = area_mapping_datafile

# method of reading flow-direction data
# def read_flow_data():
#     global flow_direction_data, flow_direction_file
#     headers, month_data = read_flat_file(flow_direction_file, skiplines=6)
#     if month_data: flow_direction_data = month_data
#     else:
#         message = 'Flow direction data could not be retrieved. Either "%s" does not exists or has bad-format.'%flow_direction_file
#         print(message)
#         exit(os.EX_NOINPUT)

# method of finding flow-direction for a given cell
# def get_flow_direction(row, col):
#     global flow_direction_data
#     if not flow_direction_data: read_flow_data()
#
#     return flow_direction_data[row][col]

# method of finding if a give cell is a upstream cell for another reference cell;
# the reference cell is referred as direction from the given cell
# def is_upstream(row, col, direction):
#     val = get_flow_direction(row, col)
#     if val == direction: return True
#     else: return False

# method of finding neighboring cell towards a given direction from a given cell
# def get_cell_indices(row, col, direction):
#     if direction == 1: return row, col-1
#     elif direction == 2: return row-1, col-1
#     elif direction == 4: return row-1, col
#     elif direction == 8: return row-1, col+1
#     elif direction == 16: return row, col+1
#     elif direction == 32: return row+1, col+1
#     elif direction == 64: return row+1, col
#     else: return row+1, col-1

# method of finding the neighboring cells of a given cell in all directions
# def get_adjacent_cells(row, col):
#     global directions
#
#     cells = []
#     for d in directions: cells.append(get_cell_indices(row, col, d))
#
#     return cells

# method of finding the upstream cells of a given cell
# def get_upstream_cells(row, col):
#     global directions
#
#     list_out = []
#     adj_cells = get_adjacent_cells(row, col)
#     for i in range(len(adj_cells)):
#         row = adj_cells[i][0]
#         col = adj_cells[i][1]
#         direction = directions[i]
#         if is_upstream(row, col, direction):
#             list_out.append((row, col))
#             month_data = get_upstream_cells(row, col)
#             if month_data: list_out = list_out + month_data
#
#     return list_out

# method of finding stations from the station file
def find_stations_from_file(station_file):
    headers, records = io.read_flat_file(station_file, separator=' ', header=False)

    stations = []
    if records:
        for record in records:
            if len(record) >= 3 and -90<=record[2]<=90 and -180<=record[1]<=180:
                stations.append((record[2], record[1], record[0]))

    return stations

# the main method
def main():
    global flow_direction_data, directions, stations, station_file, make_1deg_group, output_as_wghm_cellnum
    global output_cell_area, show_output_on_screen, output_file_area, output_file_upstream

    # check if the stations' coordinates (if given) are valid. if not, remove the invalid station
    if stations:
        for j in reversed(range(len(stations))):
            if (len(stations[j]) != 2) or not (-90<=stations[j][0]<=90) or not (-180<=stations[j][1]<=180):
                stations.pop(j)

    # if stations are not provided or they are removed during earlier process, find stations from station file
    if not stations: stations = find_stations_from_file(station_file)

    # if station list is still empty, exit with error message
    if not stations:
        message = '(Error) No geo-location is found to proceed.'
        print(message)
        exit(os.EX_NOINPUT)

    if not show_output_on_screen:
        if not output_file_upstream:
            message = 'Output file for upstream cells has not been provided. Please check input control variables.'
            print(message)
            exit(os.EX_NOINPUT)

        if output_cell_area and not output_file_area:
            message = 'Output file for cell area is required but not provided. Please check input control variables.'
            print(message)
            exit(os.EX_NOINPUT)

    # for each station find the upstream cells
    upstream_cells = []
    for station in stations:
        row, col = GlobalGrid.find_row_column(station[0], station[1], degree_resolution=0.5)
        up_cells = Upstream.get_upstream_cells(row, col)

        # add the base station to the list
        up_cells = [(row, col)] + up_cells

        # add the upstream cells to the list
        if up_cells: upstream_cells.append(up_cells)

    # if upstream cells were found
    if upstream_cells:

        # EXTRA PRECAUTION
        # delete_ndx duplicate upstream sells
        for i in range(len(upstream_cells)):
            for j in reversed(range(1, len(upstream_cells[i]))):
                for k in range(j):
                    if upstream_cells[i][j] == upstream_cells[i][k]:
                        upstream_cells[i].pop(j)
                        break

        # apply grouping only if group flag (make_1deg_group) is set true
        one_deg_groups = []
        if make_1deg_group:
            for i in range(len(upstream_cells)): one_deg_groups.append(GlobalGrid.cell_grouping(upstream_cells[i]))


        # find cell area if the corresponding flag is set on
        area_groups, area_lst = [], []
        if output_cell_area:
            # find cell area for group members of all groups, if grouping was done
            if one_deg_groups:
                for i in range(len(one_deg_groups)):
                    area_groups.append([])
                    for group in one_deg_groups[i]:
                        area_lst = []
                        for cell in group:
                            area = GlobalGrid.find_wghm_cellarea(cell[0])
                            if area: area_lst.append(area)
                        if area_lst: area_groups[i].append(area_lst)
                area_lst = []
            # else find area for all upstream cells
            else:
                for i in range(len(upstream_cells)):
                    temp = []
                    for cell in upstream_cells[i]:
                        area = GlobalGrid.find_wghm_cellarea(cell[0])
                        if area: temp.append(area)
                    area_lst.append(temp)

        # find wghm cell number of each cell
        if output_as_wghm_cellnum:
            # if groups are created, find cell numbers for all members of all groups
            if one_deg_groups:
                for i in range(len(one_deg_groups)):
                    for j in range(len(one_deg_groups[i])):
                        cnum_lst = []
                        for cell in one_deg_groups[i][j]:
                            cnum = GlobalGrid.get_wghm_cell_number(cell[0], cell[1], base_resolution=0.5)
                            if cnum: cnum_lst.append(cnum)
                        one_deg_groups[i][j] = cnum_lst

            # find wghm cell numbers for all upstream cells
            for i in range(len(upstream_cells)):
                for j in range(len(upstream_cells[i])):
                    cnum = GlobalGrid.get_wghm_cell_number(upstream_cells[i][j][0], upstream_cells[i][j][1], base_resolution=0.5)
                    upstream_cells[i][j] = cnum
        # if cell are not to be represented as wghm cell numbers, find cell centroids
        else:
            if one_deg_groups:
                for i in range(len(one_deg_groups)):
                    for j in range(len(one_deg_groups[i])):
                        temp = []
                        for k in range(len(one_deg_groups[i][j])):
                            lat, long = GlobalGrid.find_centroid(one_deg_groups[i][j][k][0], one_deg_groups[i][j][k][1], deg_resolution=0.5)
                            temp.append((lat, long))
                        one_deg_groups[i][j] = temp
            for i in range(len(upstream_cells)):
                for j in range(len(upstream_cells[i])):
                    lat, long = GlobalGrid.find_centroid(upstream_cells[i][j][0], upstream_cells[i][j][1], deg_resolution=0.5)
                    upstream_cells[i][j] = (lat, long)

        # print on screen if the corresponding flag is set on
        if show_output_on_screen:
            print('outputs:')
            if not one_deg_groups:
                print('upstream cells:')
                if output_as_wghm_cellnum:
                    for i in range(len(upstream_cells)):
                        print('\t(station %d at %f %f)' %(i, stations[i][0], stations[i][1]))
                        line = '\t'
                        for j in range(len(upstream_cells[i])):
                            line += str(upstream_cells[i][j]).rjust(8)
                            if (j+1)%20 == 0:
                                print(line)
                                line = '\t'
                        if line != '\t': print(line)
                else:
                    for i in range(len(upstream_cells)):
                        print('\t(station %d at %f %f)' % (i, stations[i][0], stations[i][1]))
                        line = '\t'
                        for j in range(len(upstream_cells[i])):
                            line += '(' + ' , '.join(str(x) for x in upstream_cells[i][j]) + ') '
                            if (j+1)%10 == 0:
                                print(line)
                                line = '\t'
                        if line != '\t': print(line)

            else:
                print('upstream cell groups:')
                if output_as_wghm_cellnum:
                    for i in range(len(one_deg_groups)):
                        print('\t(station %d at %f %f)' % (i, stations[i][0], stations[i][1]))
                        for j in range(len(one_deg_groups[i])):
                            line = '\tGroup-' + str(j+1).rjust(5, '0') + ': ' + ' '.join(str(x) for x in one_deg_groups[i][j])
                            print(line)
                else:
                    for i in range(len(one_deg_groups)):
                        print('\t(station %d at %f %f)' % (i, stations[i][0], stations[i][1]))
                        for j in range(len(one_deg_groups[i])):
                            line = '\tGroup-' + str(j+1).rjust(5, '0')
                            for k in range(len(one_deg_groups[i][j])):
                                line += ' (' + ' , '.join(str(x) for x in one_deg_groups[i][j][k]) + ')'
                            print(line)

            if output_cell_area:
                if one_deg_groups:
                    print('Cell-areas in groups:')
                    for i in range(len(area_groups)):
                        print('\t(station %d at %f %f)' % (i, stations[i][0], stations[i][1]))
                        for j in range(len(area_groups[i])):
                            line = '\tGroup-' + str(j+1).rjust(5, '0') + ': ' + ''.join('{:0.6f}'.format(x).rjust(13) for x in area_groups[i][j])
                            print(line)
                else:
                    print('Cell-areas:')
                    for i in range(len(area_lst)):
                        print('\t(station %d at %f %f)' % (i, stations[i][0], stations[i][1]))
                        line = '\t'
                        for j in range(len(area_lst[i])):
                            line += '{:0.6f}'.format(area_lst[i][j]).rjust(14)
                            if (j+1)%10 == 0:
                                print(line)
                                line = '\t'
                        if line != '\t': print(line)

        # else write output files
        else:
            # if output_as_wghm_cellnum:
            succeed = False
            if create_station_wise_output_file:
                for i in range(len(stations)):
                    filename = output_file_upstream[:-4] + '_' + str(stations[i][2]) + '.txt'

                    if one_deg_groups:
                        succeed = GlobalGrid.write_cell_info(filename, one_deg_groups[i])
                    else:
                        succeed = GlobalGrid.write_cell_info(filename, [upstream_cells[i]])

                    if not succeed: break
            else:
                for i in range(len(stations)):
                    if one_deg_groups:
                        succeed = GlobalGrid.write_cell_info(output_file_upstream, one_deg_groups[i], mode='a')
                    else:
                        succeed = GlobalGrid.write_cell_info(output_file_upstream, [upstream_cells[i]], mode='a')

                    if not succeed: break

            message = ''
            if succeed: message = 'Upstream cells have been saved successfully in ' + output_file_upstream
            else: message = 'Upstream cells could not be saved.'
            print(message)


            if output_cell_area:
                succeed = False
                if create_station_wise_output_file:
                    for i in range(len(stations)):
                        filename = output_file_area[:-4] + '_' + str(stations[i][2]) + '.txt'
                        if one_deg_groups: succeed = GlobalGrid.write_cell_info(filename, area_groups[i])
                        else: succeed = GlobalGrid.write_cell_info(filename, [area_lst[i]])

                        if not succeed: break
                else:
                    for i in range(len(stations)):
                        if one_deg_groups: succeed = GlobalGrid.write_cell_info(output_file_area, area_groups[i], mode='a')
                        else: succeed = GlobalGrid.write_cell_info(output_file_area, [area_lst[i]], mode='a')

                        if not succeed: break
                message = ''
                if succeed: message = 'Cell areas have been saved successfully in ' + output_file_area
                else: message = 'Cell areas could not be saved.'
                print(message)
    else:
        message = 'No upstream cells were detected for the selected stations.'
        print(message)

    # exit successfully
    print('The program ends with success.')
    exit(os.EX_OK)
            
if __name__ == '__main__': main()