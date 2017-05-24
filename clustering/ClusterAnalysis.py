import sys
sys.path.append('..')
from utilities.fileio import read_UNF_file
from utilities.grid import grid
import shapefile as shp, numpy as np


filename_landcover = '../wgap_home/INPUT/G_LANDCOVER.UNF1'
filename_elevation = '../wgap_home/INPUT/G_ELEV_RANGE.101.UNF2'
filename_TAWC = '../wgap_home/INPUT/G_TAWC.UNF0' # total available water capacity
filename_GLakeFrc = '../wgap_home/INPUT/G_GLOLAK.UNF0'
filename_GWetLandFrc = '../wgap_home/INPUT/G_GLOWET.UNF0'
filename_LLakeFrc = '../wgap_home/INPUT/G_LOCLAK.UNF0'
filename_LWetLandFrc = '../wgap_home/INPUT/G_LOCWET.UNF0'
output_filename = '/media/sf_mhasan/private/month_data/wghm_grid3.shp'


def main():
    global  filename_landcover, filename_elevation, filename_TAWC, filename_GLakeFrc, filename_GWetLandFrc
    global filename_LLakeFrc, filename_LWetLandFrc, output_filename

    # read wghm 0.5 degree grid centroid
    succeed = True
    wghm_centroids = grid.get_wghm_world_grid_centroids()
    if wghm_centroids: ng = len(wghm_centroids)
    else:
        succeed = False
        ng = 0

    if succeed:
        # read land-cover class
        land_cover_class = []
        if filename_landcover:
            temp = read_UNF_file(filename_landcover)
            if temp and len(temp) == ng: land_cover_class = temp
        if not land_cover_class: land_cover_class = [0] * ng

        # read elevation dataset
        elevation = []
        if filename_elevation:
            temp = read_UNF_file(filename_elevation, ncol=101)
            if temp and len(temp) == ng:
                for item in temp: elevation.append(item[0])
        if not elevation: elevation = [0] * ng

        # read Total Available Water Capacity
        tawc = []
        if filename_TAWC:
            temp  = read_UNF_file(filename_TAWC)
            if temp and len(temp) == ng: tawc = temp
        if not tawc: tawc = [0] * ng

        # read lake and wetland fraction and find the total lake and wetland fraction

        glake = read_UNF_file(filename_GLakeFrc)
        gwetland = read_UNF_file(filename_GWetLandFrc)
        llake = read_UNF_file(filename_LLakeFrc)
        lwetland = read_UNF_file(filename_LWetLandFrc)

        total_LWFrc = []
        if glake and gwetland and llake and lwetland:
            glake = np.array(glake)
            gwetland = np.array(gwetland)
            llake = np.array(llake)
            lwetland = np.array(lwetland)
            total_LWFrc = list(glake + gwetland + llake + lwetland)
        if not total_LWFrc: total_LWFrc = [0] * ng

        if succeed and output_filename:
            try:
                world_shape = shp.Writer(shp.POLYGON)
                world_shape.field('CID', 'N', 8)
                world_shape.field('LONG', 'N', 8, 2)
                world_shape.field('LAT', 'N', 8, 2)
                world_shape.field('LCC', 'N', 8)
                world_shape.field('TAWC', 'N', 15, 7)
                world_shape.field('ELEV', 'N', 8)

                world_shape.field('TLW', 'N', 15, 7)


                points = grid.cell_vertices(wghm_centroids, degree_resolution=0.5)
                print(succeed)
                for i in range(len(points)):
                    world_shape.autoBalance = 1 # ensures gemoetry and attributes match
                    world_shape.poly(parts=[points[i]], shapeType=shp.POLYGON)
                    world_shape.record(i + 1, wghm_centroids[i][1], wghm_centroids[i][0], land_cover_class[i], tawc[i],
                                       elevation[i], round(total_LWFrc[i],7))
                print(succeed)
                world_shape.save(output_filename)
                print(succeed)
            except: succeed = False

            if succeed:
                try:
                    ndx = output_filename.lower().find('.shp')
                    if ndx >= 0: output_filename = output_filename[:ndx]
                    output_filename += '.prj'
                    f = open(output_filename, 'w')
                    prj_string ='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                    f.write(prj_string)
                    f.close()
                except: pass
    print(succeed)

if __name__ == '__main__':
    main()