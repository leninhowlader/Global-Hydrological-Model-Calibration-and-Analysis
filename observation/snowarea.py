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
        def read_data(filename):
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
                                       use_landarea_fraction=False,
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
            
            if use_landarea_fraction:
                years = np.unique(snow_data.year.values)
                land_af = SnowCoverage.land_area_fraction(years)
                
                if land_af.shape[1] == 1:
                    ii = snow_data['cindex'].values
                    laf = land_af[ii]
                    
                    snow_data['snowarea'] = snow_data['snowarea'] * laf
                    snow_data['pos_unc'] = snow_data['pos_unc'] * laf
                    snow_data['neg_unc'] = snow_data['neg_unc'] * laf
                else:
                    for i in range(land_af.shape[1]):
                        ii = np.where(snow_data['year'].values==years[i])[0]
                        jj = snow_data['cindex'][ii].values
                        laf = land_af[jj, i]
                        
                        snow_data.loc[ii, 'snowarea'] = snow_data['snowarea'][ii] * laf
                        snow_data.loc[ii, 'pos_unc'] = snow_data['pos_unc'][ii] * laf
                        snow_data.loc[ii, 'neg_unc'] = snow_data['neg_unc'][ii] * laf       
            
            # remove unneccessary data
            # snow_data.drop(columns=['arcid', 'cindex'], inplace=True)
            
            
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
            if not apply_basin_summary: df['cellnum'] = snow_data['cindex'] + 1
            
            df['snow_frc'] = snow_af
            df['pos_unc'] = pos_unc
            df['neg_unc'] = neg_unc
            # end of step
            
            return df

        
        @staticmethod
        def acquire_snow_coverage_data(basin_info, 
                                    data_directory,
                                    start_year,
                                    end_year,
                                    compute_snow_fraction=True,
                                    compute_continental_areal_fraction=True,
                                    apply_basin_summary=True,
                                    use_land_area_fraction = False,
                                    filename_format='%d.txt'):
            
            snow_data = pd.DataFrame()
            
            # step: read snow data
            for year in range(start_year, end_year + 1):
                filename = os.path.join(data_directory, 
                                        eval('filename_format%' + str(year)))
                
                df = SnowCoverage.GlobalCDA_DLR.read_data(filename)
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
                                apply_basin_summary=apply_basin_summary,
                                use_landarea_fraction=use_land_area_fraction)
                            
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
            
            if start_year <= 2012:
                n = 0
                if end_year > 2012: 
                    n = end_year - 2012
                    end_year = 2012
                
                land_af = WaterGapIO.compute_land_area_fraction(start_year, 
                                                                end_year)
                if n > 0:
                    cndx = [-1] * n
                    land_af = np.concatenate((land_af, land_af[:, cndx]), axis=1)
            
        if land_af.shape[0] == 0: 
            land_af = WaterGapIO.compute_land_area_fraction()
        
        return land_af
    # end of function
    
    
    @staticmethod
    def read_snow_cover_predictions(model_output_directory,
                                    basin_info,
                                    start_year,
                                    end_year, 
                                    calculate_basin_summary=False,
                                    model_input_directory=''):
    
        # inner function to read continental area fraction of basin cells
        def get_continental_area():
            WaterGapIO.set_model_input_data_directory(model_input_directory)
            
            basin_data = pd.DataFrame()
            
            cont_area_frc = WaterGapIO.compute_continental_area_fraction()
            if cont_area_frc.shape[0] == 0: return basin_data
            
            for basin in basin_info.keys():
                try:
                    station_id = basin_info[basin]['station_id']
                    
                    upstream = np.array(basin_info[basin]['upstream'],
                                        dtype=int)
                    cellindex = upstream - 1
                    cont_af = cont_area_frc[cellindex]
                    
                    tmp = pd.DataFrame({'basin': basin, 
                                        'station_id': station_id,
                                        'cellnum': upstream, 
                                        'cont_af': cont_af})
                    
                    basin_data = basin_data.append(tmp)
                except: return basin_data
            
            return basin_data
        # end of inner function
        
        snow_cover = pd.DataFrame()
        
        # step: check inputs
        if not os.path.exists(model_output_directory): return snow_cover
        if not (start_year >= 1901 and 
                end_year >= 1901 and 
                start_year <= end_year):
            return snow_cover
        
        basin_cont_area = pd.DataFrame()
        if calculate_basin_summary:
            if not model_input_directory: return snow_cover
            
            basin_cont_area = get_continental_area()
            if basin_cont_area.shape[0] == 0: return snow_cover
        # end of step    
        
        # step: find target cells
        cellnum = np.array([])
        for basin in basin_info.keys():
            try:
                upstream = np.array(basin_info[basin]['upstream'],
                                    dtype=int)
                cellnum = np.concatenate((cellnum, upstream), axis=0)
            except: return snow_cover
        
        if cellnum.shape[0] == 0: return snow_cover
        # end of step
        
        # step: read snow cover predictions for basin cells
        cellndx = (cellnum - 1).astype(int)
        
        ncells = len(cellnum)
        m = np.array(list(range(1, 12 + 1)) * ncells).reshape(-1, 1)
        cn = np.array(cellnum.tolist() * 12).reshape(12, -1).transpose()
        cn = cn.flatten().reshape(-1, 1)
    
        r = None 
        for year in range(start_year, end_year + 1):
            filename = os.path.join(model_output_directory, 
                                    'G_SNOW_COVER_FRAC_%d.12.UNF0'%year)
            d = WaterGapIO.read_unf(filename)
            
            y = np.array([year] * 12 * ncells).reshape(-1, 1)   # year index
            ic = np.concatenate((cn, y, m), axis=1)             # index columns
            
            d0 = d[cellndx,:].flatten().reshape(-1, 1)
            
            d1 = np.concatenate((ic, d0), axis=1)
            
            try: r = np.concatenate((r, d1), axis=0)
            except: r = d1
            
        columns = ['cellnum', 'year', 'month', 'snow_frc']
        snow_cover = pd.DataFrame(data=r, columns=columns)
        # end of step
        
        # step: summarize snow cover for each basin
        if calculate_basin_summary:
            snow_cover = pd.merge(snow_cover, basin_cont_area, on='cellnum')
            snow_cover.loc[:, 'snow_frc'] = snow_cover.snow_frc * snow_cover.cont_af
            snow_cover.drop(columns=['cellnum'], inplace=True)
            
            snow_cover = snow_cover.groupby(by=['basin', 'station_id', 
                                                'year', 'month']).sum()
            snow_cover.reset_index(inplace=True)
            
            snow_cover.loc[:, 'snow_frc'] = snow_cover.snow_frc / snow_cover.cont_af
            snow_cover.drop(columns='cont_af', inplace=True)
        # end of step
        
        return snow_cover
    # end of function
    
    
    @staticmethod
    def plot_snow_cover_data(basin_info:OrderedDict,
                             snow_cover_obs:pd.DataFrame,
                             snow_cover_sim:pd.DataFrame=pd.DataFrame(),
                             save_figures=True,
                             output_directory='',
                             legend_bbox_to_anchor=(0, -0.25)):
        
        # import libraries
        from datetime import date
        from calendar import monthrange
        from matplotlib import pyplot as plt
        
        # inner function to find monthend data
        def monthenddate(year, month): 
            day = monthrange(year, month)[1]
            return date(year, month, day)
        # end of inner function
        
        # inner function to find polygon points with uncertainty region
        def polypoints(x, y, y_plus, y_minus):
            y1 = y + y_plus
            y2 = y - y_minus
            
            X = np.concatenate((x, list(reversed(x))), axis=0)
            Y = np.concatenate((y1, list(reversed(y2))), axis=0)
            return X, Y
        # end of inner function
        
        d = snow_cover_obs.loc[:, ['year', 'month']].values
        dates = [monthenddate(int(x[0]), int(x[1])) for x in d]
        snow_cover_obs['date'] = dates
        
        if snow_cover_sim.shape[0] > 0:
            d = snow_cover_sim.loc[:, ['year', 'month']].values
            dates = [monthenddate(int(x[0]), int(x[1])) for x in d]
            snow_cover_sim['date'] = dates
        
        for basin in basin_info.keys():
            d = snow_cover_obs.loc[snow_cover_obs.basin==basin,:]
            
            x, y = d.date.values, d.snow_frc.values
            
            X, Y = polypoints(x, y, d.pos_unc.values, d.neg_unc.values)
            
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(1, 1, 1)
            ax.fill(X, Y, color='lightgrey', zorder=1, 
                    label='Observed Uncertainty')
            ax.plot(x, y, color='blue', linestyle='-', linewidth=1.2, zorder=2,
                    label='Observations')
            
            # add model snow cover
            if snow_cover_sim.shape[0] > 0:
                d = snow_cover_sim.loc[snow_cover_sim.basin==basin,:]
                x, y = d.date.values, d.snow_frc.values
                ax.plot(x, y, color='red', linestyle='--', zorder=3,
                        label='Predictions')
            
            ax.set_ylabel('% of continental area covered\nwith snow', fontsize=20,
                          color='black')
            ax.set_title('DLR - Snow Coverage Observations in %s'%basin.title(), 
                         fontsize=22)
            
            ax.yaxis.set_tick_params(labelsize=16, labelcolor='black')
            ax.xaxis.set_tick_params(labelsize=16, labelcolor='black')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
            
            # add legend
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = OrderedDict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc='lower left',
                      ncol=4, bbox_to_anchor=legend_bbox_to_anchor,
                      frameon=False, fontsize=18, columnspacing=0.5)
            
            fig.tight_layout()
            
            if save_figures:
                filename = os.path.join(output_directory, '%s.png'%basin)
                fig.savefig(filename, dpi=600)
        
        return True
