# -*- coding: utf-8 -*-
"""
Created on Wed May 22 14:45:42 2019

@author: mhasan

important links:
(i) tutorial: mapping geographic data in python
    https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
"""

import os, sys, numpy as np

sys.path.append('..')
from analyses.storagecontribution import StorageContribution as scon


data_directory = 'F:/mhasan/private/temp/contribution_map_test'


def contribution_map_mississippi():
    global data_directory
    
    # 1. long-term mean contribution
    
    filename_coord_x = os.path.join(data_directory, 'mississippi_contribution_coordinate_X.5.unf0')
    filename_coord_y = os.path.join(data_directory, 'mississippi_contribution_coordinate_Y.5.unf0')
    
    lons, lats = scon.get_cell_edge_coordinates_from_unf(filename_coord_x, filename_coord_y)
    
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    title = 'Long-term (2003-2012) mean contribution of storage components to mean seasonal amplitude\nin Mississippi Basin'
    visible_coord_grid_resolution = (5, 5)
    coordsys_text = 'Coordinate System: GCS WGS 1984\nDatum: WGS 1984\nUnits: Degree'
    author_text = 'Author: H.M. Mehedi Hasan (2019)'
    acknowledge_text = '[Created using Python Matplotlib 2.2.3]'
    
    north_arrow_properties = {}
    x, y, w, h = (-114.3, 35, 0.6, 0.6)
    north_arrow_properties['pos_x'] = x
    north_arrow_properties['pos_y'] = y
    north_arrow_properties['width'] = w
    north_arrow_properties['height'] = h
    north_arrow_properties['line_width'] = 0.05
    north_arrow_properties['head_width'] = 0.25
    
    filename_data = os.path.join(data_directory, 'mississippi_contribution_long_term.11.unf0')
    r = scon.read_unf(filename_data)
    
    nrow, ncol = r.shape
    # 1-A: generate map with contributions of major storages 
    d =  np.concatenate((r[:, 1:5], r[:, 5:].sum(axis=1).reshape(nrow, 1)), axis=1)
    
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title)
    
    
    filename = 'F:/mhasan/data/GlobalCDA/mississippi_shapes/dissolved_all.shp'
    scon.add_shapefile(ax, filename, colors=['red'], text_record_index=-1, linewidth=2)
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/mississippi_long_term.png'
    fig.savefig(output_filename, dpi=600)
    
    # 1-B: generate map with contributions of surface water storage components
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    d = np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(nrow, 1)), axis=1)
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title)
    
    
    filename = 'F:/mhasan/data/GlobalCDA/mississippi_shapes/dissolved_all.shp'
    scon.add_shapefile(ax, filename, colors=['red'], text_record_index=-1, linewidth=2)
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/mississippi_long_term_sws.png'
    fig.savefig(output_filename, dpi=600)
    
    # 2. yearly contributions - animations
    
    start_year, end_year = 2003, 2012
    filenames, titles = [], []
    for year in range(start_year, end_year + 1):
        titles.append('Contribution of storage components to seasonal amplitude (%d) \nin Mississippi Basin'%year)
        filenames.append(os.path.join(data_directory, 'mississippi_contribution_%d.11.unf0'%year))
    
    # 2-A: contributions of major storages
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/mississippi_years.gif'
    shape_filename = 'F:/mhasan/data/GlobalCDA/mississippi_shapes/dissolved_all.shp'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, add_shapefile=shape_filename)
    
    # 2-B: contributions of sws storage components
    def data_manip_fun(r:np.ndarray): return np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(r.shape[0], 1)), axis=1)
    
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/mississippi_years_sws.gif'
    shape_filename = 'F:/mhasan/data/GlobalCDA/mississippi_shapes/dissolved_all.shp'
    output_filename = ''
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, add_shapefile=shape_filename,
                                    fun_dmanip=data_manip_fun)
    
