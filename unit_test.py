# -*- coding: utf-8 -*-
"""
For individual tests
"""

from gui_classes import Location, GeoMap
from config import config_dict, print_color_dict
from helper import print_color
    

def test_Location_pixel2gps_ifPixelInput() -> None:
    # create a dict with all expected corners values in gps data from the config file
    geo_map = GeoMap()
    expected_value_dict = {
        "_".join(['bottomRight', str(geo_map.topleft_x + geo_map.width), str(geo_map.topleft_y + geo_map.height)]) : 
            (config_dict['COORD_LIMITS_DICT']['lon_max'], config_dict['COORD_LIMITS_DICT']['lat_max']),
        "_".join(['bottomLeft', str(geo_map.topleft_x), str(geo_map.topleft_y + geo_map.height)]) :
            (config_dict['COORD_LIMITS_DICT']['lon_min'], config_dict['COORD_LIMITS_DICT']['lat_max']),
        "_".join(['topRight', str(geo_map.topleft_x + geo_map.width), str(geo_map.topleft_y)]) :
            (config_dict['COORD_LIMITS_DICT']['lon_max'], config_dict['COORD_LIMITS_DICT']['lat_min']),
        "_".join(['topLeft', str(geo_map.topleft_x), str(geo_map.topleft_y)]) :
            (config_dict['COORD_LIMITS_DICT']['lon_min'], config_dict['COORD_LIMITS_DICT']['lat_min']),
        }

    nb_ok = 0
    for key in expected_value_dict:
        # print(key)
        target_lon, target_lat = expected_value_dict[key]
        corner, x, y = key.split("_")
        x = int(x)
        y = int(y)
        test_loc = Location(loc=(x,y), geo_map=geo_map, coord_type='pixel')
        test_loc.pixel2gps()
        
        if round(test_loc.x, 2) == round(target_lon,2) and round(test_loc.y, 2) == round(target_lat,2):
            nb_ok += 1
        else:
            print(corner)
            print('expected x:', target_lon, "--- actual x:", test_loc.x)
            print('expected y:', target_lat, "--- actual y:",test_loc.y)
    
    if nb_ok == len(expected_value_dict):
        print_color("Location_pixel2gps_ifPixelInput: OK", color = "green")
    else:
        print_color("Location_pixel2gps_ifPixelInput: FAIL", color = "red")


def test_Location_pixel2gps_ifGPSInput() -> None:
    geo_map = GeoMap()
    test_pos = (0,0)
    test_loc = Location(loc=test_pos, geo_map=geo_map, coord_type="gps")
    test_loc.pixel2gps()
    if test_pos == (test_loc.x, test_loc.y) and test_loc.coord_type == "gps":
        print_color("Location_pixel2gps_ifGPSInput: OK", color = "green")
    else:
        print_color("Location_pixel2gps_ifGPSInput: FAIL", color = "red")


def test_Location_gps2pixel_ifGPSInput() -> None:
    geo_map = GeoMap()
    # create a dict with all expected corners values in gps data from the config file
    expected_value_dict = {
        "_".join([str(config_dict['COORD_LIMITS_DICT']['lon_max']), str(config_dict['COORD_LIMITS_DICT']['lat_max'])]) : 
            (config_dict['MAP_WIDTH'], config_dict['MAP_HEIGHT']),
        "_".join([str(config_dict['COORD_LIMITS_DICT']['lon_min']), str(config_dict['COORD_LIMITS_DICT']['lat_max'])]) :
            (0, config_dict['MAP_HEIGHT']),
        "_".join([str(config_dict['COORD_LIMITS_DICT']['lon_max']), str(config_dict['COORD_LIMITS_DICT']['lat_min'])]) :
            (config_dict['MAP_WIDTH'], 0),
        "_".join([str(config_dict['COORD_LIMITS_DICT']['lon_min']), str(config_dict['COORD_LIMITS_DICT']['lat_min'])]) :
            (0, 0),
        }

    nb_ok = 0
    for key in expected_value_dict:
        target_lon, target_lat = expected_value_dict[key]
        
        x,y = [float(elem) for elem in key.split("_")]
        test_loc = Location(loc=(x,y), coord_type='gps', geo_map=geo_map)
        test_loc.gps2pixel()
        
        if round(test_loc.x, 2) == round(target_lon,2) and round(test_loc.y, 2) == round(target_lat,2):
            nb_ok += 1
        else:
            print(key)
            print('expected x:', target_lon, "--- actual x:", test_loc.x)
            print('expected y:', target_lat, "--- actual y:",test_loc.y)
    
    if nb_ok == len(expected_value_dict):
        print_color("Location_gps2pixel_ifGPSInput: OK", color = "green")
    else:
        print_color("Location_gps2pixel_ifGPSInput: FAIL", color = "red")


def test_Location_gps2pixel_ifPixelInput() -> None:
    geo_map = GeoMap()
    test_pos = (0,0)
    test_loc = Location(loc=test_pos, geo_map=geo_map, coord_type="pixel")
    test_loc.gps2pixel()
    if test_pos == (test_loc.x_pixel, test_loc.y_pixel) and test_loc.coord_type == "pixel":
        print_color("Location_gps2pixel_ifPixelInput: OK", color = "green")
    else:
        print_color("Location_gps2pixel_ifPixelInput: FAIL", color = "red")


def run_tests() -> None:
    '''
    run all tests
    '''
    test_Location_pixel2gps_ifPixelInput()
    test_Location_pixel2gps_ifGPSInput()
    test_Location_gps2pixel_ifGPSInput()
    test_Location_gps2pixel_ifPixelInput()


if __name__ == '__main__':
    run_tests()
