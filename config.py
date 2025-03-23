# -*- coding: utf-8 -*-
"""
List of constants that should only be replaced if major changes are made
They are held in a dict
"""

config_dict = {
    'WINDOW_WIDTH' : 800,
    'WINDOW_HEIGHT' : 840,
    
    # Set up Pygame window for map
    'MAP_WIDTH' : 800,
    'MAP_HEIGHT' : 800,
    
    # min and max lon and lat values for the map
    # min and max value correspond to 0 and max pixel value for the axis respectively
    # --> so lon_max is actualy the bottom of the map
    'COORD_LIMITS_DICT' : {
        'lon_min' : -4.88788,
        'lon_max' : 9.678657,
        'lat_max' : 41.296552,
        'lat_min' : 51.173938},
    
    # map location
    'map_file' : 'data/geo_data/france_map.png',
    
    'max_score' : 1000,
    'max_fps': 60,
    
    'target_marker_file' : 'data/assets/target_marker_v2.png',
    'player_marker_file' : 'data/assets/player_marker_v2.png',   
    'marker_map_ratio' : 0.03,  # Determine the relative size of the markers on the map
    
    'max_game_number' : 10
    }

# Dict with preset colors
color_dict = {
    'black' : (0,0,0),
    'white' : (255,255,255),
    'grey' : (169,169,169),
    'red': (255,0,0),
    'blue': (0,255,0),
    'green': (0,0,255)}


print_color_dict = {
    'black': '\033[30m',
    'red':'\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[39m'}
