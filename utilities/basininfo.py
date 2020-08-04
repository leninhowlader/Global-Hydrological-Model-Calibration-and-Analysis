import sys, numpy as np
from collections import OrderedDict

sys.path.append('..')
from utilities.globalgrid import GlobalGrid as gg
from utilities.upstream import Upstream as up

class BasinInfo:
    class GlobalCDA:
        __model_version = 'wghm22d'
        __model_grid_resolution_deg = 0.5
        
        @staticmethod
        def set_model_version(model_version): 
            BasinInfo.GlobalCDA.__model_version = model_version

        @staticmethod
        def get_model_verson(): 
            return BasinInfo.GlobalCDA.__model_version
        
        @staticmethod
        def set_model_grid_resolution(resolution_deg):
            BasinInfo.GlobalCDA.__model_grid_resolution_deg = resolution_deg
        
        @staticmethod
        def get_model_grid_resolution():
            return BasinInfo.GlobalCDA.__model_grid_resolution_deg

        @staticmethod
        def GFBasin_level0(
            compute_upstream=False,
            wghm_cell_number=True,
            include_arcid=False,
            include_cellarea=False,
            include_only_basin_area=False
        ):
            basin_info = OrderedDict()
            basin_info['elbe'] = {
                'bid': 1, 'name': 'Elbe Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': 8.75, 'lat': 53.75,
                'cellnum': 22538
            }

            basin_info['weser'] = {
                'bid': 2, 'name': 'Weser Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': 8.25, 'lat': 53.75,
                'cellnum': 22537
            }

            basin_info['rhine'] = {
                'bid': 3, 'name': 'Rhine Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': 4.25, 'lat': 52.25,
                'cellnum': 23905
            }

            basin_info['meuse'] = {
                'bid': 4, 'name': 'Meuse Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': 3.75, 'lat': 51.75,
                'cellnum': 24363
            }

            basin_info['seine'] = {
                'bid': 5, 'name': 'Seine Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': 0.25, 'lat': 49.75,
                'cellnum': 26107
            }

            basin_info['rhone'] = {
                'bid': 6, 'name': 'Rhone Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': 4.75, 'lat': 43.25,
                'cellnum': 31405
            }

            basin_info['loire'] = {
                'bid': 7, 'name': 'Loire Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': -2.25, 'lat': 47.25,
                'cellnum': 28236
            }

            basin_info['vilaine'] = {
                'bid': 8, 'name': 'Vilaine Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': -2.25, 'lat': 47.75,
                'cellnum': 27826
            }

            basin_info['garonne'] = {
                'bid': 9, 'name': 'Garonne Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': -0.75, 'lat': 45.25,
                'cellnum': 29861
            }

            basin_info['adour'] = {
                'bid': 10, 'name': 'Adour Basin', 'acronym': 'NA',
                'station_id': '4127800', 'lon': -1.25, 'lat': 43.75,
                'cellnum': 31016
            }

            if include_cellarea or include_only_basin_area: compute_upstream = True

            if compute_upstream:
                BasinInfo.include_basin_property_upstream(
                    basin_info,
                    wghm_cell_number=wghm_cell_number
                )

            BasinInfo.GlobalCDA.include_basin_properties(
                basin_info,
                include_arcid=include_arcid,
                include_cellarea=include_cellarea,
                include_only_basin_area=include_only_basin_area
            )

            # [step] add basin outlet (WaterGAP) cell number
            is_available_outlet_cellnum = True
            for basin in basin_info.keys():
                if basin_info[basin]['cellnum'] == -1:
                    is_available_outlet_cellnum = False
                    break

            if (not is_available_outlet_cellnum):
                BasinInfo.GlobalCDA.include_basin_outlet_cellnumber(basin_info)
            # [end]

            return basin_info
        
        @staticmethod
        def Mississippi_level0(
            with_upstream=False,
            wghm_cell_number=True,
            include_arcid=False,
            include_cellarea=False,
            include_only_basin_area=False
        ):
            
            basin_info = OrderedDict()
            basin_info['mississippi'] = {
                'name': 'Mississippi River Basin', 'acronym': 'MRB (Unit-VI)',
                'station_id': '4127800', 'lon': -91.25, 'lat': 32.25,
                'cellnum': 38760
            }

            if include_cellarea or include_only_basin_area: with_upstream = True

            if with_upstream: 
                BasinInfo.include_basin_property_upstream(
                                            basin_info,
                                            wghm_cell_number=wghm_cell_number)
            
            BasinInfo.GlobalCDA.include_basin_properties(
                                basin_info,
                                include_arcid=include_arcid,
                                include_cellarea=include_cellarea,
                                include_only_basin_area=include_only_basin_area)
            
            return basin_info
        #end of function
        

        @staticmethod
        def Mississippi_level1(with_upstream=False, 
                               wghm_cell_number=True,
                               include_arcid=False, 
                               include_cellarea=False, 
                               include_only_basin_area=False):
            
            basin_info = OrderedDict()
            basin_info['fort_smith'] = {
                'name': 'Arkansas River Basin', 'acronym': 'Arkansas (Unit-I)',
                'station_id': '7249455', 'lon': -94.25, 'lat': 35.25,
                'cellnum': 36847
            }

            basin_info['hermann'] = {
                'name': 'Missouri River Basin', 'acronym': 'Missouri (Unit-II)',
                'station_id': '4122900', 'lon': -91.75, 'lat': 38.75,
                'cellnum': 34526
            }

            basin_info['grafton'] = {
                'name': 'Upper Mississippi River Basin',
                'acronym': 'Upper MRB (Unit-III)',
                'station_id': '5587450', 'lon': -90.25, 'lat': 39.25,
                'cellnum': 34191
            }

            basin_info['metropolis'] = {
                'name': 'Ohio River Basin', 'acronym': 'Ohio (Unit-IV)',
                'station_id': '4123050', 'lon': -88.75, 'lat': 37.25,
                'cellnum': 35523
            }

            basin_info['vicksburg'] = {
                'name': 'Lower Mississippi River Basin',
                'acronym': 'Lower MRB (Unit-V)',
                'station_id': '4127800', 'lon': -91.25, 'lat': 32.25,
                'cellnum': 38760
            }

            if include_cellarea or include_only_basin_area: with_upstream = True

            if with_upstream:
                BasinInfo.include_basin_property_upstream(
                                            basin_info, 
                                            wghm_cell_number=wghm_cell_number)

                # special computation for vicksburg basin
                basin_info['vicksburg']['upstream'] = list(
                    set(basin_info['vicksburg']['upstream'])
                    - set(basin_info['hermann']['upstream'])
                    - set(basin_info['grafton']['upstream'])
                    - set(basin_info['metropolis']['upstream'])
                    - set(basin_info['fort_smith']['upstream'])
                )
            
            BasinInfo.GlobalCDA.include_basin_properties(
                                basin_info,
                                include_arcid=include_arcid,
                                include_cellarea=include_cellarea,
                                include_only_basin_area=include_only_basin_area)
            
            
            return basin_info
        #end of function

        @staticmethod
        def Mississippi_validation(
                with_upstream=False,
                wghm_cell_number=True,
                include_arcid=False,
                include_cellarea=False,
                include_only_basin_area=False
        ):

            basin_info = OrderedDict()
            basin_info['louisville_nebraska'] = {
                'station_id': '6805500', 'lon': -96.25, 'lat': 41.25,
                'cellnum': 32754, 'cda_unit': 'hermann'
            }

            basin_info['bismarck'] = {
                'station_id': '6342500', 'lon': -100.75, 'lat': 47.25,
                'cellnum': 28159, 'cda_unit': 'hermann'
            }

            basin_info['landusky_mt'] = {
                'station_id': '6115200', 'lon': -108.75, 'lat': 47.75,
                'cellnum': 27722, 'cda_unit': 'hermann'
            }

            basin_info['mt_carmel'] = {
                'station_id': '3377500', 'lon': -87.75, 'lat': 38.25,
                'cellnum': 34863, 'cda_unit': 'metropolis'
            }

            basin_info['louisville_kentucky'] = {
                'station_id': '3294500', 'lon': -85.75, 'lat': 38.25,
                'cellnum': 34867, 'cda_unit': 'metropolis'
            }

            basin_info['nashville_tn'] = {
                'station_id': '3431500', 'lon': -86.75, 'lat': 36.25,
                'cellnum': 36217, 'cda_unit': 'metropolis'
            }

            if include_cellarea or include_only_basin_area: with_upstream = True

            if with_upstream:
                BasinInfo.include_basin_property_upstream(
                    basin_info,
                    wghm_cell_number=wghm_cell_number)

            BasinInfo.GlobalCDA.include_basin_properties(
                basin_info,
                include_arcid=include_arcid,
                include_cellarea=include_cellarea,
                include_only_basin_area=include_only_basin_area)

            return basin_info

        # end of function
        
        @staticmethod
        def Amazon_level0(with_upstream=False, 
                          wghm_cell_number=True,
                          include_arcid=False, 
                          include_cellarea=False, 
                          include_only_basin_area=False):
            
            basin_info = OrderedDict()
            basin_info['amazonas'] = {
                'station_id': '3623100', 'lon': -50.25, 'lat': 0.25,
                'cellnum': 53829
            }

            if include_cellarea or include_only_basin_area: with_upstream = True

            if with_upstream: 
                BasinInfo.include_basin_property_upstream(
                                            basin_info,
                                            wghm_cell_number=wghm_cell_number)
            
            BasinInfo.GlobalCDA.include_basin_properties(
                                basin_info,
                                include_arcid=include_arcid,
                                include_cellarea=include_cellarea,
                                include_only_basin_area=include_only_basin_area)
            
            return basin_info
        #end of function
        
        @staticmethod
        def Amazon_level1(with_upstream=False, 
                          wghm_cell_number=True,
                          include_arcid=False, 
                          include_cellarea=False, 
                          include_only_basin_area=False):
            basin_info = OrderedDict()
            basin_info['olivenca'] = {
                'station_id': '3623100', 'lon': -69.25, 'lat': -3.25,
                'cellnum': 55134
            }

            basin_info['negro_river'] = {
                'station_id': '3623100', 'lon': -60.75, 'lat': -2.75,
                'cellnum': 54942
            }

            basin_info['manicore'] = {
                'station_id': '3627030', 'lon': -61.25, 'lat': -5.75,
                'cellnum': 56135
            }

            basin_info['obidos'] = {
                'station_id': '3629000', 'lon': -55.75, 'lat': -1.75,
                'cellnum': 54549
            }

            basin_info['amazonas'] = {
                'station_id': '3623100', 'lon': -50.25, 'lat': 0.25,
                'cellnum': 53829
            }

            if include_cellarea or include_only_basin_area: with_upstream = True

            if with_upstream:
                BasinInfo.include_basin_property_upstream(
                                            basin_info, 
                                            wghm_cell_number=wghm_cell_number)
                
                # remove upstream basins from amazonas
                basin_info['amazonas']['upstream'] = list(
                        set(basin_info['amazonas']['upstream'])
                        - set(basin_info['obidos']['upstream'])
                )
                
                # remove upstream basins from obidos
                basin_info['obidos']['upstream'] = list(
                        set(basin_info['obidos']['upstream'])
                        - set(basin_info['negro_river']['upstream'])
                        - set(basin_info['manicore']['upstream'])
                        - set(basin_info['olivenca']['upstream'])
                )
                
                
            BasinInfo.GlobalCDA.include_basin_properties(
                                basin_info,
                                include_arcid=include_arcid,
                                include_cellarea=include_cellarea,
                                include_only_basin_area=include_only_basin_area)
            
            return basin_info
        # end of function

        @staticmethod
        def GangesBrahmaputra_level0(with_upstream=False,
                          wghm_cell_number=True,
                          include_arcid=False,
                          include_cellarea=False,
                          include_only_basin_area=False):

            basin_info = OrderedDict()
            basin_info['ganges'] = {
                'station_id': '2646200', 'lon': 88.75, 'lat': 24.25,
                'cellnum': -1
            }

            basin_info['brahmaputra'] = {
                'station_id': '2651100', 'lon': 89.75, 'lat': 25.25,
                'cellnum': -1
            }

            if include_cellarea or include_only_basin_area: with_upstream = True

            if with_upstream:
                BasinInfo.include_basin_property_upstream(
                                            basin_info,
                                            wghm_cell_number=wghm_cell_number)

            BasinInfo.GlobalCDA.include_basin_properties(
                                basin_info,
                                include_arcid=include_arcid,
                                include_cellarea=include_cellarea,
                                include_only_basin_area=include_only_basin_area)

            # [step] add basin outlet (WaterGAP) cell number
            is_available_outlet_cellnum = True
            for basin in basin_info.keys():
                if basin_info[basin]['cellnum'] == -1:
                    is_available_outlet_cellnum = False
                    break
            
            if (not is_available_outlet_cellnum):
                BasinInfo.GlobalCDA.include_basin_outlet_cellnumber(basin_info)
            # [end]
            
            return basin_info
        #end of function
        
        @staticmethod
        def include_basin_outlet_cellnumber(basin_info):
            for basin in basin_info.keys():
                lat, lon = basin_info[basin]['lat'], basin_info[basin]['lon']
                row, col = gg.find_row_column(lat, lon)
                
                cellnum = gg.get_wghm_cell_number(row, col)
                basin_info[basin]['cellnum'] = cellnum
                

        @staticmethod
        def include_basin_properties(basin_info,
                                     include_arcid=True,
                                     include_cellarea=True,
                                     include_only_basin_area=True):
            
            succeed = False
            if include_arcid: 
                succeed = BasinInfo.include_basin_property_arcid(basin_info)
            
            if (include_cellarea or include_only_basin_area):
                resolution_deg = BasinInfo.GlobalCDA.__model_grid_resolution_deg
                
                succeed = BasinInfo.include_basin_property_cellarea(
                                basin_info,
                                only_total_basin_area=include_only_basin_area,
                                resolution_deg=resolution_deg)
            
            return succeed
        # end of function
        
        
    # end of GlobalCDA class
    
    
    
    # Methods of BasinInfo Class _______________________________________________
    @staticmethod
    def set_model_version():
        model_version = BasinInfo.GlobalCDA.get_model_verson()
        if gg.get_current_model_version != model_version:
            gg.set_model_version(model_version)
    
    
    @staticmethod
    def include_basin_property_upstream(basin_info, wghm_cell_number=True):
        BasinInfo.set_model_version()
        
        up.read_flow_data(unf_input=True, 
                          model_version=BasinInfo.GlobalCDA.get_model_verson())
        
        try:
            for basin, properties in basin_info.items():
                lat, lon = properties['lat'], properties['lon']
                row, col = gg.find_row_column(lat, lon)

                upstream = [(row, col)] + up.get_upstream_cells(row, col)

                if wghm_cell_number:
                    upstream_cnums = [gg.get_wghm_cell_number(x[0], x[1]) 
                                      for x in upstream]
                    properties['upstream'] = upstream_cnums
                else: properties['upstream'] = upstream
        except: return False
        
        return True
        
    @staticmethod
    def include_basin_property_arcid(basin_info):
        BasinInfo.set_model_version()
        
        # step: check avialbility of upstream info
        # check if upstream is already included or not
        succeed = True
        for basin in basin_info.keys():
            if 'upstream' not in basin_info[basin].keys():
                succeed = False
                break
            
            if (len(basin_info[basin]['upstream']) == 0 or
                type(basin_info[basin]['upstream'][0]) is not int): 
                succeed = False
                break
        
        # include upstream cell list if upstream is not previously included
        if not succeed: 
            succeed = BasinInfo.include_basin_property_upstream(
                                              basin_info, wghm_cell_number=True)
        
        if not succeed: return False
        # end of step
        
        # step: collect arcid data and include them in basin properties
        # load grid info
        grid_info = gg.get_wghm_grid_info()
        if len(grid_info) == 0: return False
        
        for basin in basin_info.keys():
            upstream = basin_info[basin]['upstream']
            
            ii = [np.where(grid_info[:,0]==x)[0][0] for x in upstream]
            
            # add arcid
            basin_info[basin]['arcid'] = grid_info[ii, 1]
        # end of step
        
        return True
        
    @staticmethod
    def include_basin_property_cellarea(basin_info, 
                                        only_total_basin_area=False,
                                        resolution_deg=0.5):
        
        # inner function to read latitudinal cell area
        def read_latitudinal_cell_area():
            f = gg.get_wghm_cell_area_file()
            lat_carea = np.fromfile(f, dtype='>f')
            
            if len(lat_carea) != 360: return np.empty(0)
            else: return lat_carea
        # end of inner function
        
        BasinInfo.set_model_version()
        
        # step: check avialbility of upstream info
        # check if upstream is already included or not
        succeed = True
        for basin in basin_info.keys():
            if 'upstream' not in basin_info[basin].keys():
                succeed = False
                break
            
            if (len(basin_info[basin]['upstream']) == 0 or
                type(basin_info[basin]['upstream'][0]) is not int): 
                succeed = False
                break
        
        # include upstream cell list if upstream is not previously included
        if not succeed: 
            succeed = BasinInfo.include_basin_property_upstream(
                                              basin_info, wghm_cell_number=True)
        
        if not succeed: return False
        # end of step
        
        # step: collect area data and include them in basin properties 
        # load grid info
        grid_info = gg.get_wghm_grid_info()
        if len(grid_info) == 0: return False
        
        cell_area = read_latitudinal_cell_area()
        if len(cell_area) != 360: return False
        
        for basin in basin_info.keys():
            upstream = basin_info[basin]['upstream']
            
            ii = [np.where(grid_info[:,0]==x)[0][0] for x in upstream]
            
            lats = grid_info[ii, 3]
            rr = (np.abs(lats - 90) // resolution_deg).astype(int)
            
            if not only_total_basin_area: 
                basin_info[basin]['area'] = cell_area[rr]
            else: basin_info[basin]['basin_area'] = np.sum(cell_area[rr])
        # end of step
        
        return True