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

config_filename = 'ganges_configuration_km3_test.txt'
total_storage_variable_name = 'TOTAL_STORAGE'

def main():
    global config_filename, total_storage_variable_name

    config = Configuration.read_configuration_file(config_filename)

    succeed = False
    if config and config.is_okay() and WaterGAP.is_okay(): succeed = True

    if succeed: succeed = WaterGAP.read_predictions(config.sim_variables, WaterGAP.dir_info.output_directory)

    var_list = deepcopy(config.sim_variables)

    # it is required that the zone flag (group_start) for all sim. variables must be False. check if this condition is met
    for var in var_list:
        if var.group_stats:
            succeed = False
            break

    # it is required that cell list in each variable must be the same. check if this condition is met
    cset = set()
    for var in var_list:
        clist = []
        for group in var.cell_groups:
            for c in group:
                if c not in clist: clist.append(c)
        clist = set(clist)

        if not cset: cset = clist
        elif cset != clist:
            succeed = False
            break

    # compute the total water storage yearly amplitudes and mean amplitude
    twsa, clist = {}, []
    years = list(range(WaterGAP.start_year, WaterGAP.end_year + 1))
    if succeed:
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

    # calculate the yearly amplitudes and mean annual amplitude for other sim. vairalbes
    amp_data = {}
    if succeed:
        for var in var_list:
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
            except: succeed = False
            amp_data[var.varname] = temp

    # calculate the contribution of each variable to the total water storage amplitude
    ratios = {}
    if succeed:
        for varname in amp_data.keys():
            try:
                var_ratio = {}
                var_data = amp_data[varname]
                for year in years: var_ratio[year] = stats.ratio(var_data[year], twsa[year])
                var_ratio['mean'] = stats.ratio(var_data['mean'], twsa['mean'])
                ratios[varname] = var_ratio
            except: succeed = False

        if not ratios: succeed = False

    succeed = True
    # make shape file for each variable
    if succeed:
        clist = twsa['cls']
        centroids = []
        for c in clist: centroids.append(grid.map_centroid_from_wghm_cell_number(c))
        vertices = grid.cell_vertices(centroids, degree_resolution=0.5)

        g = shp.Writer(shp.POLYGON)
        g.field('CLID', 'N', 8)
        for i in range(len(vertices)):
            g.poly(parts=[vertices[i]], shapeType=shp.POLYGON)
            g.record(clist[i])
        g.save('basin_test.shp')
        # for varname in ratios.keys():
        #     filename = os.path.join('output', varname.lower() + '.shp')





    print(succeed)


if __name__ == '__main__':
    main()