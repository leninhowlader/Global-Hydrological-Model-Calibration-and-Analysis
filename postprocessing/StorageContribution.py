__author__ = 'mhasan'

import sys, shapefile as shp, os
sys.path.append('..')
from calibration.configuration import Configuration
from calibration.watergap import WaterGAP
from calibration.stats import stats
from copy import deepcopy
from utilities.grid import grid

#temporarily
from calibration.variable import SimVariable

config_filename = 'ganges_configuration_km3.txt'
total_storage_variable_name = 'TOTAL_STORAGE'
filename_postfix = 'ganges_optimum'

def main():
    global config_filename, total_storage_variable_name, filename_postfix

    config = Configuration.read_configuration_file(config_filename)

    succeed = False
    if config and config.is_okay() and WaterGAP.is_okay(): succeed = True

    var_list = config.sim_variables
    # it is required that the zone flag (group_start) for all sim. variables must be False. check if this condition is met
    if succeed:
        print('checking and correcting zone flag...', end='', flush=True)
        for var in var_list:
            if var.group_stats: var.group_stats = False
        print('[done]')

    # it is required that cell list in each variable must be the same. check if this condition is met
    if succeed:
        print('checking cell list size...', end='', flush=True)
        cset = set()
        ncell = 0
        for var in var_list:
            clist = []
            for group in var.cell_groups:
                for c in group:
                    if c not in clist: clist.append(c)
            var.clist = set(clist)

            if len(var.clist) > ncell: ncell = len(clist)

        for i in reversed(range(len(var_list))):
            var = var_list[i]
            if len(var.clist) != ncell: var_list.pop(i)
            else: var.clist = None

        if len(var_list) > 0: print('[okay]')
        else:
            succeed = False
            print('[not okay]')

    if succeed:
        print('reading model predictions ...', end='', flush=True)
        succeed = WaterGAP.read_predictions(config.sim_variables, WaterGAP.dir_info.output_directory)
        if succeed: print('[done]')
        else: print('[failed]')

    #var_list = deepcopy(config.sim_variables)


    # compute the total water storage yearly amplitudes and mean amplitude
    twsa, clist = {}, []
    years = list(range(WaterGAP.start_year, WaterGAP.end_year + 1))
    if succeed:
        print('computing annual and mean annual amplitudes...\n\tTotal Water Storage...', end='', flush=True)
        var = None
        for i in range(len(var_list)):
            if var_list[i].varname == total_storage_variable_name:
                var = var_list[i]
                var_list.pop(i)
                break
        if not var: succeed = False
        else:
            clist = []
            if var.cell_groups:
                for group in var.cell_groups:
                    for c in group:
                        if c not in clist: clist.append(c)
            else: clist = list(range(1, WaterGAP.get_grid_cell_count()+1))

            if not clist: succeed = False
            else:
                try:
                    clist.sort()
                    for year in years:
                        for c in clist:
                            d = var.data_cloud.crop([0, 1], [c, year])
                            s = stats.multiple_statistics(d, functions=['range'])
                            try: twsa[year].append(s[0])
                            except: twsa[year] = [s[0]]

                    # calculate the average amplitude for each cell over years
                    try:
                        d = []
                        for year in years: d.append(twsa[year])
                        twsa['mean'] = stats.column_statistics(d, function='mean')
                        twsa['cls'] = clist
                    except: pass
                except: succeed = False
        if succeed: print('[done]')
        else: print('[failed]')
    # calculate the yearly amplitudes and mean annual amplitude for other sim. vairalbes
    amp_data = {}
    if succeed:
        for var in var_list:
            print('\t' + var.varname + '...', end='', flush=True)
            temp = {}
            clist = []
            for group in var.cell_groups:
                for c in group: clist.append(c)
            if not clist: clist = list(range(1, WaterGAP.get_grid_cell_count()+1))
            try:
                clist.sort()
                for year in years:
                    for c in clist:
                        d = var.data_cloud.crop([0, 1], [c, year])
                        s = stats.multiple_statistics(d, functions=['range'])
                        try: temp[year].append(s[0])
                        except: temp[year] = [s[0]]

                # calculate mean annual amplitude
                try:
                    d = []
                    for year in years: d.append(temp[year])
                    temp['mean'] = stats.column_statistics(d, function='mean')
                except: pass
            except:
                succeed = False
                print('[failed]')

            amp_data[var.varname] = temp
            succeed = True
            print('[done]')

    # calculate the contribution of each variable to the total water storage amplitude
    ratios = {}
    if succeed:
        print('calutaling the contributions ...', end='', flush=True)
        for varname in amp_data.keys():
            try:
                var_ratio = {}
                var_data = amp_data[varname]
                for year in years: var_ratio[year] = stats.ratio(var_data[year], twsa[year])
                var_ratio['mean'] = stats.ratio(var_data['mean'], twsa['mean'])
                ratios[varname] = var_ratio
            except: succeed = False

        if not ratios:
            succeed = False
            print('[failed]')
        else: print('[done]')



    # make shape file for each variable
    if succeed:
        print('creating output files (.shp):')
        vars = ratios.keys()
        for var in vars:
            print('\tproducing shape file for ' + var + '...', end='', flush=True)
            g = shp.Writer(shp.POLYGON)
            g.autoBalance = 1  # ensures gemoetry and attributes match
            g.field('CLID', 'N', 8)

            years = []

            for year in range(WaterGAP.start_year, WaterGAP.end_year+1):
                g.field(str(year), 'N', 27,19)
                years.append(year)

            g.field('mean', 'N', 27, 19)
            years.append('mean')


            clist = twsa['cls']
            for i in range(len(clist)):
                # draw cell
                centroid = grid.map_centroid_from_wghm_cell_number(clist[i])
                vertices = grid.cell_vertices([centroid], degree_resolution=0.5)


                g.poly(parts=vertices, shapeType=shp.POLYGON)

                # insert records for the cell
                records = [clist[i]]
                for year in years:
                    try: records.append(ratios[var][year][i])
                    except: records.append(0.0)
                try:records.append(ratios[var]['mean'][i])
                except: records.append(0.0)
                g.record(*records)

            # save shape into a file (.shp format)
            filename = os.path.join('output', var.lower() + '_' + filename_postfix + '.shp')
            g.save(filename)

            if not os.path.exists(filename):
                succeed = False
                print('[failed]')
            else:
                print('[done]')

                print('\tcreating projection file (.prj) for ' + var + '...', end='', flush=True)
                # create a spatial reference file
                filename = os.path.join('output', var.lower() + '_' + filename_postfix + '.prj')
                f = None
                try:
                    f = open(filename, 'w')
                    prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                    f.write(prj_string)
                    succeed = True
                    print('[done]')
                except:
                    succeed = False
                    print('[failed]')
                finally:
                    try: f.close()
                    except: pass

    if succeed:
        print('creating yearly and mean output files (.shp)')
        vars = ratios.keys()
        years = list(range(WaterGAP.start_year, WaterGAP.end_year+1)) + ['mean']
        clist = twsa['cls']

        for year in years:
            print('\tproducing output for ' + str(year) + '...', end='', flush=True)
            g = shp.Writer(shp.POLYGON)
            g.autoBalance = 1  # ensures gemoetry and attributes match
            g.field('CLID', 'N', 8)

            for var in vars: g.field(var, 'N', 27,19)


            for i in range(len(clist)):
                # draw cell
                centroid = grid.map_centroid_from_wghm_cell_number(clist[i])
                vertices = grid.cell_vertices([centroid], degree_resolution=0.5)


                g.poly(parts=vertices, shapeType=shp.POLYGON)

                # insert records for the cell
                records = [clist[i]]
                for var in vars:
                    try: records.append(ratios[var][year][i])
                    except: records.append(0.0)
                g.record(*records)

            # save shape into a file (.shp format)
            filename = os.path.join('output', filename_postfix + '_' + str(year).lower() + '.shp')
            g.save(filename)
            if not os.path.exists(filename):
                succeed = False
                print('[failed]')
            else:
                print('[done]')
                print('\tcreating project file (.prj)...', end='', flush=True)
                # create a spatial reference file
                filename = os.path.join('output', filename_postfix + '_' + str(year).lower() + '.prj')
                f = None
                try:
                    f = open(filename, 'w')
                    prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                    f.write(prj_string)
                    succeed = True
                    print('[done]')
                except:
                    succeed = False
                    print('[failed]')
                finally:
                    try: f.close()
                    except: pass
    if succeed: print('Program ends with success!!\nThank you for using this program.')
    else: print('Program was not successful.\nPlease check the inputs and try later. Thank you.')

if __name__ == '__main__':
    main()