def contribution_map_hermann():
    global data_directory
    
    # 1. long-term mean contribution
    
    filename_coord_x = os.path.join(data_directory, 'hermann_contribution_coordinate_X.5.unf0')
    filename_coord_y = os.path.join(data_directory, 'hermann_contribution_coordinate_Y.5.unf0')
    
    lons, lats = scon.get_cell_edge_coordinates_from_unf(filename_coord_x, filename_coord_y)
    
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    title = 'Long-term (2003-2012) mean contribution of storage components to mean seasonal amplitude\nin Hermann Upstream Basin'
    visible_coord_grid_resolution = (5, 5)
    coordsys_text = 'Coordinate System: GCS WGS 1984\nDatum: WGS 1984\nUnits: Degree'
    author_text = 'Author: H.M. Mehedi Hasan (2019)'
    acknowledge_text = '[Created using Python Matplotlib 2.2.3]'
    
    north_arrow_properties = {}
    x, y, w, h = (-114.3, 39, 0.6, 0.6)
    north_arrow_properties['pos_x'] = x
    north_arrow_properties['pos_y'] = y
    north_arrow_properties['width'] = w
    north_arrow_properties['height'] = h
    north_arrow_properties['line_width'] = 0.05
    north_arrow_properties['head_width'] = 0.25
    
    filename_data = os.path.join(data_directory, 'hermann_contribution_long_term.11.unf0')
    r = scon.read_unf(filename_data)
    
    nrow, ncol = r.shape
    # 1-A: generate map with contributions of major storages 
    d =  np.concatenate((r[:, 1:5], r[:, 5:].sum(axis=1).reshape(nrow, 1)), axis=1)
    
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/hermann_long_term.png'
    fig.savefig(output_filename, dpi=600)
    
    # 1-B: generate map with contributions of surface water storage components
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    d = np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(nrow, 1)), axis=1)
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/hermann_long_term_sws.png'
    fig.savefig(output_filename, dpi=600)
    
    # 2. yearly contributions - animations
    
    start_year, end_year = 2003, 2012
    filenames, titles = [], []
    for year in range(start_year, end_year + 1):
        titles.append('Contribution of storage components to seasonal amplitude (%d) \nin Hermann Upstream Basin'%year)
        filenames.append(os.path.join(data_directory, 'hermann_contribution_%d.11.unf0'%year))
    
    # 2-A: contributions of major storages
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/hermann_years.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600)
    
    # 2-B: contributions of sws storage components
    def data_manip_fun(r:np.ndarray): return np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(r.shape[0], 1)), axis=1)
    
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/hermann_years_sws.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, fun_dmanip=data_manip_fun)

def contribution_map_alton():
    global data_directory
    
    # 1. long-term mean contribution
    
    filename_coord_x = os.path.join(data_directory, 'alton_contribution_coordinate_X.5.unf0')
    filename_coord_y = os.path.join(data_directory, 'alton_contribution_coordinate_Y.5.unf0')
    
    lons, lats = scon.get_cell_edge_coordinates_from_unf(filename_coord_x, filename_coord_y)
    
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    title = 'Long-term (2003-2012) mean contribution of storage components to mean seasonal amplitude\nin Alton Upstream Basin'
    visible_coord_grid_resolution = (5, 5)
    coordsys_text = 'Coordinate System: GCS WGS 1984\nDatum: WGS 1984\nUnits: Degree'
    author_text = 'Author: H.M. Mehedi Hasan (2019)'
    acknowledge_text = '[Created using Python Matplotlib 2.2.3]'
    
    north_arrow_properties = {}
    x, y, w, h = (-97.3, 40.3, 0.55, 0.55)
    north_arrow_properties['pos_x'] = x
    north_arrow_properties['pos_y'] = y
    north_arrow_properties['width'] = w
    north_arrow_properties['height'] = h
    north_arrow_properties['line_width'] = 0.05
    north_arrow_properties['head_width'] = 0.20
    
    filename_data = os.path.join(data_directory, 'alton_contribution_long_term.11.unf0')
    r = scon.read_unf(filename_data)
    
    nrow, ncol = r.shape
    # 1-A: generate map with contributions of major storages 
    d =  np.concatenate((r[:, 1:5], r[:, 5:].sum(axis=1).reshape(nrow, 1)), axis=1)
    
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/alton_long_term.png'
    fig.savefig(output_filename, dpi=600)
    
    # 1-B: generate map with contributions of surface water storage components
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    d = np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(nrow, 1)), axis=1)
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/alton_long_term_sws.png'
    fig.savefig(output_filename, dpi=600)
    
    # 2. yearly contributions - animations
    
    start_year, end_year = 2003, 2012
    filenames, titles = [], []
    for year in range(start_year, end_year + 1):
        titles.append('Contribution of storage components to seasonal amplitude (%d) \nin Alton Upstream Basin'%year)
        filenames.append(os.path.join(data_directory, 'alton_contribution_%d.11.unf0'%year))
    
    # 2-A: contributions of major storages
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/alton_years.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600)
    
    # 2-B: contributions of sws storage components
    def data_manip_fun(r:np.ndarray): return np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(r.shape[0], 1)), axis=1)
    
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/alton_years_sws.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, fun_dmanip=data_manip_fun)
    
