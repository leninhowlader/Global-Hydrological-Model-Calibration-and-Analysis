import sys, os
sys.path.append('..')
from utilities.fileio import read_flat_file, write_flat_file
from utilities.grid import grid
from datetime import datetime



directory  = '/media/sf_mhasan/private/GRACE_DAILY/'
output_filename = 'grace_daily'

def generate_cell_id(longitude, latitude):
    row, col = grid.find_row_column(latitude, longitude, degree_resolution=1.0)
    return row*360+col

def main():
    global directory, output_filename

    dlist = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

    dlist.sort()
    for i in reversed(range(len(dlist))):
        if dlist[i].find('_2002') < 0: dlist.pop(i)
    for sd in dlist:
        sd = os.path.join(directory,sd)
        print('reading data from directory ' + sd + '...')
        flist = [f for f in os.listdir(sd) if os.path.isfile(os.path.join(sd, f))]
        flist.sort()
        for f in flist:
            print('\tfile: ' + f + '...', end='', flush=True)

            succeed = False
            f = os.path.join(sd, str(f))
            date = datetime.strptime(f[-14:-4], '%Y-%m-%d').date()
            headers, data = read_flat_file(f, separator=' ', header=False, skiplines=10)
            for d in data: d.append(date)
            if data: succeed = True

            filename = os.path.join(directory, output_filename + '_' + str(date.year) + '.csv')
            succeed = write_flat_file(filename, data, separator=',', append=True)
            if succeed: print('[done]')
            else: print('[failed]')
    print(dlist)

if __name__ == '__main__':
    main()