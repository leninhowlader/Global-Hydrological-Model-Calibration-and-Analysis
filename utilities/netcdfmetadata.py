import sys, os
from netCDF4 import Dataset

class NetCdfMetadata:
    @staticmethod
    def explore_metadata(netcdf_filename, output_filename:str=''):
        '''
        The method explores metadata of a given netCDF data

        :param netcdf_filename: (string) filename of target netCDF datafile
        :param output_filename: (string, optional, default = '') name of the output file. if provided, all metadate will
                                be written on the file
        :return: (boolean) True on success, False otherwise
        '''
        succeed = True
        if not os.path.exists(netcdf_filename):
            print('File not found!!')
            succeed = False

        if succeed:
            try:
                fid = Dataset(netcdf_filename, 'r')
                if output_filename: sys.stdout = open(output_filename, "w")

                temp = NetCdfMetadata.ncdump(fid)

                if output_filename: sys.stdout.close()
            except: succeed = False
            finally: sys.stdout = sys.__stdout__

        return succeed

    @staticmethod
    def ncdump(nc_fid, verb=True):
        '''
        [Credit: this function is copied from 'http://schubert.atmos.colostate.edu/~cslocum/code/netcdf_example.py']

        ncdump outputs dimensions, variables and their attribute information.
        The information is similar to that of NCAR's ncdump utility.
        ncdump requires a valid instance of Dataset.

        Parameters
        ----------
        nc_fid : netCDF4.Dataset
            A netCDF4 dateset object
        verb : Boolean
            whether or not nc_attrs, nc_dims, and nc_vars are printed

        Returns
        -------
        nc_attrs : list
            A Python list of the NetCDF file global attributes
        nc_dims : list
            A Python list of the NetCDF file dimensions
        nc_vars : list
            A Python list of the NetCDF file variables
        '''

        def print_ncattr(key):
            """
            Prints the NetCDF file attributes for a given key

            Parameters
            ----------
            key : unicode
                a valid netCDF4.Dataset.variables key
            """
            try:
                print ("\t\ttype:", repr(nc_fid.variables[key].dtype))
                for ncattr in nc_fid.variables[key].ncattrs():
                    print ('\t\t%s:' % ncattr, repr(nc_fid.variables[key].getncattr(ncattr)))
            except KeyError:
                print ("\t\tWARNING: %s does not contain variable attributes" % key)


        # NetCDF global attributes
        nc_attrs = nc_fid.ncattrs()
        if verb:
            print("NetCDF Global Attributes:")
            for nc_attr in nc_attrs:
                print('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
        nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
        # Dimension shape information.
        if verb:
            print("NetCDF dimension information:")
            for dim in nc_dims:
                print("\tName:", dim)
                print("\t\tsize:", len(nc_fid.dimensions[dim]))
                print_ncattr(dim)
        # Variable information.
        nc_vars = [var for var in nc_fid.variables]  # list of nc variables
        if verb:
            print("NetCDF variable information:")
            for var in nc_vars:
                if var not in nc_dims:
                    print('\tName:', var)
                    print("\t\tdimensions:", nc_fid.variables[var].dimensions)
                    print("\t\tsize:", nc_fid.variables[var].size)
                    print_ncattr(var)
        return nc_attrs, nc_dims, nc_vars
# ... end [of class NetCdfMetadata]
