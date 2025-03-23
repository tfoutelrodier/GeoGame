# -*- coding: utf-8 -*-
"""
helper functions
"""
import csv
import re
import pandas as pd
import math
from config import print_color_dict
import pygame
import numpy as np

# for font work before pygame.init()
pygame.font.init()

def csv2dict(csv_file:str, separator: str = ",", header: bool = False) -> dict[str:str]:
    '''
    csv_file : str of path
    separator : str
    header : BOOL
    
    load a 2 column csv into a dict
    return a dict with dict[col1] = col2
    '''
    data_dict = {}
    with open(csv_file, 'r') as file:
        reader = csv.reader(file, delimiter=separator,)
        if header:
            next(reader)
        for row in reader:
            key, value = row
            data_dict[key] = value
    return(data_dict)


def load_database() -> pd.DataFrame:
    '''
    return city data in a dataframe
    '''
    df = pd.read_csv('data/cities_data.csv', sep=";", header=0)
    return(df)


def haversine(lon1: int|float, lat1: int|float, lon2: int|float, lat2: int|float) -> int:
    '''
    Calculated distance in km between two points in GPS (WSG84) Coordinates
    '''
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of the Earth in kilometers
    R = 6371.0

    # Calculate the distance
    distance = R * c
    return distance


def print_color(txt: str, color:str='red') -> None:
    '''
    Display message in color
    if wrong color, print a warning
    '''
    if type(txt) is str:
        txt = str(txt)

    if color in print_color_dict:
        print(print_color_dict[color] + txt + print_color_dict['reset'])
    else:
        print("WARNING: wrong color passed to print_color")
        print(txt)


def render_text(topleft_x:int, topleft_y:int, text:int, font_name:str, font_size:int, color:str) -> tuple[pygame.Surface, pygame.Rect]:
    '''
    Display some text
    Pass argument as a dict with following keys:
        font, font_size, text, topleft_x, topleft_y, color
    '''
    # Load arg
    x = topleft_x
    y = topleft_y
    textMessage = text
    fontName = font_name
    fontSize = font_size
    colorMessage = color

    # Create text objects
    font = pygame.font.SysFont(fontName, fontSize)
    text_surface = font.render(textMessage, True, colorMessage)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    return(text_surface, text_rect)


def calculate_score(distance:int, config_dict:dict) -> int:
    '''
    Return a score based on distance in km to target
    Score is defined by a A*exp(B*x) equation
    A is max score (for perfect max)
    B is the number that gives half score for a distance of N km
        B = ln(0.5) / N
    '''
    x = distance  # distance in km to target
    N = 200  # Distance in km for half max score
    A = config_dict['max_score']  # max score
    B = math.log(0.5) / N  # Coefficient for decreasing

    score = A * math.exp(B * x)
    return(int(score))


# def place_text_along_line(target_pos, player_pos, line_rect, text, value_type='score', is_close=0, offset=10):
#     '''
#     Take two Location objects, a rect, a text to print and a qualifyier
#     value type can be either 'score' or 'distance'
#     is_close refer to closeness of the two marker using a score or km threshold
#     offset (int >=0) is the pixel number to offset the text from the lines or markers
    
#     Return a Text objects to display the text
    
#     General case: plot the text along the middle of the line
#                   angle the text along the line slope
#                   plot score on one side and distance on the other
#                   Adapt according to relative position of marker and line length
    
#     Find the slope of the line from player to target.
    
#     By default put the score on the left of a positive slope and right of a negative one
        
#              /                \               score
#       score / dist   or  dist \ score     ------------
#            /                  \               dist

    
#     '''
#     from gui_classes import Text
    
#     # Create text and rotate to match slope
#     return_text = Text(
#         text = text,
#         x=0,
#         y=0,
#         anchor='topleft',
#         fontSize=30)
    
#     if is_close:
#         '''
#         Plot horizontally, above or below the markers 
#         '''
#         from config import config_dict
#         lowest_pixel = max(target_pos.bottomleft[1], player_pos.bottomleft[1])
        
#         window_height = config_dict['WINDOW_HEIGHT']
        
#         return_text.x, return_text.y = line_rect.center
#         if lowest_pixel <= 0.9 * config_dict['WINDOW_HEIGHT']:
#             # plot above
#             highest_pixel = min(target_pos.topleft[1], player_pos.topleft[1])
#             return_text.y = highest_pixel - offset
#             return_text.anchor = 'midbottom'
#         else:
#             # plot below
#             return_text.y = lowest_pixel + offset
#             return_text.anchor = 'midtop'
        
#         return_text.update()
#         return(return_text)
    
#     # General case : plot at angle
            
#     # Slope is delta_y / delta_x
#     if target_pos.x_pixel == player_pos.x_pixel:
#         slope = 'inf'
#         angle = 90
#     else:
#         slope = (target_pos.y_pixel - player_pos.y_pixel + 1) / (target_pos.x_pixel - player_pos.x_pixel + 1)
#         angle = np.degrees(np.arctan(slope))
    
#     if slope >= 0 or slope == 'inf':
#         return_text.rotate(int(round(-angle, 0)))
#         text_x, text_y = line_rect.center
#         if value_type == 'score':
#             # Score is on left
#             text_x = text_x - 10
#             text_y = text_y - 10
#             text_anchor = 'midbottom'
#         elif value_type == 'distance':
#             # Distance is on right
#             text_x = text_x + 10
#             text_y = text_y + 10
#             text_anchor = 'topbottom'
#     else:
#         return_text.rotate(int(round(angle, 0)))
#         text_x, text_y = line_rect.center
#         if value_type == 'score':
#             # Score is on left
#             text_x = text_x - 10
#             text_y = text_y - 10
#             text_anchor = 'topbottom'
#         elif value_type == 'distance':
#             # Distance is on right
#             text_x = text_x + 10
#             text_y = text_y + 10
#             text_anchor = 'midbottom'
    
#     return_text.move(x=text_x, y=text_y, anchor=text_anchor)
#     return(return_text)


# def place_guess_score(target_pos, player_pos, line_rect, text, value_type='score', value=1000):
#     if value_type == 'score' and value >= 800:
#         is_close = 1
#     return_text = place_text_along_line(target_pos, player_pos, line_rect, text, value_type='score', value, is_close=0, offset=10)
#     return(return_text)

# def place_guess_distance(target_pos, player_pos, line_rect, text, value_type='score', value=1000):
#     return_text = place_text_along_line(target_pos, player_pos, line_rect, text, value_type='score', is_close=0, offset=10)
#     return(return_text)