def contribution_map_metropolis():
    global data_directory
    
    # 1. long-term mean contribution
    
    filename_coord_x = os.path.join(data_directory, 'metropolis_contribution_coordinate_X.5.unf0')
    filename_coord_y = os.path.join(data_directory, 'metropolis_contribution_coordinate_Y.5.unf0')
    
    lons, lats = scon.get_cell_edge_coordinates_from_unf(filename_coord_x, filename_coord_y)
    
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    title = 'Long-term (2003-2012) mean contribution of storage components to mean seasonal amplitude\nin Metropolis Upstream Basin'
    visible_coord_grid_resolution = (5, 5)
    coordsys_text = 'Coordinate System: GCS WGS 1984\nDatum: WGS 1984\nUnits: Degree'
    author_text = 'Author: H.M. Mehedi Hasan (2019)'
    acknowledge_text = '[Created using Python Matplotlib 2.2.3]'
    
    north_arrow_properties = {}
    x, y, w, h = (-80.6, 35.1, 0.5, 0.5)
    north_arrow_properties['pos_x'] = x
    north_arrow_properties['pos_y'] = y
    north_arrow_properties['width'] = w
    north_arrow_properties['height'] = h
    north_arrow_properties['line_width'] = 0.05
    north_arrow_properties['head_width'] = 0.20
    
    filename_data = os.path.join(data_directory, 'metropolis_contribution_long_term.11.unf0')
    r = scon.read_unf(filename_data)
    
    nrow, ncol = r.shape
    # 1-A: generate map with contributions of major storages 
    d =  np.concatenate((r[:, 1:5], r[:, 5:].sum(axis=1).reshape(nrow, 1)), axis=1)
    
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title, additional_text_loc=4)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/metropolis_long_term.png'
    fig.savefig(output_filename, dpi=600)
    
    # 1-B: generate map with contributions of surface water storage components
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    d = np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(nrow, 1)), axis=1)
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title, additional_text_loc=4)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/metropolis_long_term_sws.png'
    fig.savefig(output_filename, dpi=600)
    
    # 2. yearly contributions - animations
    
    start_year, end_year = 2003, 2012
    filenames, titles = [], []
    for year in range(start_year, end_year + 1):
        titles.append('Contribution of storage components to seasonal amplitude (%d) \nin Metropolis Upstream Basin'%year)
        filenames.append(os.path.join(data_directory, 'metropolis_contribution_%d.11.unf0'%year))
    
    # 2-A: contributions of major storages
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/metropolis_years.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, additional_text_loc=4)
    
    # 2-B: contributions of sws storage components
    def data_manip_fun(r:np.ndarray): return np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(r.shape[0], 1)), axis=1)
    
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/metropolis_years_sws.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, fun_dmanip=data_manip_fun, additional_text_loc=4)

def contribution_map_little_rock():
    global data_directory
    
    # 1. long-term mean contribution
    
    filename_coord_x = os.path.join(data_directory, 'little_rock_contribution_coordinate_X.5.unf0')
    filename_coord_y = os.path.join(data_directory, 'little_rock_contribution_coordinate_Y.5.unf0')
    
    lons, lats = scon.get_cell_edge_coordinates_from_unf(filename_coord_x, filename_coord_y)
    
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    title = 'Long-term (2003-2012) mean contribution of storage components to mean seasonal amplitude\nin Little Rock Upstream Basin'
    visible_coord_grid_resolution = (3, 3)
    coordsys_text = 'Coordinate System: GCS WGS 1984\nDatum: WGS 1984\nUnits: Degree'
    author_text = 'Author: H.M. Mehedi Hasan (2019)'
    acknowledge_text = '[Created using Python Matplotlib 2.2.3]'
    
    north_arrow_properties = {}
    x, y, w, h = (-106.9, 35.5, 0.5, 0.5)
    north_arrow_properties['pos_x'] = x
    north_arrow_properties['pos_y'] = y
    north_arrow_properties['width'] = w
    north_arrow_properties['height'] = h
    north_arrow_properties['line_width'] = 0.05
    north_arrow_properties['head_width'] = 0.20
    
    filename_data = os.path.join(data_directory, 'little_rock_contribution_long_term.11.unf0')
    r = scon.read_unf(filename_data)
    
    nrow, ncol = r.shape
    # 1-A: generate map with contributions of major storages 
    d =  np.concatenate((r[:, 1:5], r[:, 5:].sum(axis=1).reshape(nrow, 1)), axis=1)
    
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title, additional_text_loc=3)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/little_rock_long_term.png'
    fig.savefig(output_filename, dpi=600)
    
    # 1-B: generate map with contributions of surface water storage components
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    d = np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(nrow, 1)), axis=1)
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title, additional_text_loc=3)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/little_rock_long_term_sws.png'
    fig.savefig(output_filename, dpi=600)
    
    # 2. yearly contributions - animations
    
    start_year, end_year = 2003, 2012
    filenames, titles = [], []
    for year in range(start_year, end_year + 1):
        titles.append('Contribution of storage components to seasonal amplitude (%d) \nin Little Rock Upstream Basin'%year)
        filenames.append(os.path.join(data_directory, 'little_rock_contribution_%d.11.unf0'%year))
    
    # 2-A: contributions of major storages
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/little_rock_years.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, additional_text_loc=3, 
                                    visible_coord_grid_resolution=visible_coord_grid_resolution)
    
    # 2-B: contributions of sws storage components
    def data_manip_fun(r:np.ndarray): return np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(r.shape[0], 1)), axis=1)
    
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/little_rock_years_sws.png'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, fun_dmanip=data_manip_fun, additional_text_loc=3,
                                    visible_coord_grid_resolution=visible_coord_grid_resolution)
   
