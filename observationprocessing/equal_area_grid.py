import sys, shapefile as shp
sys.path.append('..')
from utilities.fileio import read_flat_file

grid_data_filename = '/media/sf_mhasan/private/temp/equal_area_grid/cell_lat_lon_width'
grid_data = None
output_grid_shapefile = '/media/sf_mhasan/private/temp/equal_area_grid/ea_grid.shp'

def read_grid_info(filename=''):
    global grid_data_filename, grid_data
    succeed = True

    if not filename:
        filename = grid_data_filename

    if filename:
        headers, data = read_flat_file(filename, separator=' ')
        if data:
            grid_data = data
        else: succeed = False
    else: succeed = False

    return succeed

def find_cell_vertices(lat_centroid, lon_centroid, cell_width):
    half_width = cell_width/2
    half_length = 0.25/2

    x1, x2 = lon_centroid-half_width, lon_centroid+half_width
    y1, y2 = lat_centroid-half_length, lat_centroid+half_length

    points = []
    if x1 < -180:
        points.append([(-180, y1), (-180, y2), (x2, y2), (x2, y1), (-180, y1)])
        x1 += 360
        points.append([(x1, y1), (x1, y2), (180, y2), (180, y1), (x1, y1)])
    elif x2 > 180:
        points.append([(x1, y1), (x1, y2), (180, y2), (180, y1), (x1, y1)])
        x2 -= 360
        points.append([(-180, y1), (-180, y2), (x2, y2), (x2, y1), (-180, y1)])
    else: points.append([(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)])

    return points

def create_shape(list_of_vertices, attrib_names, attrib_values, filename, flag_projection_file=True):
    succeed = True

    if list_of_vertices and filename:
        grid_shape = shp.Writer(shp.POLYGON)

        attrib = False
        if attrib_names and attrib_values and len(attrib_names) == len(attrib_values[0]):
            attrib = True
            for i in range(len(attrib_names)): grid_shape.field(attrib_names[i], 'N', '8')

        for i in range(len(list_of_vertices)):
            vertices = list_of_vertices[i]
            #grid_shape.autoBalance = 1  # ensures gemoetry and attributes match
            grid_shape.poly(parts=vertices, shapeType=shp.POLYGON)

            if attrib: grid_shape.record(*attrib_values[i])

        grid_shape.save(filename)

        if succeed and flag_projection_file:
            try:
                ndx = filename.lower().find('.shp')
                if ndx >= 0: filename = filename[:ndx]
                filename += '.prj'
                f = open(filename, 'w')
                prj_string = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
                f.write(prj_string)
                f.close()
            except:
                succeed = False
    else: succeed = False

    return succeed

def main():
    global grid_data_filename, output_grid_shapefile, grid_data

    succeed = True

    print('reading grid cell info ... ', end='', flush=True)
    succeed = read_grid_info(filename=grid_data_filename)
    if succeed: print('[done]')
    else: print('[failed]')

    print('calculating cell vertices ... ', end='', flush=True)
    cell_vertices = []
    if succeed:
        for d in grid_data: cell_vertices.append(find_cell_vertices(d[1], d[2], d[3]))
        if not cell_vertices: succeed = False
    if succeed: print('[done]')
    else: print('[failed]')

    #succeed = False
    print('creating shape file ... ', end='', flush=True)
    if succeed:
        attrib_names = ['CID']
        attrib_values = []
        for d in grid_data: attrib_values.append([d[0]])

        succeed = create_shape(cell_vertices, attrib_names, attrib_values, output_grid_shapefile, flag_projection_file=True)
    if succeed: print('[done]')
    else: print('[failed]')

    if succeed: exit(0)
    else: exit(-1)


if __name__ == '__main__': main()

