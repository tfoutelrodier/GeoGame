# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:44:18 2024

@author: theof
"""
# load shp files
import geopandas as gpd
import pandas as pd
import re
import matplotlib.pyplot as plt
from pyproj import CRS, Transformer

"""
NUTS description:
    LVL 0 --> pays
    LVL 1 --> lander allemand, regions autonome/fédérales, regroupement de regions françaises
    LVL 2 --> anciennes régions française
    LVL 3 --> dppartements français metropolitains (les outremers sont regroupe en seulement 2-3 NUTS)
"""

'''
CONFIG parameters
'''
input_file = "data/geo_data/NUTS_RG_20M_2021_4326.shp/NUTS_RG_20M_2021_4326.shp"

# filtering france dataset
outre_mer_nuts_id = ['FRY','FRY1','FRY10','FRY3','FRY30','FRY2','FRY20','FRY5','FRY50','FRY4', 'FRY40']
outemer_pattern = r'^FRY'
levels_to_select = [1,2,3]
pattern_to_select = r'^FR'

# European neighbour countries to add
neighbours_code_lst = ['DE', 'ES', 'LU', 'BE', 'IT', 'UK', 'NL']

# Plot parameters
output_file = 'data/geo_data/france_map.png'
output_format = 'png'
nb_dpi = 300

plot_size = (10,10)
map_color = 'forestgreen'
map_facecolor = 'none'
map_edge_color = 'black'
border_limit_linewidth = 1.5
pad = 15000  # extend the map slightly around france, empirical, pad is in 3857 coord


'''
CODE
'''

# Load data for european NUTS 
gdf = gpd.read_file(input_file)

# select French nuts
subset_gdf = gdf.loc[gdf['LEVL_CODE'].isin(levels_to_select) &
                     gdf['NUTS_ID'].str.contains(pattern_to_select)]
# remove outremer
subset_gdf = subset_gdf.loc[~subset_gdf['NUTS_ID'].str.contains(outemer_pattern)]

# Get france boundaries for map display (converted in 3857 coord)
france_boundaries_proj = subset_gdf.to_crs(epsg=3857)['geometry'].total_bounds

# Add neighbouring countries (still missing andorre, switzerland)
neighbouring_countries_gdf = gdf.loc[gdf['NUTS_ID'].isin(neighbours_code_lst)]
gdf_wneighbors = pd.concat([subset_gdf, neighbouring_countries_gdf])

# convert to proj coord
gdf_wneighbors = gdf_wneighbors.to_crs(epsg=3857)  

# Plot the map (all lines until saving mmust be executed as a single block)
# Plot in proj coord
fig, ax = plt.subplots(figsize = plot_size)
gdf_wneighbors.plot(ax=ax,
                    color=map_color,
                    facecolor=map_facecolor,
                    edgecolor=map_edge_color,
                    linewidth=border_limit_linewidth)

# remove axis and legend
ax.set_axis_off()

# extend boundaries slightly
xmin, ymin, xmax, ymax = france_boundaries_proj
# add a padding around the geometry (empirical value), pad is in 3857 coord value
ax.set_xlim(xmin-pad, xmax+pad)
ax.set_ylim(ymin-pad, ymax+pad)

# Save fig
plt.savefig(output_file, dpi=nb_dpi, format=output_format,
        pad_inches=0, bbox_inches='tight')

# Convert new map boundaries back to gps values and store for game
proj_map = CRS('epsg:3857')
proj_gps = CRS("WGS84")        
to_gps = Transformer.from_crs(proj_map, proj_gps, always_xy=True)  
to_map = Transformer.from_crs(proj_gps, proj_map, always_xy=True)

xmin_gps, ymin_gps = to_gps.transform(xmin - pad, ymin - pad)
xmax_gps, ymax_gps = to_gps.transform(xmax + pad, ymax + pad)

print('xlim: ', xmin_gps, xmax_gps)
print('ylim: ', ymin_gps, ymax_gps)

'''
limit coordinates:
    xmin = -4.88788,
    xmax = 9.678657,
    ymin = 41.296552,
    ymax = 51.173938
'''



