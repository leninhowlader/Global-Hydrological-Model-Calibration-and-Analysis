import pandas as pd
from collections import OrderedDict

class ParameterInfo:
    __param_info = OrderedDict()
    __param_info['precip_mult'] = {
                'description': 'Precipitation multiplier',
                'acronym': 'P-PM',
                'log_scale': False,
                'min': 0.5,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'P',
                'index': 1
    }
    __param_info['net_radiation_mult'] = {
                'description': 'Net radiation multiplier',
                'acronym': 'EP-NM',
                'log_scale': False,
                'min': 0.5,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'EP',
                'index': 2
    }
    __param_info['PT_coeff_humid'] = {
                'description': 'Priestley-Taylor coefficient (humid)',
                'acronym': 'EP-PTh',
                'log_scale': False,
                'min': 0.885,
                'max': 1.65,
                'nominal': 1.26,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'EP',
                'index': 3
    }
    __param_info['PT_coeff_arid'] = {
                'description': 'Priestley-Taylor coefficient (semi-arid/arid)',
                'acronym': 'EP-PTa',
                'log_scale': False,
                'min': 1.365,
                'max': 2.115,
                'nominal': 1.74,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'EP',
                'index': 4
    }
    __param_info['mcwh'] = {
                'description': 'Max. canopy water height [mm]',
                'acronym': 'CA-MC',
                'log_scale': False,
                'min': 0.1,
                'max': 1.4,
                'nominal': 0.3,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'CA',
                'index': 5
    }
    __param_info['LAI_mult'] = {
                'description': 'LAI multiplier',
                'acronym': 'CA-LAIM',
                'log_scale': False,
                'min': 0.2,
                'max': 2.5,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'CA',
                'index': 6
    }
    __param_info['snow_freeze_temp'] = {
                'description': 'Snow-freeze temperature [°C]',
                'acronym': 'SN-FT',
                'log_scale': False,
                'min': -1,
                'max': 3.0,
                'nominal': 2.0,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SN',
                'index': 7
    }
    __param_info['snow_melt_temp'] = {
                'description': 'Snow-melt temperature [°C]',
                'acronym': 'SN-MT',
                'log_scale': False,
                'min': -3.75,
                'max': 3.75,
                'nominal': 0.0,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SN',
                'index': 8
    }
    __param_info['degree_day_factor_mult'] = {
                'description': 'Degree-day factor multiplier',
                'acronym': 'SN-DM',
                'log_scale': False,
                'min': 0.5,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'SN',
                'index': 9
    }
    __param_info['temperature_gradient'] = {
                'description': 'Temperature gradient [°C/m]',
                'acronym': 'SN-TG',
                'log_scale': False,
                'min': 0.001,
                'max': 0.01,
                'nominal': 0.006,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SN',
                'index': 10
    }
    __param_info['gammaHBV_runoff_coeff'] = {
                'description': 'Runoff coefficient',
                'acronym': 'SL-RC',
                'log_scale': False,
                'min': 0.3,
                'max': 3.0,
                'nominal': 2.0,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SL',
                'index': 11
    }
    __param_info['root_depth_multiplier'] = {
                'description': 'Maximum soil capacity multiplier',
                'acronym': 'SL-MSM',
                'log_scale': False,
                'min': 0.5,
                'max': 3.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'SL',
                'index': 12
    }
    __param_info['max_daily_PET'] = {
                'description': 'Maximum EP (mm/d)',
                'acronym': 'SL-MEP',
                'log_scale': False,
                'min': 6.0,
                'max': 22.0,
                'nominal': 15.0,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SL',
                'index': 13
    }
    __param_info['river_roughness_coeff_mult'] = {
                'description': 'River roughness coefficient multiplier',
                'acronym': 'SW-RRM',
                'log_scale': False,
                'min': 1.0,
                'max': 5.0,
                'nominal': 3,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'SW',
                'index': 14
    }
    __param_info['lake_depth'] = {
                'description': 'Active lake depth [m]',
                'acronym': 'SW-LD',
                'log_scale': False,
                'min': 1.0,
                'max': 20.0,
                'nominal': 5,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SW',
                'index': 15
    }
    __param_info['wetland_depth'] = {
                'description': 'Active wetland depth [m]',
                'acronym': 'SW-WD',
                'log_scale': False,
                'min': 1.0,
                'max': 20.0,
                'nominal': 2.0,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SW',
                'index': 16
    }
    __param_info['surfacewater_outflow_coefficient'] = {
                'description': 'SW discharge coefficient [1/d]',
                'acronym': 'SW-DC',
                'log_scale': False,
                'min': 0.001,
                'max': 0.1,
                'nominal': 0.01,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'SW',
                'index': 17
    }
    __param_info['evapo_red_fact_exp_mult'] = {
                'description': 'ET reduction factor multiplier',
                'acronym': 'SW-ERM',
                'log_scale': False,
                'min': 0.33,
                'max': 1.5,
                'nominal': 1,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'SW',
                'index': 18
    }
    __param_info['gw_factor_mult'] = {
                'description': 'GW recharge factor multiplier',
                'acronym': 'GW-RFM',
                'log_scale': False,
                'min': 0.3,
                'max': 3.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'GW',
                'index': 19
    }
    __param_info['rg_max_mult'] = {
                'description': 'Max. GW recharge multiplier',
                'acronym': 'GW-MM',
                'log_scale': False,
                'min': 0.3,
                'max': 3.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'GW',
                'index': 20
    }
    __param_info['pcrit_aridgw'] = {
                'description': 'Critical precipitation for GW recharge (arid/semi-arid) [mm/d]',
                'acronym': 'GW-CP',
                'log_scale': False,
                'min': 2.5,
                'max': 20.0,
                'nominal': 12.5,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'GW',
                'index': 21
    }
    __param_info['groundwater_outflow_coeff'] = {
                'description': 'GW discharge coefficient [1/d]',
                'acronym': 'GW-DC',
                'log_scale': False,
                'min': 0.001,
                'max': 0.02,
                'nominal': 0.01,
                'optimal': None,
                'distribution': 'uniform',
                'group': 'GW',
                'index': 22
    }
    __param_info['net_abstraction_surfacewater_mult'] = {
                'description': 'Net SW abstraction multiplier',
                'acronym': 'NA-SM',
                'log_scale': False,
                'min': -2.0,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'NA',
                'index': 23
    }
    __param_info['net_abstraction_groundwater_mult'] = {
                'description': 'Net GW abstraction multiplier',
                'acronym': 'NA-GM',
                'log_scale': False,
                'min': -2.0,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'NA',
                'index': 24
    }
    __param_info['consumptive_use_mult'] = {
                'description': 'Consumptive use multiplier',
                'acronym': 'CU-M',
                'log_scale': False,
                'min': 0.2,
                'max': 6.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular',
                'group': 'CU',
                'index': 25
    }

    @staticmethod
    def get_parameter_info():
        param_info = OrderedDict()
        for param in ParameterInfo.__param_info.keys():
            param_info[param] = ParameterInfo.__param_info[param].copy()

        return param_info

    @staticmethod
    def get_selected_paramter_info(param_names:list=[], param_acronyms:list=[]):
        if not (param_names or param_acronyms): return {}

        param_info = OrderedDict()

        succeed = False
        if param_names:
            try:
                for param in param_names:
                    param_info[param] = ParameterInfo.__param_info[param].copy()
                succeed = True
            except: pass

        if not succeed and param_acronyms:
            for acronym in param_acronyms:
                for param in ParameterInfo.__param_info.keys():
                    if ParameterInfo.__param_info[param]['acronym'] == acronym:
                        param_info[param] = ParameterInfo.__param_info[param].copy()
                        break
            if len(param_info) == len(param_acronyms): succeed = True

        if succeed: return param_info
        else: return {}

    @staticmethod
    def write_parameter_info(
            filename_out,
            param_names:list=[],
            param_acronyms:list=[],
            param_info:dict={}
    ):
        if not filename_out: return False

        if not param_info:
            if param_names or param_acronyms:
                param_info = ParameterInfo.get_selected_paramter_info(
                    param_names=param_names,
                    param_acronyms=param_acronyms
                )
            else: param_info = ParameterInfo.__param_info

        if len(param_info) == 0: return False

        df = pd.DataFrame()
        df['parameter_name'] = list(param_info.keys())

        info = ['min', 'max', 'nominal', 'distribution']
        for x in info:
            temp = []
            for param in param_info.keys(): temp.append(param_info[param][x])
            df[x] = temp

        df.to_csv(filename_out, index=False)

        return True

    @staticmethod
    def update_parameters(param_info:dict, property_name, values):
        if len(param_info) != len(values): return False

        param_names = list(param_info.keys())
        for i in range(len(param_names)):
            param = param_names[i]
            try: param_info[param][property_name] = values[i]
            except: return False

        return True

    @staticmethod
    def get_parameter_property_values(param_info:dict, property_name):
        values = []
        try:
            for param in param_info.keys():
                values.append(param_info[param][property_name])
        except: return []

        return values

    @staticmethod
    def get_parameter_property_names():
        property_names = ['description', 'acronym', 'log_scale', 'min', 'max',
                          'nominal', 'optimal', 'distribution']
        return property_names

    @staticmethod
    def describe_parameters(
            param_info,
            filename_out='',
            added_description=''
    ):
        string_out = '\nBEGIN PARAMETER'

        for param in param_info.keys():
            string_out += '\n@'
            string_out += '\nparam_name = %s' % param
            if param_info[param]['log_scale']:
                import math

                s_min = ('%f' % math.log10(param_info[param]['min'])
                         ).rstrip('0').rstrip('.')
                s_max = ('%f' % math.log10(param_info[param]['max'])
                         ).rstrip('0').rstrip('.')
                string_out += '\nlower_bound = %s' % s_min
                string_out += '\nupper_bound = %s' % s_max

                string_out += '\nlogarithmic_scale = True'
            else:
                s_min = ('%f' % param_info[param]['min']).rstrip('0').rstrip('.')
                s_max = ('%f' % param_info[param]['max']).rstrip('0').rstrip('.')
                string_out += '\nlower_bound = %s' % s_min
                string_out += '\nupper_bound = %s' % s_max
            if added_description: string_out += '\n%s' % added_description
            string_out += '\n@@'

        string_out += '\nEND PARAMETER\n'

        if filename_out:
            f = open(filename_out, 'a')
            f.write(string_out)
            f.close()
        else: print(string_out)

    class GlobalCDA:
        parameter_acronyms = {
            'gammaHBV_runoff_coeff': 'SL-RC',
            'root_depth_multiplier': 'SL-MSM',
            'river_roughness_coeff_mult': 'SW-RRM',
            'lake_depth': 'SW-LD',
            'wetland_depth': 'SW-WD',
            'surfacewater_outflow_coefficient': 'SW-DC',
            'evapo_red_fact_exp_mult': 'SW-ERM',
            'net_radiation_mult': 'EP-NM',
            'PT_coeff_humid': 'EP-PTh',
            'PT_coeff_arid': 'EP-PTa',
            'max_daily_PET': 'SL-MEP',
            'mcwh': 'CA-MC',
            'LAI_mult': 'CA-LAIM',
            'snow_freeze_temp': 'SN-FT',
            'snow_melt_temp': 'SN-MT',
            'degree_day_factor_mult': 'SN-DM',
            'temperature_gradient': 'SN-TG',
            'gw_factor_mult': 'GW-RFM',
            'rg_max_mult': 'GW-MM',
            'pcrit_aridgw': 'GW-CP',
            'groundwater_outflow_coeff': 'GW-DC',
            'net_abstraction_surfacewater_mult': 'NA-SM',
            'net_abstraction_groundwater_mult': 'NA-GM',
            'precip_mult': 'P-PM'
        }

        @staticmethod
        def update_multibasin_parameter_acronym(multibasin_parameter_info):
            acronyms = ParameterInfo.GlobalCDA.parameter_acronyms

            for basin in multibasin_parameter_info.keys():
                for param, info in multibasin_parameter_info[basin].items():
                    info['acronym'] = acronyms[param]

            return multibasin_parameter_info

        @staticmethod
        def update_parameter_acronym(parameter_info):
            acronyms = ParameterInfo.GlobalCDA.parameter_acronyms

            for param, info in parameter_info.items():
                info['acronym'] = acronyms[param]

            return parameter_info

        @staticmethod
        def Mississippi_Sensitive_Parameters():
            param_info = OrderedDict()

            paramlist_hermann = ['Gamma', 'RTDM', 'LKDep', 'WLDep', 'SWOC',
                                 'PTCH', 'SNMT', 'SWAM', 'GWAM']
            pinfo = ParameterInfo.get_selected_paramter_info(
                                            param_acronyms=paramlist_hermann)
            param_info['hermann'] = pinfo

            paramlist_grafton = ['Gamma', 'RTDM', 'LKDep', 'WLDep', 'SWOC',
                                 'PTCH', 'SNMT', 'MRGM']
            pinfo = ParameterInfo.get_selected_paramter_info(
                                            param_acronyms=paramlist_grafton)
            param_info['grafton'] = pinfo

            paramlist_metropolis = ['Gamma', 'RTDM', 'RRCM', 'LKDep', 'WLDep',
                                    'SWOC', 'PTCH', 'SNMT', 'MRGM', 'GWOC']
            pinfo = ParameterInfo.get_selected_paramter_info(
                                            param_acronyms=paramlist_metropolis)
            param_info['metropolis'] = pinfo

            paramlist_fortsmith = ['Gamma', 'RTDM', 'LKDep', 'WLDep', 'SWOC',
                                   'PTCH', 'MDPET', 'SNMT', 'MRGM', 'GWAM']
            pinfo = ParameterInfo.get_selected_paramter_info(
                                            param_acronyms=paramlist_fortsmith)
            param_info['fort_smith'] = pinfo

            paramlist_vicksburg = ['Gamma', 'RTDM', 'RRCM', 'LKDep', 'WLDep',
                                   'SWOC', 'PTCH', 'SNMT', 'GWFM', 'GWAM']
            pinfo = ParameterInfo.get_selected_paramter_info(
                                            param_acronyms=paramlist_vicksburg)
            param_info['vicksburg'] = pinfo

            paramlist_mississippi = ['Gamma', 'RTDM', 'RRCM', 'LKDep', 'WLDep',
                                     'SWOC', 'PTCH', 'SNMT', 'GWAM']
            pinfo = ParameterInfo.get_selected_paramter_info(
                                            param_acronyms=paramlist_mississippi)
            param_info['mississippi'] = pinfo

            param_info = ParameterInfo.GlobalCDA.update_multibasin_parameter_acronym(
                                                                    param_info)

            return param_info

        @staticmethod
        def GBB_all_parameters():
            param_info = ParameterInfo.get_parameter_info()

            t = param_info.pop('net_radiation_mult')
            t = param_info.pop('precip_mult')

            return param_info

        @staticmethod
        def GBB_selected_parameters():
            param_info = OrderedDict()

            params_gan = [
                'precip_mult', 'PT_coeff_humid','gammaHBV_runoff_coeff', 
                'root_depth_multiplier', 'river_roughness_coeff_mult', 
                'wetland_depth', 'surfacewater_outflow_coefficient',
                'rg_max_mult', 'net_abstraction_surfacewater_mult',
                'net_abstraction_groundwater_mult'
            ]

            params_brh = [
                'precip_mult', 'PT_coeff_humid', 'snow_freeze_temp', 
                'snow_melt_temp', 'degree_day_factor_mult', 
                'temperature_gradient', 'gammaHBV_runoff_coeff', 'root_depth_multiplier', 
                'river_roughness_coeff_mult', 'lake_depth', 'wetland_depth', 
                'surfacewater_outflow_coefficient', 
                'gw_factor_mult', 'rg_max_mult', 
                'groundwater_outflow_coeff', 'net_abstraction_groundwater_mult'
            ]

            t = ParameterInfo.get_selected_paramter_info(param_names=params_gan)
            param_info['ganges'] \
            = ParameterInfo.GlobalCDA.update_parameter_acronym(t)

            t = ParameterInfo.get_selected_paramter_info(param_names=params_brh)
            param_info['brahmaputra'] \
            = ParameterInfo.GlobalCDA.update_parameter_acronym(t)
            
            return param_info

        @staticmethod
        def GBB_sensitive_parameters():
            param_info = OrderedDict()

            ## add sensitive parameters of ganges
            params_gan = ['Gamma', 'RTDM', 'RRCM', 'WLDep', 'SWOC', 'PTCH', 'GWFM',
                          'MRGM', 'GWOC', 'SWAM', 'GWAM', 'PrecipM']
            temp = ParameterInfo.get_selected_paramter_info(
                                                      param_acronyms=params_gan)
            temp['surfacewater_outflow_coefficient']['log_scale'] = True
            param_info['ganges'] = temp
            ##

            ## add sensitive parameters of brahmaputra
            params_brh = ['Gamma', 'RTDM', 'RRCM', 'WLDep', 'SWOC', 'PTCH',
                          'SNMT', 'TempG', 'GWFM', 'MRGM', 'GWOC', 'PrecipM']
            temp = ParameterInfo.get_selected_paramter_info(
                                                      param_acronyms=params_brh)
            temp['surfacewater_outflow_coefficient']['log_scale'] = True
            param_info['brahmaputra'] = temp
            ##

            return param_info

        @staticmethod
        def influential_parameters_EuropeanBasins(experiment_id='SA-QTG'):

            sa_params = OrderedDict()
            if experiment_id == 'SA-QTG': # 3-variable SA using Q, TWSA, and GWSA
                sa_params['seine'] = ['Gamma', 'RTDM', 'PTCH', 'GWFM', 'MRGM',
                                      'GWOC', 'GWAM', 'PrecipM']

            parameters = OrderedDict()
            for basin in sa_params.keys():
                temp = ParameterInfo.get_selected_paramter_info(
                                                param_acronyms=sa_params[basin])
                parameters[basin] = temp

            parameters = ParameterInfo.GlobalCDA.update_multibasin_parameter_acronym(
                                                                            parameters)

            return parameters

        @staticmethod
        def FGB_sensitive_parameters(expid='SA-QTG'):

            params = OrderedDict()
            if expid == 'SA-QTG':
                params['elbe'] = ['Gamma', 'RTDM', 'PTCH','SNMT','GWFM','MRGM',
                                  'GWOC', 'PrecipM']
                params['weser'] = ['Gamma','RTDM','PTCH','MRGM','GWOC', 'PrecipM']
                params['rhine'] = ['Gamma','RTDM','PTCH','SNMT','GWFM','MRGM',
                                   'GWOC', 'PrecipM']
                params['meuse'] = ['Gamma','RTDM','WLDep','PTCH','GWFM','MRGM',
                                   'GWOC', 'PrecipM']
                params['seine'] = ['Gamma','RTDM','PTCH', 'GWFM', 'MRGM','GWOC',
                                   'GWAM', 'PrecipM']
                params['rhone'] = ['Gamma','RTDM','LKDep','SWOC','PTCH','SNMT',
                                   'GWFM','MRGM','GWOC', 'PrecipM']
                params['loire'] = ['Gamma','RTDM','PTCH','GWFM','GWOC', 'PrecipM']
                params['vilaine'] = ['Gamma','RTDM','PTCH','GWFM','MRGM','GWOC',
                                      'PrecipM']
                params['garonne'] = ['Gamma','RTDM','PTCH','GWFM','MRGM',
                                      'GWOC','SWAM', 'PrecipM']
                params['adour'] = ['Gamma','RTDM','MRGM','GWOC','SWAM',
                                   'PrecipM']

            param_info = OrderedDict()
            for basin in params.keys():
                temp = ParameterInfo.get_selected_paramter_info(
                                                param_acronyms=params[basin])
                param_info[basin] = temp

            param_info = ParameterInfo.GlobalCDA.update_multibasin_parameter_acronym(
                                                                    param_info)

            return param_info
