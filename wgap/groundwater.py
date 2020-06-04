import os, numpy as np

class GroundWater():
    # input array
    soil_texture = np.array([])
    permafrost_glacier = np.array([])
    aquifer = np.array([])
    slope = np.array([])
    
    # factors
    factor_soil_texture = np.array([])
    factor_permafrost_glacier = np.array([])
    factor_aquifer = np.array([])
    factor_slope = np.array([])
    factor_rgmax = np.array([])                 # soil texture specific max. GW recharge fraction
    factor_rg = np.array([])
    
    # multipliers
    multiplier_rgmax = np.array([])
    multiplier_rg = np.array([])
    
    # flags
    flag_rgmax_multiplier = False               # flag to show if rgmax multiplier has been applied
    flag_rg_multiplier = False                  # flag showing if rg (recharge factor) multiplier has already been applied
    
    # WGHM Home Directory
    wghm_home_directory = ''

    def __init__(self): pass

    @staticmethod
    def set_rgmax_multiplier(multiplier): 
        GroundWater.multiplier_rgmax = multiplier
        GroundWater.flag_rgmax_multiplier = False
        GroundWater.factor_rgmax = np.array([])
    
    @staticmethod
    def set_rg_multiplier(multiplier): 
        GroundWater.multiplier_rg = multiplier
        GroundWater.flag_rg_multiplier = False
        GroundWater.factor_rg = np.array([])
    
    @staticmethod
    def apply_rg_multiplier():
        succeed = False
        
        if not GroundWater.flag_rg_multiplier:
            if GroundWater.multiplier_rg.size > 0 and GroundWater.multiplier_rg.size == GroundWater.factor_rg.size:
                GroundWater.factor_rg = GroundWater.factor_rg * GroundWater.multiplier_rg
                GroundWater.flag_rg_multiplier = True
                succeed = True
        
        return succeed
    
    @staticmethod
    def apply_rgmax_multiplier():
        succeed = False
        
        if not GroundWater.flag_rgmax_multiplier:
            if GroundWater.multiplier_rgmax.size > 0 and GroundWater.multiplier_rgmax.size == GroundWater.factor_rgmax.size:
                GroundWater.factor_rgmax = GroundWater.factor_rgmax * GroundWater.multiplier_rgmax
                GroundWater.flag_rgmax_multiplier = True
                succeed = True
        
        return succeed
    
    
    @staticmethod
    def get_soil_texture(filename='INPUT/G_TEXTURE.UNF1'):
        if GroundWater.wghm_home_directory:
            filename = os.path.join(GroundWater.wghm_home_directory, filename)

        if GroundWater.soil_texture.size == 0: 
            try: GroundWater.soil_texture = np.fromfile(filename, dtype='>b')
            except Exception as ex: print(str(ex)) 
        
        return GroundWater.soil_texture
    
    @staticmethod
    def get_factor_soil_texture():
        if GroundWater.factor_soil_texture.size == 0:
            # step-1: get soil texture data
            t = GroundWater.get_soil_texture()
            
            # step-2: calculate soil texture related factor, only if soil texture data is availale
            if t.size > 0:
                f = np.zeros(len(t), dtype=np.float32)
                
                
                # Case-1: texture = 1
                # f[t==1] = 0        # default value is zero
                
                # Case-2: texture <= 0
                f[t<=0] = 0.95
                
                # Case-3: 10 >= soil texture <= 30
                # in this case, textures have been grouped into two classes 10-20 and 20-30 with predefined texture
                # specific factor value ranges for each class. Within a group, the factor value is linearly interpolated.
                texture_table = [10, 20, 30]
                texFac_table = [1.0, 0.95, 0.7]
                for i in range(len(texture_table)-1):
                    t1, t2 = texture_table[i], texture_table[i+1]
                    f1, f2 = texFac_table[i], texFac_table[i+1]
                    
                    f[(t>=t1)&(t<=t2)] = f1 + ((f2 - f1) / (t2 - t1)) * (t[(t>=t1)&(t<=t2)] - t1)
                
                # Case-4: otherwise
                # error in input soil texture file (G_TEXTURE.UNF1)
                # if (t[(t>=2)&(t<10)].size + t[t>30].size) > 0: print('Error in "G_TEXTURE.UNF1" input file!')
                
                # step-3: impose limit (factor value must be between 0 and 1)
                # f[f<0] = 0
                # f[f>1] = 1
                GroundWater.factor_soil_texture = f
        
        # step-4: return soil texture related factor
        return GroundWater.factor_soil_texture
        
    @staticmethod
    def get_permafrost_glacier(filename='INPUT/G_PERMAGLAC.UNF1'):
        if GroundWater.wghm_home_directory:
            filename = os.path.join(GroundWater.wghm_home_directory, filename)

        if GroundWater.permafrost_glacier.size == 0:
            try: 
                temp = np.fromfile(filename, dtype='>b')
                if temp.size > 0:  GroundWater.permafrost_glacier = temp
            except Exception as ex: print(str(ex))
        
        return GroundWater.permafrost_glacier
    
    @staticmethod
    def get_factor_permafrost_glacier():
        if  GroundWater.factor_permafrost_glacier.size == 0:
            pg = GroundWater.get_permafrost_glacier()
            if pg.size > 0:
                f = 1 - (pg/100.0)
                
                f[f<0] = 0
                f[f>1] = 1
                GroundWater.factor_permafrost_glacier = f
        
        return GroundWater.factor_permafrost_glacier
        
    @staticmethod
    def get_aquifer_data(filename='INPUT/G_AQ_FACTOR.UNF1'):
        if GroundWater.wghm_home_directory:
            filename = os.path.join(GroundWater.wghm_home_directory, filename)

        if GroundWater.aquifer.size == 0:
            try:
                temp = np.fromfile(filename, dtype='>b')
                if temp.size > 0: GroundWater.aquifer = temp
            except Exception as ex: print(str(ex))
        
        return GroundWater.aquifer
    
    @staticmethod
    def get_factor_aquifer():
        if GroundWater.factor_aquifer.size == 0:
            a = GroundWater.get_aquifer_data()
            if a.size > 0:
                f = a/100.0
                
                f[f<0] = 0
                f[f>1] = 1
                GroundWater.factor_aquifer = f
        
        return GroundWater.factor_aquifer
    
    @staticmethod
    def get_slope_data(filename='INPUT/G_SLOPE_CLASS.UNF1'):
        if GroundWater.wghm_home_directory:
            filename = os.path.join(GroundWater.wghm_home_directory, filename)

        if GroundWater.slope.size == 0:
            try:
                temp = np.fromfile(filename, dtype='>b')
                if temp.size > 0: GroundWater.slope = temp
            except Exception as ex: print(str(ex))
            
        return GroundWater.slope
    
    @staticmethod
    def get_factor_slope():
        if GroundWater.factor_slope.size == 0:
            s = GroundWater.get_slope_data()
            if s.size > 0:
                f = np.zeros(s.size, dtype='f')
                
                # Case-I: slope = 0
                f[s==0] = 1.0
                
                # Case-II: 10 <= slope <= 70
                # in this case, slopes will be devided into 6 classes. within a class factor values is calculated 
                # using linear interpolation
                slope_table = [10, 20, 30, 40, 50, 60, 70]
                fac_table = [1.00, 0.95, 0.90, 0.75, 0.60, 0.30, 0.15]
                for i in range(len(slope_table)-1):
                    s1, s2 = slope_table[i], slope_table[i+1]
                    f1, f2 = fac_table[i], fac_table[i+1]
                    
                    f[(s>=s1)&(s<=s2)] = f1 + (((f2 - f1)/ (s2 - s1)) * (s[(s>=s1)&(s<=s2)] - s1))
                    
                # Case-III: otherwise
                # no information avialable for this case
                
                GroundWater.factor_slope = f
        
        return GroundWater.factor_slope
    
    @staticmethod
    def get_factor_texture_specific_max_recharge_rgmax(used_time_series=0):
        if GroundWater.factor_rgmax.size == 0:
            t = GroundWater.get_soil_texture()
            if t.size > 0:
                f = np.zeros(t.size)
                
                # Case-1: soil texture <= 0 or 2 (assuming ?undefined texture classes as class-20)
                f[t<=0] = 3.0
                f[t==2] = 3.0
                # note: the rgmax value should be changed to 4.5 for using daily WFD input files
                # according to BSc thesis Toege. in the model code, however, the value was not 
                # updated for the current case (i.e., soil texture <= 0 or equals to 2)
                
                # Case-2: soil texture = 1
                # f[t==0] = 0       # the default rgmax value is zero, thus this line of code is not necessary
                
                # Case-3: 10 >= soil texture <= 30
                # in this case, texture has been grouped into two classes 10-20 and 20-30 with rgmax value ranges
                # for each class. Within a group, rgmax value is linearly interpolated.
                texture_table = [10, 20, 30]
                rgmax_table = [5, 3, 1.5]           # the standard values for each soil texture class;
                                                    # however, if the model uses daily WFD input files
                                                    # rgmax values should be changed to 7, 4.5 and 2.5 
                                                    # respectively [according to BSc Thesis of Toege]
                if used_time_series == 0: rgmax_table = [7, 4.5, 2.5]
                
                for i in range(len(texture_table)-1):
                    t1, t2 = texture_table[i], texture_table[i+1]
                    f1, f2 = rgmax_table[i], rgmax_table[i+1]
                    
                    f[(t>=t1)&(t<=t2)] = f1 + ((f2-f1)/(t2-t1)) * (t[(t>=t1)&(t<=t2)]-t1)
                
                # Case-4: otherwise
                # no information is available 
                
                GroundWater.factor_rgmax = f
        
        return GroundWater.factor_rgmax
    
    
    @staticmethod
    def get_recharge_factor():
        if GroundWater.factor_rg.size == 0:
            fs, ft = GroundWater.get_factor_slope(), GroundWater.get_factor_soil_texture()
            fa, fp = GroundWater.get_factor_aquifer(), GroundWater.get_factor_permafrost_glacier()
            
            if fs.size == ft.size == fa.size == fp.size:
                rg = fs * ft * fa * fp
                GroundWater.factor_rg = rg
        
        # apply multiplier if available
        GroundWater.apply_rg_multiplier()
        
        return GroundWater.factor_rg

