import os, math, sys
sys.path.append('..')
from utilities.fileio import read_flat_file, write_flat_file
from utilities.grid import grid


basin_extent_filename = ''#''extent_papa_etal.dat'
data_directory = '/media/sf_mhasan/private/new_data_from_fabrice_papa/Surface_Volumes'
upstream_filename = 'brahmaputra_upstream.txt'
cell_area_filename = ''# 'ganges_area.txt'
output_datafile = 'brahmaputra_sws_km3_papa_etal_2015.csv'
output_subbasin_filename = 'sub_basin_brahmaputra.txt'
output_shapefile = 'papa_etal_2015.shp'
calculate_basin_total = True
basin_id = 1
unit_conversion_factor = 1
grid_selection_method = 1

def read_data(data_directory):
    data = {}  # structure: {(yr, mon): [data], ..}

    if not data_directory: return data
    flist = [f for f in os.listdir(data_directory) if os.path.isfile(os.path.join(data_directory, f))]

    year, month = 0, 0
    for filename in flist:
        try:
            year = int(filename[-8:-4])
            month = int(filename[-11:-9])
        except: break

        filename = os.path.join(data_directory, filename)
        h, d = read_flat_file(filename, separator=' ', header=False, skiplines=0)
        for i in reversed(range(len(d))):
            if math.isnan(d[i][2]): d.pop(i)
            # else: d[i] = [year, month] + d[i]
        data[(year, month)] = d

    return data

def find_extent(data):
    coords = []
    for k, v in data.items(): # python-2x: data.items(); python-3x: data.iteritems()
        for d in v:
            if (d[1], d[0]) not in coords: coords.append((d[1], d[0]))
    return coords

def read_upstream_file(filename): return grid.read_groupfile(filename)

def read_upstream_area(filename): return grid.read_groupfile(filename, data_type='float')

def read_basin_extent(filename):
    h, d = read_flat_file(filename, separator=',', header=True)

    if d:
        for i in range(len(d)): d[i] = (d[i][1], d[i][0])

    return d

