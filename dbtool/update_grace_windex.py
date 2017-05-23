#!/usr/bin/python3

'''
Author: H.M. Mehedi Hasan
Date: 23-May-2017

'''

import sys, os, struct, gzip
from datetime import datetime
from urllib import request
import psycopg2


server = '139.17.99.27'
database = 'cedim_rfra'
usr = 'mhasan'
pwd = ''
schema = 'tmp'


datadir = '/media/sf_mhasan/private/WINDEX'
flag_create_new_column = False
data_column_name = 'windex'
temporary_db_table = 'windex_temp'
main_datatable = 'grace_anomaly'

def read_flat_file(filename, separator=',', header=False, skiplines=0):
    headers, data = [], []      #here headers is one dimensional and data is two dimensional array

    obs_file = None
    try:
        obs_file = open(filename, 'r')

        # step-01: skip lines
        if skiplines > 0:
            for i in range(skiplines): line = obs_file.readline()

        # step-02: read header names
        if header:
            line = obs_file.readline().strip()
            if line:
                temp = line.strip().split(separator)
                for i in range(len(temp)):
                    temp[i] = temp[i].strip().strip('"').strip('\'')
                    if temp[i]: headers.append(temp[i])

        # step-03: read data
        for line in obs_file.readlines():
            line = line.strip()
            if line:
                if separator:  temp = line.split(separator)
                else: temp = line.split()

                if temp:
                    for i in reversed(range(len(temp))):
                        temp[i] = temp[i].strip()
                        if temp[i]:
                            try: temp[i] = int(temp[i])
                            except:
                                try: temp[i] = float(temp[i])
                                except:
                                    try: temp[i] = datetime.strptime(temp[i], '%Y-%m-%d')
                                    except: pass
                        else: temp.pop(i)
                if temp: data.append(temp)
    except: return None, None
    finally:
        try: obs_file.close()
        except: pass

    return headers, data

def create_new_column():
    global schema, main_datatable, data_column_name

    sql_str = 'ALTER TABLE %s.%s ADD COLUMN %s NUMERIC;' % (schema, main_datatable, data_column_name)
    try:
        con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
        cur = con.cursor()
        cur.execute(sql_str)
        con.commit()
    except: return False

    return True

def create_temporary_db_table():
    global schema, temporary_db_table, data_column_name

    if not (temporary_db_table and schema): return False
    else:
        try: con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
        except: return False

        try:
            sql_str = """
                      CREATE TABLE %s.%s (
                      cid NUMERIC(10,0) NOT NULL,
                      date DATE NOT NULL,
                      %s NUMERIC);""" % (schema, temporary_db_table, data_column_name)
            cur = con.cursor()
            cur.execute(sql_str)
            con.commit()
        except: return False
        finally:
            try: con.close()
            except: pass

    return True

def clear_temporary_db_table():
    global schema, temporary_db_table

    if not (schema and temporary_db_table):
        return False
    else:
        con = None
        try:
            con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
            sql_str = 'DELETE FROM %s.%s;' % (schema, temporary_db_table)
            cur = con.cursor()
            cur.execute(sql_str)
            con.commit()
        except: return False
        finally:
            try: con.close()
            except: pass
    return True

def drop_temporary_db_table():
    global schema, temporary_db_table

    if not (schema and temporary_db_table): return False
    else:
        try: con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
        except: return False

        try:
            sql_str = 'DROP TABLE %s.%s;' % (schema, temporary_db_table)
            cur = con.cursor()
            cur.execute(sql_str)
            con.commit()
        except: return False
        finally:
            try: con.close()
            except: pass
    return True

def update_main_dbtable():
    global schema, temporary_db_table, main_datatable, data_column_name

    sql_str = """
              UPDATE %s.%s as a
                    SET %s = b.%s
              FROM %s.%s as b
              WHERE a.cid = b.cid and a.date = b.date;
              """ % (schema, main_datatable, data_column_name, data_column_name, schema, temporary_db_table)
    con = None
    try:
        con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
        cur = con.cursor()
        cur.execute(sql_str)
        con.commit()
    except: return False

    return True

def insert_into_temporary_dbtable():
    global datadir, schema, temporary_db_table, data_column_name
    succeed = True

    rcount = 0
    flist = [f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir, f))]
    for f in flist:
        print('\treading file %s' %f)
        filename = os.path.join(datadir, f)
        headers, d = read_flat_file(filename, separator=',', header=False)

        if d and len(d) == 180:
            for r in d:
                if len(r) != 360:
                    succeed = False
                    break
        if succeed:
            con = None
            try:
                con = psycopg2.connect(host=server, database=database, user=usr, password=pwd)
                cur = con.cursor()

                yr, mon, day = int(f[-12:][:4]), int(f[-8:][:2]), int(f[-6:][:2])
                sql_str = 'INSERT INTO %s.%s (cid, date, %s) VALUES ' % (schema, temporary_db_table, data_column_name)
                sql_str += ','.join(["(%d,'%d-%d-%d',%f)" % (i*360+j, yr, mon, day, d[i][j]) for i in range(180) for j in range(360) if d[i][j]==d[i][j]]) + ';'

                cur.execute(sql_str)
                rcount += cur.rowcount
                con.commit()
                try: con.close()
                except: pass
            except: pass

    return rcount

def main():
    global flag_create_new_column

    if flag_create_new_column:
        print('inserting new column into the main data table ...', end='', flush=True)
        succeed = create_new_column()
        if succeed: print('[done]')
        else: print('[failed]')

    print('creating temporary table in database ...', end='', flush=True)
    succeed = create_temporary_db_table()
    if succeed: print('[done]')
    else: print('[failed]')

    print('inserting new data into the temporary data table ...')
    rowcount = insert_into_temporary_dbtable()
    if rowcount > 0: print('[done]')
    else: print('[failed]')

    print('updating the main data table...', end='', flush=True)
    if rowcount > 0:
        succeed = update_main_dbtable()
        if succeed: print('[done]')
        else: print('[failed]')

    print('droping the temporary data table ...', end='', flush=True)
    succeed = drop_temporary_db_table()
    if succeed: print('[done]')
    else: print('[failed]')

    print(succeed)

def test():
    print('this must work ...', end='', flush=False)
    print('[okay]')

    print('finished')

if __name__ == '__main__': test()