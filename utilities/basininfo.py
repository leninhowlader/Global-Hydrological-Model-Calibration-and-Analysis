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
        def Mississippi_level0(with_upstream=False, 
                               wghm_cell_number=True,
                               include_arcid=False, 
                               include_cellarea=False, 
                               include_only_basin_area=False):
            
            basin_info = OrderedDict()
            basin_info['mississippi'] = {'station_id': '4127800', 'lon': -91.25, 'lat': 32.25, 'cellnum': 38760}

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
            basin_info['hermann'] = {'station_id': '4122900', 'lon': -91.75, 'lat': 38.75, 'cellnum': 34526}
            basin_info['alton'] = {'station_id': '4119800', 'lon': -90.25, 'lat': 39.25, 'cellnum': 34191}
            basin_info['metropolis'] = {'station_id': '4123050', 'lon': -88.75, 'lat': 37.25, 'cellnum': 35523}
            basin_info['little_rock'] = {'station_id': '4125800', 'lon': -92.25, 'lat': 34.75, 'cellnum': 37185}
            basin_info['vicksburg'] = {'station_id': '4127800', 'lon': -91.25, 'lat': 32.25, 'cellnum': 38760}


            if with_upstream:
                BasinInfo.include_basin_property_upstream(
                                            basin_info, 
                                            wghm_cell_number=wghm_cell_number)

                # special computation for vicksburg basin
                basin_info['vicksburg']['upstream'] = list(
                    set(basin_info['vicksburg']['upstream'])
                    - set(basin_info['hermann']['upstream'])
                    - set(basin_info['alton']['upstream'])
                    - set(basin_info['metropolis']['upstream'])
                    - set(basin_info['little_rock']['upstream'])
                )
            
            BasinInfo.GlobalCDA.include_basin_properties(
                                basin_info,
                                include_arcid=include_arcid,
                                include_cellarea=include_cellarea,
                                include_only_basin_area=include_only_basin_area)
            
            
            return basin_info
        #end of function

        
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
                succeed 
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
                succeed 
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