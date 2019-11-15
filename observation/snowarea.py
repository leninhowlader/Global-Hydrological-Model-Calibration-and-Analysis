# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 15:26:49 2019

@author: mhasan

@remarks: 
    Snow Coverage:
    In WGHM, snow cover fraction is calculated as the percent of continental area
    cover with snow. In order to compare the snow cover observations with model
    predictions, the observations must be converted to equivalent contianal 
    areal coverage (fraction) of snow. This conversion can be done by (1)
    
    SN_fcon = A_sn / (AF_con * A)           ... ... ... ... ... ... ... ... (1)
    where,
        SN_fcon = Snow areal coverage of continental area
        A_sn    = (Observed) Snow area
        AF_con  = Continental area fraction
        A       = Actural Area of a Cell
    
    Basin Average:
    Basin average should be computed using weighted average mean like (2)
    
    SN_bf  = (SN_fcon_1 * A_con_1 + SN_fcon_2 * A_con_2 + ....) 
             / (A_con_1 + A_con_2 + ...)                           ... ... (2)
           = (A_sn_1 + A_sn_2 + ....) / (A_con_1 + A_con_2 + ...)  
           = total_snow_area / total_continental_area              ... ... (3)
    where,
        SN_bf       = Basin average of snow fraction
        SN_fcon_i   = Fraction of continental area covered with snow in i-th
                      cell
        A_con_i     = Continental area of i-th cell which can be calculated
                      as (AF_con * A)
"""


import os, sys, numpy as np, pandas as pd
from collections import OrderedDict

sys.path.append('F:/mhasan/Code&Script/ProjectWGHM')
from wgap.wgapio import WaterGapIO

class SnowCoverage:
    class GlobalCDA_DLR:
        @staticmethod
        def load_data(filename):
            df = pd.read_csv(filename, sep=' ')
        
            # read year and month from yyyy_mm column
            years = df.iloc[:,0].apply(lambda x: int(x[:4]))
            months = df.iloc[:,0].apply(lambda x: int(x[5:]))
            
            df.drop(df.columns[0], axis=1, inplace=True)
            
            df.insert(loc=0, value=months, column='month')
            df.insert(loc=0, column='year', value=years)
            
            df.columns = ['year', 'month', 'arcid', 'snowarea', 'pos_unc', 
                          'neg_unc']
            
            return df
        
        @staticmethod
        def compute_snow_area_fraction(snow_data:pd.DataFrame, 
                                       basin_info:OrderedDict,
                                       compute_continental_snow_coverage=True,
                                       apply_basin_summary:bool=True):
            
            # inner function to build data frame from basin info
            def basin_info_data_frame():
                df = pd.DataFrame()
                
                for basin in basin_info.keys():
                    cindex = np.array(basin_info[basin]['upstream']) - 1
                    arcid = basin_info[basin]['arcid']
                    area = basin_info[basin]['area'].byteswap().newbyteorder()
                    
                    ncell = len(arcid)
                    name = np.array([basin] * ncell)
                    
                    temp = pd.DataFrame({'basin': name, 'arcid': arcid, 
                                         'cindex': cindex, 'area': area})
    
                    df = df.append(temp)
                    
                return df
            # end of inner function
            
            # create basin data frame with necessary data
            basin_data = basin_info_data_frame()
            
            # merge snow and basin data frames
            snow_data = snow_data.merge(basin_data, how='inner', on='arcid')
            
            
            # step: compute continental area if required
            if compute_continental_snow_coverage:
                af_con = WaterGapIO.compute_continental_area_fraction()
                if af_con.shape[0] == 0: return np.empty(0)
                
                ii = snow_data['cindex'].values
                snow_data['area'] = snow_data['area'] * af_con[ii]
                
            snow_data['area'] = snow_data['area'] * 10**6   # km2 to m2
            # end of step
            
            
            # remove unneccessary data
            snow_data.drop(columns=['arcid', 'cindex'], inplace=True)
            
            
            # step: compute basin summary when applicable
            if apply_basin_summary:
                snow_data = snow_data.groupby(
                                        by=['basin', 'year', 'month']).sum()
                snow_data.reset_index(inplace=True)
            # end of step
            
            # step: compute snow cover fraction
            snow_af = snow_data['snowarea'] / snow_data['area']
            pos_unc = snow_data['pos_unc'] / snow_data['area']
            neg_unc = snow_data['neg_unc'] / snow_data['area']
            # end of step
            
            # step: prepare output data
            df = snow_data[['basin', 'year', 'month']].copy(deep=True)
            df['snow_frc'] = snow_af
            df['pos_unc'] = pos_unc
            df['neg_unc'] = neg_unc
            # end of step
            
            return df

        
        @staticmethod
        def read_snow_coverage_data(basin_info, 
                                    data_directory,
                                    start_year,
                                    end_year,
                                    compute_snow_fraction=True,
                                    compute_continental_areal_fraction=True,
                                    apply_basin_summary=True,
                                    filename_format='%d.txt'):
            
            snow_data = pd.DataFrame()
            
            # step: read snow data
            for year in range(start_year, end_year + 1):
                filename = os.path.join(data_directory, 
                                        eval('filename_format%' + str(year)))
                
                df = SnowCoverage.GlobalCDA_DLR.load_data(filename)
                snow_data = snow_data.append(df)
            
            if snow_data.shape[0] == 0: return snow_data
            # end of step
            
            # step: compute snow fraction
            if (compute_snow_fraction):
                snow_data = \
                        SnowCoverage.GlobalCDA_DLR.compute_snow_area_fraction(
                                snow_data, basin_info, 
                                compute_continental_snow_coverage
                                =compute_continental_areal_fraction,
                                apply_basin_summary=apply_basin_summary)
            # end of step
            
            return snow_data
        # end of function
        
    # end of GlobalCDA_DLR class
        
    # Attributes and Methods of SnowCoverage Class _____________________________
    @staticmethod
    def land_area_fraction(years:list=[]):
        land_af = np.empty(0)
        if len(years) > 0:
            start_year, end_year = years[0], years[-1]
            
            land_af = WaterGapIO.compute_land_area_fraction(start_year, 
                                                            end_year)
            
        if land_af.shape[0] == 0: 
            land_af = WaterGapIO.compute_land_area_fraction()
        
        return land_af