def contribution_map_vicksburg():
    global data_directory
    
    # 1. long-term mean contribution
    
    filename_coord_x = os.path.join(data_directory, 'vicksburg_contribution_coordinate_X.5.unf0')
    filename_coord_y = os.path.join(data_directory, 'vicksburg_contribution_coordinate_Y.5.unf0')
    
    lons, lats = scon.get_cell_edge_coordinates_from_unf(filename_coord_x, filename_coord_y)
    
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    title = 'Long-term (2003-2012) mean contribution of storage components to mean seasonal amplitude\nin Vicksburg Upstream Basin'
    visible_coord_grid_resolution = (3, 3)
    coordsys_text = 'Coordinate System: GCS WGS 1984\nDatum: WGS 1984\nUnits: Degree'
    author_text = 'Author: H.M. Mehedi Hasan (2019)'
    acknowledge_text = '[Created using Python Matplotlib 2.2.3]'
    
    north_arrow_properties = {}
    x, y, w, h = (-94.4, 33., 0.5, 0.5)
    north_arrow_properties['pos_x'] = x
    north_arrow_properties['pos_y'] = y
    north_arrow_properties['width'] = w
    north_arrow_properties['height'] = h
    north_arrow_properties['line_width'] = 0.05
    north_arrow_properties['head_width'] = 0.20
    
    filename_data = os.path.join(data_directory, 'vicksburg_contribution_long_term.11.unf0')
    r = scon.read_unf(filename_data)
    
    nrow, ncol = r.shape
    # 1-A: generate map with contributions of major storages 
    d =  np.concatenate((r[:, 1:5], r[:, 5:].sum(axis=1).reshape(nrow, 1)), axis=1)
    
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title, additional_text_loc=3)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/vicksburg_long_term.png'
    fig.savefig(output_filename, dpi=600)
    
    # 1-B: generate map with contributions of surface water storage components
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    d = np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(nrow, 1)), axis=1)
    succeed, fig, ax = scon.draw_contribution_pie(lons, lats, d, colors=colors, labels=legend_labels, visible_coord_grid_resolution=visible_coord_grid_resolution,
                               offset=1.0, north_arrow_props=north_arrow_properties, figsize=(14, 8), coordsys_text=coordsys_text,
                               author_text=author_text, acknowledge_text=acknowledge_text, title=title, additional_text_loc=3)
    
    
    output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/vicksburg_long_term_sws.png'
    fig.savefig(output_filename, dpi=600)
    
    # 2. yearly contributions - animations
    
    start_year, end_year = 2003, 2012
    filenames, titles = [], []
    for year in range(start_year, end_year + 1):
        titles.append('Contribution of storage components to seasonal amplitude (%d) \nin Vicksburg Upstream Basin'%year)
        filenames.append(os.path.join(data_directory, 'vicksburg_contribution_%d.11.unf0'%year))
    
    # 2-A: contributions of major storages
    legend_labels = ['Canopy Storage', 'Snow Storage', 'Soil Storage', 'Groundwater Storage', 'Surface Water Storage']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/vicksburg_years.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, additional_text_loc=3, 
                                    visible_coord_grid_resolution=visible_coord_grid_resolution)
    
    # 2-B: contributions of sws storage components
    def data_manip_fun(r:np.ndarray): return np.concatenate((r[:, 5:], r[:, 1:5].sum(axis=1).reshape(r.shape[0], 1)), axis=1)
    
    legend_labels = ['Local Lake', 'Global Lake', 'Local Wetland', 'Global Wetland', 'Reservoir', 'River', 'Others']
    colors = []
    for label in legend_labels: colors.append(scon.get_storage_color(label))
    
    output_filename = output_filename = 'F:/mhasan/experiments/GlobalCDA/calibration_mississippi/output/contrib_map/vicksburg_years_sws.gif'
    scon.contributoin_map_animation(filenames_data=filenames, lons=lons, lats=lats, titles=titles, colors=colors,
                                    legend_labels=legend_labels, north_arrow_properties=north_arrow_properties,
                                    coordsys_text=coordsys_text, author_text=author_text, acknowledge_text=acknowledge_text,
                                    output_filename=output_filename, dpi=600, fun_dmanip=data_manip_fun, additional_text_loc=3,
                                    visible_coord_grid_resolution=visible_coord_grid_resolution)
