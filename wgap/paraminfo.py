import pandas as pd
from collections import OrderedDict

class ParameterInfo:
    __param_info = OrderedDict()
    __param_info['gammaHBV_runoff_coeff'] = {
                'description': 'Runoff Coefficient',
                'acronym': 'Gamma',
                'log_scale': False,
                'min': 0.3,
                'max': 3.0,
                'nominal': 0.7,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['root_depth_multiplier'] = {
                'description': 'Root Depth Multiplier',
                'acronym': 'RTDM',
                'log_scale': False,
                'min': 0.5,
                'max': 3.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['river_roughness_coeff_mult'] = {
                'description': 'River Roughness Coefficient Multiplier',
                'acronym': 'RRCM',
                'log_scale': False,
                'min': 1.0,
                'max': 5.0,
                'nominal': 3,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['lake_depth'] = {
                'description': 'Lake Depth',
                'acronym': 'LKDep',
                'log_scale': False,
                'min': 1.0,
                'max': 20.0,
                'nominal': 5,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['wetland_depth'] = {
                'description': 'Wetland Depth',
                'acronym': 'WLDep',
                'log_scale': False,
                'min': 1.0,
                'max': 20.0,
                'nominal': 2.0,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['surfacewater_outflow_coefficient'] = {
                'description': 'Surface Water Outflow Coefficient',
                'acronym': 'SWOC',
                'log_scale': False,
                'min': 0.001,
                'max': 0.1,
                'nominal': 0.01,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['evapo_red_fact_exp_mult'] = {
                'description': 'Evaporation Reduction Factor Exponent Multiplier',
                'acronym': 'ERFM',
                'log_scale': False,
                'min': 0.33,
                'max': 1.5,
                'nominal': 1,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['net_radiation_mult'] = {
                'description': 'Net Radiation Multiplier',
                'acronym': 'NRDM',
                'log_scale': False,
                'min': 0.5,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['PT_coeff_humid'] = {
                'description': 'PT-Coefficient - Humid',
                'acronym': 'PTCH',
                'log_scale': False,
                'min': 0.885,
                'max': 1.65,
                'nominal': 1.26,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['PT_coeff_arid'] = {
                'description': 'PT-Coefficient - Arid',
                'acronym': 'PTCA',
                'log_scale': False,
                'min': 1.365,
                'max': 2.115,
                'nominal': 1.74,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['max_daily_PET'] = {
                'description': 'Max Daily PET',
                'acronym': 'MDPET',
                'log_scale': False,
                'min': 6.0,
                'max': 22.0,
                'nominal': 15.0,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['mcwh'] = {
                'description': 'Maximum Canopy Water Height',
                'acronym': 'MCWH',
                'log_scale': False,
                'min': 0.1,
                'max': 1.4,
                'nominal': 0.3,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['LAI_mult'] = {
                'description': 'LAI Multiplier',
                'acronym': 'LAIM',
                'log_scale': False,
                'min': 0.2,
                'max': 2.5,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['snow_freeze_temp'] = {
                'description': 'Snow Freeze Temperature  ',
                'acronym': 'SNFT',
                'log_scale': False,
                'min': -1,
                'max': 3.0,
                'nominal': 2.0,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['snow_melt_temp'] = {
                'description': 'Snow Melt Temperature',
                'acronym': 'SNMT',
                'log_scale': False,
                'min': -3.75,
                'max': 3.75,
                'nominal': 0.0,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['degree_day_factor_mult'] = {
                'description': 'Degree Day Factor Multiplier',
                'acronym': 'DDFM',
                'log_scale': False,
                'min': 0.5,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['temperature_gradient'] = {
                'description': 'Temperature Gradient',
                'acronym': 'TempG',
                'log_scale': False,
                'min': 0.001,
                'max': 0.01,
                'nominal': 0.006,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['gw_factor_mult'] = {
                'description': 'Groundwater Factor Multiplier',
                'acronym': 'GWFM',
                'log_scale': False,
                'min': 0.3,
                'max': 3.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['rg_max_mult'] = {
                'description': 'Maximum Groundwater Recharge Factor Multiplier',
                'acronym': 'MRGM',
                'log_scale': False,
                'min': 0.3,
                'max': 3.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['pcrit_aridgw'] = {
                'description': 'Critical Precipitation for GW - Arid Zone',
                'acronym': 'CPGW',
                'log_scale': False,
                'min': 2.5,
                'max': 20.0,
                'nominal': 12.5,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['groundwater_outflow_coeff'] = {
                'description': 'Groundwater Outflow Coefficient',
                'acronym': 'GWOC',
                'log_scale': False,
                'min': 0.001,
                'max': 0.02,
                'nominal': 0.01,
                'optimal': None,
                'distribution': 'uniform'
    }

    __param_info['net_abstraction_surfacewater_mult'] = {
                'description': 'Net Surfacewater Abstraction Multiplier ',
                'acronym': 'SWAM',
                'log_scale': False,
                'min': -2.0,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['net_abstraction_groundwater_mult'] = {
                'description': 'Net Groundwater Abstraction Multiplier',
                'acronym': 'GWAM',
                'log_scale': False,
                'min': -2.0,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
    }

    __param_info['precip_mult'] = {
                'description': 'Precipitation Multiplier',
                'acronym': 'PrecipM',
                'log_scale': False,
                'min': 0.5,
                'max': 2.0,
                'nominal': 1.0,
                'optimal': None,
                'distribution': 'triangular'
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
        def update_parameter_acronym(parameter_info):
            acronyms = ParameterInfo.GlobalCDA.parameter_acronyms

            for basin in parameter_info.keys():
                for param, info in parameter_info[basin].items():
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

            param_info = ParameterInfo.GlobalCDA.update_parameter_acronym(
                                                                    param_info)

            return param_info

        @staticmethod
        def GBB_all_parameters():
            param_info = ParameterInfo.get_parameter_info()

            t = param_info.pop('net_radiation_mult')
            t = param_info.pop('precip_mult')

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
        def GFB_sensitive_parameters(expid='SA-QTG'):

            params = OrderedDict()
            if expid == 'SA-QTG':
                params['elbe'] = ['Gamma', 'RTDM', 'PTCH','SNMT','GWFM','MRGM',
                                  'GWOC', 'PrecipM']
                params['weser'] = ['Gamma','RTDM','PTCH','MRGM','GWOC', 'PrecipM']
                params['rhine'] = ['Gamma','RTDM','PTCH','SNMT','GWFM','MRGM',
                                   'GWOC', 'PrecipM']
                params['meuse'] = ['Gamma','RTDM','WLDep','PTCH','GWFM','MRGM',
                                   'GWOC', 'PrecipM']
                params['seine'] = ['Gamma','RTDM','PTCH','MRGM','GWOC','GWAM',
                                   'PrecipM']
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

            param_info = ParameterInfo.GlobalCDA.update_parameter_acronym(
                                                                    param_info)

            return param_info
