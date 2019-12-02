# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 16:52:46 2019

@author: mhasan
"""

import sys

sys.path.append('..')
from analyses.storagecontribution import StorageContribution as scon

data_directory = 'F:/mhasan/private/temp/contribution_map_test'
filename_prefix = 'mississippi_contribution'
start_year, end_year = 2003, 2012
nyear = end_year - start_year + 1

succeed = scon.stddev_of_contribution_unf(data_directory, filename_prefix, nyear, classify=False)