def main():
    global basin_extent_filename, data_directory, upstream_filename, calculate_basin_total, basin_id
    global output_datafile, output_subbasin_filename, cell_area_filename, unit_conversion_factor
    global grid_selection_method

    msgs = []   # messages

    # step-01: check inputs
    print('Checking input ...'.ljust(50, ' '), end='', flush=True)
    if not data_directory:
        print('[not okay]\n\tData directory was not provided. [Input Error]')
        exit(-101)
    elif not upstream_filename:
        print('[not okay]\n\tWGHM upstream file was not provided. [Input Error]')
        exit(-102)
    elif not output_datafile:
        print('[not okay]\n\tOutput config_filename was not provided. [Input Error]')
        exit(-103)
    print('[okay]')

    # step-02: read data from input files
    # read upstream cells
    print('Reading data (Papa et al 2015)..'.ljust(50, ' '), end='', flush=True)
    upc = read_upstream_file(upstream_filename)
    if not upc:
        print('[not okay]\n\tWGHM upstream cannot be read. Please check the config_filename. [Data Error]')
        exit(-201)

    if len(upc) > 1: upc = upc[0]

    # read papa_etal data from data directory
    data = read_data(data_directory)
    if not data:
        print('[not okay]\n\tData could not be read. Please check if the directory is empty. [Data Error]')
        exit(-202)
    print('[done]')

    # read extent of data (papa et al 2015)
    print('Reading data-extent (Papa et al. 2015) ..'.ljust(50, ' '), end='', flush=True)
    papa_etal_extent = []
    if basin_extent_filename: papa_etal_extent = read_basin_extent(basin_extent_filename)

    if not papa_etal_extent:
        papa_etal_extent = find_extent(data)

        if not papa_etal_extent:
            print('Basin extent (Papa et al. 2015) could not be generated. [Data Error]')
            exit(-203)
        else:
            write_flat_file(basin_extent_filename, papa_etal_extent)

    print('[done]')

    # read area of 0.5 deg basin cells
    area_050deg = []
    if cell_area_filename:
        print('Reading 0.5 deg grid cell area..'.ljust(50, ' '), end='', flush=True)
        area_050deg = read_upstream_area(cell_area_filename)[0]
        if not area_050deg: print('[not successful]\n\tWarning: SWS will be generated in volume units.')
        else: print('[done]')

    # step-03: select wghm cells for which SWS can be reconstructed using Papa et al. 2015 dataset
    # find upstream cell centroids
    print('Selection of WGHM sub-basin..'.ljust(50, ' '), end='', flush=True)
    centroid_upc = [] # upstream cell centroids
    for c in upc[0]: centroid_upc.append(grid.map_centroid_from_wghm_cell_number(c))

    # select (wghm) cell centroids for which data can be reconstructed
    slc = {}  # selected cells = {centroids: [corresponding papa_etal_2015 cells], ...}
    for centroid in centroid_upc:
        lat, lng = centroid[0], centroid[1]
        if grid_selection_method == 1:
            peripheral_points = [(lat-0.25, lng-0.25), (lat, lng-0.25), (lat+0.25, lng-0.25), (lat+0.25, lng),
                                 (lat+0.25, lng+0.25), (lat, lng+0.25), (lat-0.25, lng+0.25), (lat-0.25, lng),
                                 (lat, lng)]
        else: peripheral_points = [(lat, lng), (lat, lng-0.25), (lat+0.25, lng-0.25), (lat+0.25, lng)]


        for pf in peripheral_points:
            if pf not in papa_etal_extent: break
        else: slc[centroid] = peripheral_points

    if not slc:
        print('[not okay]\n\tSWS cannot be reconstructed. No cell has been selected.')
        return 0
    print('[done]')


    # step-04: reconstruct data for selected cells using Papa et al. 2015 dataset
    print('Reconstruction of Papa et al. 2015 data..'.ljust(50, ' '), end='', flush=True)
    if grid_selection_method == 1:
        # weights or share of 0.25 deg peripheral cells in 0.5 deg wghm cell
        # note that the central 0.25 deg cell should has complete participation
        wts = [0.25, 0.5, 0.25, 0.5, 0.25, 0.5, 0.25, 0.5, 1.0]
    else: wts = [1.0, 1.0, 1.0, 1.0]
    sws_data = {}       # sws_data (= surface water storage data): {timestamp: {cell: sws, ..}, ...}

    for t, t_data in data.items(): # python-2x: data.items(); python-3x: data.iteritems()
        # t = time stamp; t_data = data at t

        c_sws = {}  # sws for all cells for sepecific time stamp (year, month); structure: {cell: sws, ...}

        for c, p in slc.items():  # python-2x: slc.items(); python-3x: slc.iteritems()
            # c = centroid, p = peripheral points
            sws = 0.0

            for d in t_data:
                cell_025 = (d[1], d[0])
                if cell_025 == c: sws += d[2]
                elif cell_025 in p: sws += d[2] * wts[p.index(cell_025)]

            c_sws[c] = sws

        sws_data[t] = c_sws

    if not sws_data:
        print('[not okay]\n\t Data reconstruction was not successful.')
        exit(-401)
    print('[done]')

    # step-05: calculate basin sum if demanded and organize output data
    print('Organize data for printing..'.ljust(50, ' '), end='', flush=True)
    headers_out, data_out = [], []
    if calculate_basin_total:
        # calculate the area of the sub-basin
        area = 0.0
        if len(area_050deg) == len(centroid_upc):
            for k in slc.keys(): area += area_050deg[centroid_upc.index(k)]

        if area > 0: msgs.append('Output has been produced in water height units. Sub-basin area was found %0.3f.' %area)
        else: msgs.append('Output has been produced in water volume units.')

        for t, c_sws in sws_data.items():   # python-2x: sws_data.items(); python-3x: sws_data.iteritems()
            bsum = 0
            for c, sws in c_sws.items():    # python-2x: c_sws.items(); python-3x: c_sws.iteritems()
                bsum += sws
            # sws_data[t] = bsum
            if area > 0: bsum /= area
            data_out.append([basin_id, t[0], t[1], bsum])

        headers_out = ['basin', 'year', 'month', 'sws']
    else:
        if len(area_050deg) == len(centroid_upc):
            msgs.append('Output has been produced in water height units.')

            for t, c_sws in sws_data.items():   # python-2x: sws_data.items(); python-3x: sws_data.iteritems()
                for c, sws in c_sws.items():  # python-2x: c_sws.items(); python-3x: c_sws.iteritems()
                    area = area_050deg[centroid_upc.index(c)]
                    data_out.append([c[1], c[0], t[0], t[1], sws/area])
        else:
            msgs.append('Output has been produced in water volume units.')

            for t, c_sws in sws_data.items():   # python-2x: sws_data.items(); python-3x: sws_data.iteritems()
                for c, sws in c_sws.items():  # python-2x: c_sws.items(); python-3x: c_sws.iteritems()
                    data_out.append([c[1], c[0], t[0], t[1], sws])
        headers_out = ['long', 'lat', 'year', 'month', 'sws']
    print('[done]')

    # unit conversion
    if data_out and unit_conversion_factor != 1:
        print('Changing units..'.ljust(50, ' '), end='', flush=True)
        msgs.append('Unit conversion was applied at the very end. Make sure the conversion factor is correct. %0.3f was used as conversion factor.' %unit_conversion_factor)

        ndx = len(data_out[0]) - 1
        for i in range(len(data_out)): data_out[i][ndx] *= unit_conversion_factor
        print('[done]')

    # step-06: write data into output files
    # writing datafile
    print('Printing data into output file..'.ljust(50, ' '), end='', flush=True)
    data_out.sort()
    write_flat_file(output_datafile, data_out, data_headers=headers_out, separator=',')

    # writing sub-basin cells
    if output_subbasin_filename:
        sub_basin = []
        sub_basin_area = []
        for c in slc.keys():
            row, col = grid.find_row_column(c[0], c[1])
            sub_basin.append(grid.map_wghm_cell_number(row, col))
            sub_basin_area.append(grid.find_wghm_cellarea(row))

        grid.write_groupfile(output_subbasin_filename, [sub_basin])
        grid.write_groupfile('sub_basin_area.txt', [sub_basin_area])
    print('[done]')

    if msgs:
        print('\nNotes :')
        for i in range(len(msgs)): print('\t(%d) %s' %(i+1, msgs[i]))

    print('\nThe program is being terminated with success.\nThank you for using this program.')

main()
