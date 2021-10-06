import sys, numpy as np
from collections import OrderedDict

sys.path.append('..')
from utilities.globalgrid import GlobalGrid as gg
from utilities.upstream import Upstream as up
from wgap.wgapio import WaterGapIO as wio

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
        def GermanFrenchBasin_Entire(
            compute_upstream=False,
            wghm_cell_number=True,
            include_arcid=False,
            include_cellarea=False,
            include_only_basin_area=False,
            report_continental_area=False
        ):
            basin_info = OrderedDict()
            basin_info['elbe'] = {
                'bid': 1, 'name': 'Elbe Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': 8.75, 'lat': 53.75,
                'cellnum': 22538
            }

            basin_info['weser'] = {
                'bid': 2, 'name': 'Weser Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': 8.25, 'lat': 53.75,
                'cellnum': 22537
            }

            basin_info['rhine'] = {
                'bid': 3, 'name': 'Rhine Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': 4.25, 'lat': 52.25,
                'cellnum': 23905
            }

            basin_info['meuse'] = {
                'bid': 4, 'name': 'Meuse Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': 3.75, 'lat': 51.75,
                'cellnum': 24363
            }

            basin_info['seine'] = {
                'bid': 5, 'name': 'Seine Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': 0.25, 'lat': 49.75,
                'cellnum': 26107
            }

            basin_info['rhone'] = {
                'bid': 6, 'name': 'Rhone Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': 4.75, 'lat': 43.25,
                'cellnum': 31405
            }

            basin_info['loire'] = {
                'bid': 7, 'name': 'Loire Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': -2.25, 'lat': 47.25,
                'cellnum': 28236
            }

            basin_info['vilaine'] = {
                'bid': 8, 'name': 'Vilaine Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': -2.25, 'lat': 47.75,
                'cellnum': 27826
            }

            basin_info['garonne'] = {
                'bid': 9, 'name': 'Garonne Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': -0.75, 'lat': 45.25,
                'cellnum': 29861
            }

            basin_info['adour'] = {
                'bid': 10, 'name': 'Adour Basin', 'acronym': 'NA',
                'station_id': '-1', 'lon': -1.25, 'lat': 43.75,
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
                include_only_basin_area=include_only_basin_area,
                report_continental_area=report_continental_area
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
        def GermanFrenchBasin_Level0(
            compute_upstream=False,
            wghm_cell_number=True,
            include_arcid=False,
            include_cellarea=False,
            include_only_basin_area=False,
            report_continental_area=False
        ):
            basin_info = OrderedDict()
            basin_info['elbe'] = {
                'bid': 1, 'name': 'Elbe Basin', 'acronym': 'NA',
                'station_id': '6340110', 'lon': 11.25, 'lat': 53.25,
                'cellnum': 23001
            }

            basin_info['weser'] = {
                'bid': 2, 'name': 'Weser Basin', 'acronym': 'NA',
                'station_id': '6337200', 'lon': 9.25, 'lat': 52.75,
                'cellnum': 23453
            }

            basin_info['rhine'] = {
                'bid': 3, 'name': 'Rhine Basin', 'acronym': 'NA',
                'station_id': '6435060', 'lon': 6.25, 'lat': 51.75,
                'cellnum': 24368
            }

            basin_info['meuse'] = {
                'bid': 4, 'name': 'Meuse Basin', 'acronym': 'NA',
                'station_id': '6421500', 'lon': 5.75, 'lat': 50.75,
                'cellnum': 25256
            }

            basin_info['seine'] = {
                'bid': 5, 'name': 'Seine Basin', 'acronym': 'NA',
                'station_id': '6122100', 'lon': 1.75, 'lat': 49.25,
                'cellnum': 26547
            }

            basin_info['rhone'] = {
                'bid': 6, 'name': 'Rhone Basin', 'acronym': 'NA',
                'station_id': '6139100', 'lon': 4.75, 'lat': 43.75,
                'cellnum': 31028
            }

            basin_info['loire'] = {
                'bid': 7, 'name': 'Loire Basin', 'acronym': 'NA',
                'station_id': '6123100', 'lon': -0.75, 'lat': 47.25,
                'cellnum': 28239
            }

            basin_info['garonne_mas_agenais'] = {
                'bid': 8, 'name': 'Garonne Basin', 'acronym': 'NA',
                'station_id': '6125100', 'lon': 0.25, 'lat': 44.25,
                'cellnum': 30639
            }

            basin_info['garonne_baigneaux'] = {
                'bid': 9, 'name': 'Garonne Basin (Ruisseau L\'Engranne)', 'acronym': 'NA',
                'station_id': '6124100', 'lon': -0.25, 'lat': 44.75,
                'cellnum': 30253
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
                include_only_basin_area=include_only_basin_area,
                report_continental_area=report_continental_area
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
        def GermanFrenchBasin_level1(
                compute_upstream=False,
                wghm_cell_number=True,
                include_arcid=False,
                include_cellarea=False,
                include_only_basin_area=False,
                report_continental_area=False
        ):
            basin_info = OrderedDict()
            basin_info['elbe_neu_darchau'] = {
                'bid': 101, 'name': 'Elbe (Neu-Darchau)', 'acronym': 'NA',
                'parent_basin': 'Elbe River Basin','station_id': 6340110,
                'station_name': 'Neu-Darchau','river': 'Elbe River',
                'lon': 11.25, 'lat': 53.25, 'arcid': 23013, 'cellnum': 23001,
                'is_downmost_station': True
            }

            basin_info['elbe_tangermuende'] = {
                'bid': 102, 'name': 'Elbe (Tangermuende)', 'acronym': 'NA',
                'parent_basin': 'Elbe River Basin','station_id': 6340160,
                'station_name': 'Tangermuende','river': 'Elbe River',
                'lon': 11.75, 'lat': 52.25, 'arcid': 23934, 'cellnum': 23920,
                'is_downmost_station': False
            }

            basin_info['elbe_aken'] = {
                'bid': 103, 'name': 'Elbe (Aken)', 'acronym': 'NA',
                'parent_basin': 'Elbe River Basin','station_id': 6340170,
                'station_name': 'Aken','river': 'Elbe River',
                'lon': 12.25, 'lat': 51.75, 'arcid': 24394, 'cellnum': 24380,
                'is_downmost_station': False
            }

            basin_info['elbe_decin'] = {
                'bid': 104, 'name': 'Elbe (Decin)', 'acronym': 'NA',
                'parent_basin': 'Elbe River Basin','station_id': 6140400,
                'station_name': 'Decin','river': 'Elbe River',
                'lon': 14.25, 'lat': 50.75, 'arcid': 25287, 'cellnum': 25273,
                'is_downmost_station': False
            }
            basin_info['wesser_rethem'] = {
                'bid': 201, 'name': 'Weser (Rethem)', 'acronym': 'NA',
                'parent_basin': 'Weser Basin','station_id': 6337250,
                'station_name': 'Rethem','river': 'Aller',
                'lon': 9.75, 'lat': 52.75, 'arcid': 23468, 'cellnum': 23454,
                'is_downmost_station': False
            }

            basin_info['wesser_liebenau'] = {
                'bid': 202, 'name': 'Weser (Liebenau)', 'acronym': 'NA',
                'parent_basin': 'Weser Basin','station_id': 6337517,
                'station_name': 'Liebenau','river': 'Weser',
                'lon': 8.75, 'lat': 52.25, 'arcid': 23928, 'cellnum': 23914,
                'is_downmost_station': False
            }

            basin_info['wesser_intschede'] = {
                'bid': 203, 'name': 'Weser (Intschede)', 'acronym': 'NA',
                'parent_basin': 'Weser Basin','station_id': 6337200,
                'station_name': 'Intschede','river': 'Weser',
                'lon': 9.25, 'lat': 52.75, 'arcid': 23467, 'cellnum': 23453,
                'is_downmost_station': True
            }

            basin_info['upper_rhine_murgenthal'] = {
                'bid': 301, 'name': 'Upper Rhine (Murgenthal)', 'acronym': 'NA',
                'parent_basin': 'Upper Rhine River Basin', 'station_id': 6935302,
                'station_name': 'Murgenthal','river': 'Aare',
                'lon': 7.25, 'lat': 47.25, 'arcid': 28287, 'cellnum': 28255,
                'is_downmost_station': False
            }

            basin_info['upper_rhine_rekingen'] = {
                'bid': 302, 'name': 'Upper Rhine (Rekingen)', 'acronym': 'NA',
                'parent_basin': 'Upper Rhine River Basin','station_id': 6935054,
                'station_name': 'Rekingen','river': 'Rhine River',
                'lon': 8.75, 'lat': 47.75, 'arcid': 27871, 'cellnum': 27848,
                'is_downmost_station': False
            }

            basin_info['upper_rhine_maxau'] = {
                'bid': 303, 'name': 'Upper Rhine (Maxau)', 'acronym': 'NA',
                'parent_basin': 'Upper Rhine River Basin','station_id': 6335200,
                'station_name': 'Maxau','river': 'Rhine River',
                'lon': 8.25, 'lat': 48.75, 'arcid': 27010, 'cellnum': 26996,
                'is_downmost_station': False
            }

            basin_info['lower_rhine_rockenau_ska'] = {
                'bid': 304, 'name': 'Lower Rhine (Rockenau-Ska)', 'acronym': 'NA',
                'parent_basin': 'Lower Rhine River Basin','station_id': 6335600,
                'station_name': 'Rockenau-Ska','river': 'Neckar',
                'lon': 9.25, 'lat': 49.25, 'arcid': 26576, 'cellnum': 26562,
                'is_downmost_station': False
            }

            basin_info['lower_rhine_mainz'] = {
                'bid': 305, 'name': 'Lower Rhine (Mainz)', 'acronym': 'NA',
                'parent_basin': 'Lower Rhine River Basin','station_id': 6335150,
                'station_name': 'Mainz','river': 'Rhine River',
                'lon': 8.25, 'lat': 49.75, 'arcid': 26137, 'cellnum': 26123,
                'is_downmost_station': False
            }

            basin_info['lower_rhine_frankfurt_main'] = {
                'bid': 306, 'name': 'Lower Rhine (Frankfurt / Main (Osthafen))',
                'acronym': 'NA', 'parent_basin': 'Lower Rhine River Basin',
                'station_id': 6335304, 'station_name': 'Frankfurt / Main (Osthafen)',
                'river': 'Main', 'lon': 8.75, 'lat': 50.25,
                'arcid': 25711, 'cellnum': 25697,
                'is_downmost_station': False
            }

            basin_info['lower_rhine_trier_up'] = {
                'bid': 307, 'name': 'Lower Rhine (Trier Up)', 'acronym': 'NA',
                'parent_basin': 'Lower Rhine River Basin','station_id': 6336500,
                'station_name': 'Trier Up','river': 'Moselle River',
                'lon': 6.25, 'lat': 49.75, 'arcid': 26133, 'cellnum': 26119,
                'is_downmost_station': False
            }

            basin_info['lower_rhine_andernach'] = {
                'bid': 308, 'name': 'Lower Rhine (Andernach)', 'acronym': 'NA',
                'parent_basin': 'Lower Rhine River Basin','station_id': 6335070,
                'station_name': 'Andernach','river': 'Rhine River',
                'lon': 7.75, 'lat': 50.25, 'arcid': 25709, 'cellnum': 25695,
                'is_downmost_station': False
            }

            basin_info['lower_rhine_lobith'] = {
                'bid': 309, 'name': 'Lower Rhine (Lobith)', 'acronym': 'NA',
                'parent_basin': 'Lower Rhine River Basin','station_id': 6435060,
                'station_name': 'Lobith','river': 'Rhine River',
                'lon': 6.25, 'lat': 51.75, 'arcid': 24382, 'cellnum': 24368,
                'is_downmost_station': True
            }

            basin_info['meuse_borgharen'] = {
                'bid': 401, 'name': 'Meuse (Borgharen)', 'acronym': 'NA',
                'parent_basin': 'Meuse River Basin','station_id': 6421500,
                'station_name': 'Borgharen','river': 'Meuse',
                'lon': 5.75, 'lat': 50.75, 'arcid': 25270, 'cellnum': 25256,
                'is_downmost_station': True
            }

            basin_info['seine_paris'] = {
                'bid': 501, 'name': 'Seine (Paris)', 'acronym': 'NA',
                'parent_basin': 'Seine River Basin','station_id': 6122300,
                'station_name': 'Paris','river': 'Seine',
                'lon': 2.25, 'lat': 48.75, 'arcid': 26998, 'cellnum': 26984,
                'is_downmost_station': False
            }

            basin_info['seine_poses'] = {
                'bid': 502, 'name': 'Seine (Poses)', 'acronym': 'NA',
                'parent_basin': 'Seine River Basin','station_id': 6122100,
                'station_name': 'Poses','river': 'Seine',
                'lon': 1.75, 'lat': 49.25, 'arcid': 26561, 'cellnum': 26547,
                'is_downmost_station': True
            }

            basin_info['upper_loire_fourilles'] = {
                'bid': 701, 'name': 'Upper Loire (Fourilles)', 'acronym': 'NA',
                'parent_basin': 'Upper Loire River Basin','station_id': 6123610,
                'station_name': 'Fourilles','river': 'Boublon Lagees',
                'lon': 3.25, 'lat': 46.25, 'arcid': 29111, 'cellnum': 29078,
                'is_downmost_station': False
            }

            basin_info['upper_loire_rigny_sur_arroux'] = {
                'bid': 702, 'name': 'Upper Loire (Rigny-Sur-Arroux)',
                'acronym': 'NA', 'parent_basin': 'Upper Loire River Basin',
                'station_id': 6123710, 'station_name': 'Rigny-Sur-Arroux',
                'river': 'Arroux', 'lon': 3.75, 'lat': 46.75,
                'arcid': 28700, 'cellnum': 28667,
                'is_downmost_station': False
            }

            basin_info['upper_loire_blois'] = {
                'bid': 703, 'name': 'Upper Loire (Blois)', 'acronym': 'NA',
                'parent_basin': 'Upper Loire River Basin','station_id': 6123300,
                'station_name': 'Blois','river': 'Loire',
                'lon': 1.75, 'lat': 47.75, 'arcid': 27857, 'cellnum': 27834,
                'is_downmost_station': False
            }

            basin_info['lower_loire_montjean'] = {
                'bid': 704, 'name': 'Lower Loire (Montjean)', 'acronym': 'NA',
                'parent_basin': 'Lower Loire River Basin','station_id': 6123100,
                'station_name': 'Montjean','river': 'Loire',
                'lon': -0.75, 'lat': 47.25, 'arcid': 28271, 'cellnum': 28239,
                'is_downmost_station': True
            }

            basin_info['rhone_beaucaire'] = {
                'bid': 601, 'name': 'Rhone (Beaucaire)', 'acronym': 'NA',
                'parent_basin': 'Rhone River Basin','station_id': 6139100,
                'station_name': 'Beaucaire','river': 'Rhone',
                'lon': 4.75, 'lat': 43.75, 'arcid': 31091, 'cellnum': 31028,
                'is_downmost_station': True
            }

            basin_info['rhone_mulatiere'] = {
                'bid': 602, 'name': 'Rhone (La Mulatiere)', 'acronym': 'NA',
                'parent_basin': 'Rhone River Basin','station_id': 6139390,
                'station_name': 'La Mulatiere','river': 'Rhone',
                'lon': 4.75, 'lat': 45.75, 'arcid': 29516, 'cellnum': 29483,
                'is_downmost_station': False
            }

            basin_info['rhone_chancy_aux_ripes'] = {
                'bid': 603, 'name': 'Rhone (Chancy, Aux Ripes)', 'acronym': 'NA',
                'parent_basin': 'Rhone River Basin','station_id': 6939050,
                'station_name': 'Chancy, Aux Ripes','river': 'Rhone',
                'lon': 5.75, 'lat': 46.25, 'arcid': 29116, 'cellnum': 29083,
                'is_downmost_station': False
            }

            basin_info['garonne_mas_agenais'] = {
                'bid': 801, 'name': 'Garonne (Mas-D\'Agenais)', 'acronym': 'NA',
                'parent_basin': 'Garonne River Basin','station_id': 6125100,
                'station_name': 'Mas-D\'Agenais','river': 'Garonne',
                'lon': 0.25, 'lat': 44.25, 'arcid': 30693, 'cellnum': 30639,
                'is_downmost_station': True
            }

            basin_info['garonne_baigneaux'] = {
                'bid': 802, 'name': 'Garonne (Baigneaux)', 'acronym': 'NA',
                'parent_basin': 'Garonne River Basin','station_id': 6124100,
                'station_name': 'Baigneaux','river': 'Ruisseau L\'Engranne',
                'lon': -0.25, 'lat': 44.75, 'arcid': 30300, 'cellnum': 30253,
                'is_downmost_station': True
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
                include_only_basin_area=include_only_basin_area,
                report_continental_area=report_continental_area
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
            include_only_basin_area=False,
            report_continental_area=False
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
                                include_only_basin_area=include_only_basin_area,
                                report_continental_area=report_continental_area)
            
            return basin_info
        #end of function
        

        @staticmethod
        def Mississippi_level1(with_upstream=False, 
                               wghm_cell_number=True,
                               include_arcid=False, 
                               include_cellarea=False, 
                               include_only_basin_area=False,
                               report_continental_area=False):
            
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
                                include_only_basin_area=include_only_basin_area,
                                report_continental_area=report_continental_area)
            
            
            return basin_info
        #end of function

        @staticmethod
        def Mississippi_validation(
                with_upstream=False,
                wghm_cell_number=True,
                include_arcid=False,
                include_cellarea=False,
                include_only_basin_area=False,
                report_continental_area=False
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
                include_only_basin_area=include_only_basin_area,
                report_continental_area=report_continental_area)

            return basin_info

        # end of function
        
        @staticmethod
        def Amazon_level0(with_upstream=False, 
                          wghm_cell_number=True,
                          include_arcid=False, 
                          include_cellarea=False, 
                          include_only_basin_area=False,
                          report_continental_area=False):
            
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
                                include_only_basin_area=include_only_basin_area,
                                report_continental_area=report_continental_area)
            
            return basin_info
        #end of function
        
        @staticmethod
        def Amazon_level1(with_upstream=False, 
                          wghm_cell_number=True,
                          include_arcid=False, 
                          include_cellarea=False, 
                          include_only_basin_area=False,
                          report_continental_area=False):
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
                                include_only_basin_area=include_only_basin_area,
                                report_continental_area=report_continental_area)
            
            return basin_info
        # end of function

        @staticmethod
        def GangesBrahmaputra_level0(with_upstream=False,
                          wghm_cell_number=True,
                          include_arcid=False,
                          include_cellarea=False,
                          include_only_basin_area=False,
                          report_continental_area=False):

            basin_info = OrderedDict()
            basin_info['ganges'] = {
                'acronym': 'GAN',
                'station_id': '2646200', 'lon': 88.75, 'lat': 24.25,
                'cellnum': 43913
            }

            basin_info['brahmaputra'] = {
                'acronym': 'BRH',
                'station_id': '2651100', 'lon': 89.75, 'lat': 25.25,
                'cellnum': 43357
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
                                include_only_basin_area=include_only_basin_area,
                                report_continental_area=report_continental_area)

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
                                     include_only_basin_area=True,
                                     report_continental_area=False):
            
            succeed = False
            if include_arcid: 
                succeed = BasinInfo.include_basin_property_arcid(basin_info)
            
            if (include_cellarea or include_only_basin_area):
                resolution_deg = BasinInfo.GlobalCDA.__model_grid_resolution_deg
                
                succeed = BasinInfo.include_basin_property_cellarea(
                                basin_info,
                                only_total_basin_area=include_only_basin_area,
                                resolution_deg=resolution_deg,
                                report_continental_area=report_continental_area)
            
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
                                        resolution_deg=0.5,
                                        report_continental_area=False
                                        ):
        
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
            
            basin_info[basin]['area'] = cell_area[rr]

        # end of step

        ## step: compute continental area
        if report_continental_area:
            contarea_frc = wio.compute_continental_area_fraction()

            for basin in basin_info.keys():
                upstream = np.array(basin_info[basin]['upstream'])
                area_frc = contarea_frc[upstream - 1]
                basin_info[basin]['area'] *= area_frc
        ## end of step

        ## step: compute total basin area
        if only_total_basin_area:
            for basin in basin_info.keys():
                area = basin_info[basin].pop('area')
                basin_info[basin]['basin_area'] = area.sum()
        ##

        return True