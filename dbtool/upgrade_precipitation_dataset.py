'''
Author: H.M. Mehedi Hasan
Date: 25-Feb-2016

This script downloads global precipitation data from GPCP server and
inserts data into Global Flood Archive Database at GFZ.
'''

import sys, os, struct, gzip
from datetime import datetime
from urllib import request
import psycopg2


server = '139.17.99.27'
database = 'cedim_rfra'
usr = 'mhasan'
pwd = 'password'
gpgc_url = ''

base_date = datetime(year=2015, month=9, day=1)

def find_latest_date():
    dt = None

    global server, database, usr, pwd

    con = None
    try: con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
    except: return False

    try:
        cur = con.cursor()
        sql_str = 'select max(date) from tmp.mh_gpcp_lib where cell = 1;' #where clause ensures index-only-scan
        cur.execute(sql_str)
        dt = cur.fetchone()[0]
    except: return None
    finally:
        try: con.close()
        except: pass

    return dt

def update_precipitation_records(year, month, records):
    global server, database, usr, pwd

    con = None
    try: con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
    except: return False

    try:
        cur = con.cursor()

        for i in range(len(records)):
            day = i + 1
            args_str = ','.join(["(%d,'%d-%d-%d',%f)" %(j+1, year, month, day, records[i][j]) for j in range(360*180)])
            cur.execute("INSERT INTO tmp.mh_gpcp_lib VALUES " + args_str + ";")
            con.commit()
    except: return None
    finally:
        try: con.close()
        except: pass

    return True


def read_gpcp_unzipped_data(filename, records):
    fs = None

    try:
        fs = open(filename, 'rb')

        #skip headers (1440 bytes)
        chunk = fs.read(1440)

        chunk_size = 360 * 180 * 4
        chunk_format = '>' + 'f' * (360 * 180) #big-endian format
        while True:
            chunk = fs.read(chunk_size)
            if chunk:
                records.append(struct.unpack(chunk_format, chunk))
            else: break
    except: return False
    finally:
        try: fs.close()
        except: pass

    return True

def read_gpcp_zipped_data(zipfile, records):
    fs = None

    try:
        fs = gzip.open(zipfile, 'rb')

        #skip headers (1440 bytes)
        chunk = fs.read(1440)

        chunk_size = 360 * 180 * 4
        chunk_format = '>' + 'f' * (360 * 180) #big-endian format
        while True:
            chunk = fs.read(chunk_size)
            if chunk:
                records.append(struct.unpack(chunk_format, chunk))
            else: break
    except: return False
    finally:
        try: fs.close()
        except: pass

    return True

def main(argv):
    global base_date

    #find the date of latest precipitation data
    latest_update_date = find_latest_date()

    if latest_update_date:
        print('Database contains data until %s.' %latest_update_date.strftime('%Y-%m-%d'))
    else:
        if latest_update_date == False:
            print('Database connection could not be established.')
            exit(-1)
        else:
            if base_date.month == 1: latest_update_date = datetime(year=base_date.year - 1, month=12, day=base_date.day)
            else: latest_update_date = datetime(year=base_date.year, month=base_date.month-1, day=base_date.day)
            print('There is no precipitation data found in the database. An attempt will be made to retrieve data from %s.' %base_date.strftime('%Y-%m-%d'))

    #retrieving data from the next month
    update_count = 0
    year = latest_update_date.year
    month = latest_update_date.month

    while True:
        #calculate next month
        if month == 12:
            year += 1
            month = 1
        else: month += 1

        #generate url and try to download data
        filename = 'gpcp_1dd_v1.2_p1d.%d%s.gz' % (year, str(month).rjust(2,'0'))
        url = 'ftp://rsd.gsfc.nasa.gov/pub/1dd-v1.2/%s' % filename
        try: request.urlretrieve(url, filename)
        except: break

        #read downloaded zip file and extract records
        records = []
        read_gpcp_zipped_data(filename, records)

        #update local precipitation database
        if records:
            if update_precipitation_records(year, month, records): update_count += 1

    if update_count == 0:
        print('No new precipitation data could be retrieved from GPCP server. Database seems to be up-do-date.')
    else:
        print('Precipitation data for %d months has been retrieved and uploaded into the database.' %update_count)
        latest_update_date = find_latest_date()
        if latest_update_date: print('Data available until %s.' %latest_update_date.strftime('%Y-%m-%d'))

    exit(os.EX_OK)

main(sys.argv)