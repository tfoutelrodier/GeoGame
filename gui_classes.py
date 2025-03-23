# -*- coding: utf-8 -*-
"""
clases for object to display using pygames
"""
import pygame
from helper import haversine, print_color
from pyproj import CRS, Transformer
from config import color_dict, config_dict
import math
import numpy as np

class Location():
    '''
    This class is meant to hold a location on the map
    Can change from gps to pixel coordinates
        --> 3 types of coordinates:
            - window pixel (display ready)
            - map pixel (intermediate for gps conversion, 0,0 is topleft)
            - gps coord (for calculating distances)
    If input is pixels, then they are window pixel
    Can be named and display marker and name
    '''
    def __init__(
            self,
            marker_surface:pygame.Surface=None,
            loc:tuple[int|float, int|float]=(0,0),
            coord_type:str='pixel',
            map_lim:str='auto',
            geo_map:'GeoMap'=None
                ) -> None:
        
        if geo_map is not None:
            self.map_width = geo_map.width
            self.map_height = geo_map.height
            self.map_topleft_x = geo_map.topleft_x
            self.map_topleft_y = geo_map.topleft_y
        else:
            # Should not happen in normal case
            # This is a duplicated code that works for the inital layout
            # Always pass the GeoMap object
            print("WARNING: no geomap passed, using old calculation method. It might lead to issues")
            self.map_width = config_dict['MAP_WIDTH']
            self.map_height = config_dict['MAP_HEIGHT']
            self.map_topleft_x = config_dict['WINDOW_WIDTH'] - config_dict['MAP_WIDTH']
            self.map_topleft_y = config_dict['WINDOW_HEIGHT'] - config_dict['MAP_HEIGHT']
        
        self.coord_type = coord_type
        self.marker_surface = marker_surface  # marker image to plot
        
        # Save and adjust coordinates as required
        if self.coord_type == 'pixel':
            # Keep track of plot ready pixel values
            self.x_pixel = loc[0]  
            self.y_pixel = loc[1]
            
            # Calculate relative pixel coordinates to the map
            self.x = loc[0] - self.map_topleft_x
            self.y = loc[1] - self.map_topleft_y
        elif self.coord_type == 'gps':
            self.x = loc[0]
            self.y = loc[1]
            # save inital gps coordinates
            self.x_gps = loc[0]
            self.y_gps = loc[1]
        else:
            print('WARNING: coord type is neither "gps" or "pixel"')
            self.x = loc[0]
            self.y = loc[1]


        if map_lim == 'auto':
            self.map_lim = config_dict['COORD_LIMITS_DICT']
        
        # projection to convert between projected and geographic pos data
            # initialize coord systems
        self.proj_map = CRS('epsg:3857')
        self.proj_gps = CRS("WGS84")
            # create functions to transform coord from one system to another
            # usage : self.to_gps.transform(map_coord_x, map_coord_y) = (gps_x, gps_y)
        self.to_gps = Transformer.from_crs(self.proj_map, self.proj_gps, always_xy=True)
        self.to_map = Transformer.from_crs(self.proj_gps, self.proj_map, always_xy=True)
        
        
    def pixel2gps(self) -> None:
        '''
        Convert coordinates from pixels (EPSG:3857 coordinates) to GPS (WGS84 coordinates)
        '''
        if self.coord_type == 'gps':
            print('WARNING coord are already in gsp system')
            return
        
        # convert map corner coordiantes to proj map coord
        # x axis is lon and y axis is lat
        xmin_map, ymin_map = self.to_map.transform(self.map_lim['lon_min'], self.map_lim['lat_min'])
        xmax_map, ymax_map = self.to_map.transform(self.map_lim['lon_max'], self.map_lim['lat_max'])
        
        # Find pixel coord in 3857 system
            # Get map scale in map proj unit/px
        map_scale_x = (xmax_map - xmin_map) / self.map_width
        map_scale_y = (ymax_map - ymin_map) / self.map_height
            # Extrapolate pixels to map proj units (linear in proj system, not linear in GPS system)
        x_map = xmin_map + self.x * map_scale_x
        y_map = ymin_map + self.y * map_scale_y  # ymin_map refers to the value at the top of the map and the scale should be negative here
        # Convert to GPS system
        self.x, self.y = self.to_gps.transform(x_map, y_map)
        self.coord_type = 'gps'
    
    
    def gps2pixel(self) -> None:
        '''
        Convert GPS coordinates to (EPSG:3857 coordinates) then to pixel
        '''
        if self.coord_type == 'pixel':
            print('WARNING coord are already in pixel system')
            return
        
        # Convert GPS to 3857 system
        self.x, self.y = self.to_map.transform(self.x, self.y)
        
        # Find extreme values of the map in 3857 coord
        # x axis is lon and y axis is lat
        xmin_map, ymin_map = self.to_map.transform(self.map_lim['lon_min'], self.map_lim['lat_min'])
        xmax_map, ymax_map = self.to_map.transform(self.map_lim['lon_max'], self.map_lim['lat_max'])
        
        # Find the pixel for each coordiante
        self.x = math.floor((self.x - xmin_map) / (xmax_map - xmin_map) * self.map_width)
        self.y = math.floor((self.y - ymin_map) / (ymax_map - ymin_map) * self.map_width)
        self.coord_type = 'pixel'
        
        # Create the pixel coor if not existant
        if not hasattr(self, 'x_pixel') and not hasattr(self, 'y_pixel'):
            # Adjust for the top band space
            self.x_pixel = self.x + self.map_topleft_x
            self.y_pixel = self.y + self.map_topleft_y
        
        
    def calculate_distance(self, target_pos:tuple[int|float, int|float]) -> int|float:
        '''
        Calculate the distance in km between two gps coordinates
        '''
        target_x, target_y = target_pos
        distance_km = haversine(lon1 = self.x, 
                                lat1 = self.y,
                                lon2 = target_x,
                                lat2 = target_y)
        return(distance_km)

    
    def place_marker(self, window):
        '''
        Place a marker at the location.
        Put the arrow tip at the location --> middle bottom position
        '''
        if self.marker_surface is None:
            print("ERROR: No marker_surface given when creating class")
            return
        
        if not hasattr(self, 'x_pixel') or not hasattr(self, 'y_pixel'):
            # COnvert to pixel to plot if needed
            print("WARNING converting coord to pixel before plotting")
            self.gps2pixel(self)
        
        marker_rect = self.marker_surface.get_rect()
        marker_rect.midbottom = (self.x_pixel, self.y_pixel)
        window.blit(self.marker_surface, marker_rect)
        
        # Blit the marker name if it has one
        if hasattr(self, 'marker_name'):
            x_text, y_text = marker_rect.midtop
            marker_text = Text(
                text=self.marker_name,
                x=x_text,
                y=y_text,
                anchor='midbottom',
                color=self.marker_color)
            marker_text.display(window)


    def name_marker(self, name="Lorem Ipsum", color=color_dict['white']):
        '''
        Give a name to the marker
        Will be displayed when marker is shown
        '''
        # Find position to plot
        self.marker_name = name
        self.marker_color = color


class GeoMap():
    '''
    Store the map and its relative data
    '''
    def __init__(
            self, 
            map_width: int=config_dict['MAP_WIDTH'],
            map_height: int=config_dict['MAP_HEIGHT'],
            map_file: str=config_dict['map_file'],
            window_width:int =config_dict['WINDOW_WIDTH'],
            window_height:int =config_dict['WINDOW_HEIGHT']
                ) -> None:

        self.width = map_width
        self.height = map_height
        self.file = map_file
        
        # Load map
        self.surface = pygame.image.load(self.file)
        self.surface = pygame.transform.scale(self.surface, (self.width, self.height))
        
        # Find topleft coordinates
        self.topleft_x = window_width - self.width
        self.topleft_y = window_height - self.height
    
    
    def display(self, window: pygame.Surface, pos: str='auto') -> None:
        '''
        Blit the image on window
        '''
        if pos == 'auto':
            pos = (self.topleft_x, self.topleft_y)
        window.blit(self.surface, pos)


class TopBand():
    '''
    Create a band at the top of the display
    Used to print score, objective and other info
    '''
    def __init__(
            self,
            x: int|float=0,
            y: int|float=0,
            width: int=config_dict['WINDOW_WIDTH'],
            height: int=50,
            color_dict: dict[str:tuple[int, int, int]]=color_dict
                ) -> None:
        
        grey = color_dict['grey']
        black = color_dict['black']
        
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height))
        self.image.fill(grey)
        
        self.rect = self.image.get_rect()


    def display(self, window: pygame.Surface, pos: str='auto') -> None:
        '''
        Blit the image on window
        '''
        if pos == 'auto':
            pos = self.rect.topleft
        window.blit(self.image, pos)
        
        
class Text():
    '''
    Holds information for text to display
    '''
    def __init__(
            self,
            text: str="Lorem Ipsum",
            x: int|float=0,
            y: int|float=0,
            anchor: str='topleft',
            fontName: str='freesansbold.ttf',
            fontSize: int=35,
            color: tuple[int, int , int]=(0,0,0)
                 ) -> None:
        
        # Import data
        self.text = str(text)  # text to display
        self.font_name = fontName  # Font name in pygame font available
        self.font_size = int(fontSize)  # size in pixel
        self.color = color  # tuple, RGB color
        
        self.x = x  # position where to put the text
        self.y = y
        self.anchor = anchor  # key word to dicate text postioning relative to the x-y position
        
        # create GUI elements
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        # Position the text
        setattr(self.rect, self.anchor, (self.x, self.y))

    
    def rotate(self, angle: int|float) -> None:
        '''
        angle is int in degree
        positive is counter clockwise and negative clockwise
        '''
        self.surface = pygame.transform.rotate(self.surface, angle) 
        self.rect = self.surface.get_rect()    
    

    def move(self, x: int|float, y: int|float, anchor: str|None=None) -> None:
        '''
        Position the text at the given location
        '''
        self.x = x
        self.y = y
        if anchor is not None:
            self.anchor = anchor
        setattr(self.rect, self.anchor, (self.x, self.y))


    def update(self) -> None:
        '''
        Update surface if text was changed
        '''
        # update GUI elements
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        # Position the text
        setattr(self.rect, self.anchor, (self.x, self.y))


    def display(self, window: pygame.Surface) -> None:
        # Display
        window.blit(self.surface, self.rect)


class FakeWindow():
    '''
    Create a simily window but is just a rectangle
    '''
    def __init__(
            self,x: int=0,
            y: int=0,
            width: int=10,
            height: int=10,
            color: tuple[int, int, int]=(190,190,190),
            anchor: str='topleft'
            ) -> None:
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.anchor = anchor
        
        # create the surface
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.color)
        self.rect = self.surface.get_rect()
        
        # position the surface
        setattr(self.rect, self.anchor, (self.x, self.y))
    
    
    def display(self, window: pygame.Surface) -> None:
        window.blit(self.surface, self.rect)
    

class Button():
    
    def __init__(
            self,
            text: str='Lorem Ipsum',
            x: int|float=0,
            y: int|float=0,
            width: int|float=10,
            height: int|float=10,
            command: None=None,  # Not implemented yet
            font: str='freesansbold.ttf',
            font_size: int=15,
            color_normal: tuple[int, int , int]=(169,169,169),
            color_hovered: tuple[int, int , int]=(100,100,100),
            anchor: str='topleft',
            parent: str='window'
                 ) -> None:
        
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.command = command
        self.font_name = font
        self.font_size = font_size
        self.anchor = anchor
        self.parent = parent  # rect object to extract reference coord
        
        self.color_normal = color_normal
        self.color_hovered = color_hovered
        
        # Create font and surfaces
        self.surface_normal = pygame.Surface((self.width, self.height))
        self.surface_normal.fill(self.color_normal)
        
        self.surface_hovered = pygame.Surface((self.width, self.height))
        self.surface_hovered.fill(self.color_hovered)
        
        # surface hold the current button to display
        self.surface = self.surface_normal
        self.rect = self.surface.get_rect()
        
        self.font = pygame.font.Font(self.font_name, self.font_size)
        
        self.text_image = self.font.render(self.text, True, (255, 255, 255))
        
        # For text in the center of button
        self.text_rect = self.text_image.get_rect(center = self.rect.center)
        
        # Create the two possible version of the button, normal and hovered
        self.surface_normal.blit(self.text_image, self.text_rect)
        self.surface_hovered.blit(self.text_image, self.text_rect)

        # you can't use it before `blit`
        setattr(self.rect, self.anchor, (self.x, self.y))

        self.hovered = False
        self.clicked = False


    def update(self) -> None:

        if self.hovered:
            self.surface = self.surface_hovered
        else:
            self.surface = self.surface_normal
    
        
    def handle_event(self, event: pygame.event.Event) -> None:

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            self.update()
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.hovered:
                self.clicked = True


    def display(self, window: pygame.Surface) -> None:
        window.blit(self.surface, self.rect)


class Line():
    def __init__(
            self,
            window: pygame.Surface,
            marker_A: 'Location',
            marker_B: 'Location',
            score: int=1000,
            distance: int|float=0,
            color: tuple[int, int, int]=(0,0,0),
            width: int=2,
            offset: int=10
                ) -> None:
        
        '''
        window is the display surface
        marker_A and marker_B are Location objects
        
        Generate Text objects to print the score and distance along the line
        offset controls how far they are printed from the line
        
        General case: plot the text along the middle of the line
                      angle the text along the line slope
                      plot score on one side and distance on the other
                      Adapt according to relative position of marker and line length
        
        Find the slope of the line from player to target.
        
        By default put the score on the left of a positive slope and right of a negative one
            
                 /                \               score
          score / dist   or  dist \ score     ------------
               /                  \               dist

        
        '''
        
        # Required to draw the line between marker
        self.color = color
        self.width = width
        
        self.start_pos = (marker_A.x_pixel, marker_A.y_pixel)
        self.end_pos = (marker_B.x_pixel, marker_B.y_pixel)
        
        # Display line
        self.line_rect = pygame.draw.line(window,
                                         color=self.color,
                                         start_pos=self.start_pos,
                                         end_pos=self.end_pos,
                                         width=self.width)
        
        # Calculate where to display score and distance along the line
        self.score = score
        self.distance = distance
        self.offset = offset
        
        # Find line slope
        if marker_A.x_pixel == marker_B.x_pixel:
            self.slope = 'inf'
            self.angle = 90
        else:
            self.slope = (marker_B.y_pixel - marker_A.y_pixel + 1) / (marker_B.x_pixel - marker_A.x_pixel + 1)
            self.angle = np.degrees(np.arctan(self.slope))
        
        
        # Create Text object and rotate to match slope
        self.score_text = Text(
            text = f'{self.score} pts',
            x=0,
            y=0,
            anchor='topleft',
            fontSize=30)
        self.distance_text = Text(
            text = f'{self.score} pts',
            x=0,
            y=0,
            anchor='topleft',
            fontSize=30)
        
        self.marker_A = marker_A
        self.marker_B = marker_B
        self.window_height = window.get_height()


    def find_score_distance_positions(self) -> None:
        
        # Find if markers are too close to print along the line
        if self.score > 700 or self.distance < 100:
            self.is_close = 1
        else:
            self.is_close = 0
        
        # Special case, markers are close and line is too small to print
        
        if self.is_close:
            '''
            Plot horizontally, above or below the markers 
            '''
            lowest_pixel = max(self.marker_A.marker_surface.get_rect().bottomleft[1], self.marker_B.marker_surface.get_rect().bottomleft[1])
            
            self.score_text.x, self.score_text.y = self.line_rect.center
            self.distance_text.x, self.distance_text.y = self.line_rect.center
            
            if lowest_pixel >= 0.9 * self.window_height:
                # plot above
                highest_pixel = min(self.marker_A.rect.topleft[1], self.marker_B.rect.topleft[1])
                self.distance_text.y = highest_pixel - self.offset
                self.distance_text.anchor = 'midbottom'
                self.distance_text.update()
                
                self.score_text.y = self.distance_text.rect.midtop[1] - self.offset
                self.score_text.anchor = 'midbottom'
                self.score_text.update() 
            else:
                # plot below
                self.score_text.y = lowest_pixel + self.offset
                self.score_text.anchor = 'midtop'
                self.score_text.update() 
                
                self.distance_text.y = self.score_text.rect.midbottom[1] + self.offset
                self.distance_text.anchor = 'midtop'
                self.distance_text.update() 
            
            return None
        
        # General case : plot at angle
                
        # # Slope is delta_y / delta_x
        # if target_pos.x_pixel == player_pos.x_pixel:
        #     slope = 'inf'
        #     angle = 90
        # else:
        #     slope = (target_pos.y_pixel - player_pos.y_pixel + 1) / (target_pos.x_pixel - player_pos.x_pixel + 1)
        #     angle = np.degrees(np.arctan(slope))
        
        # if slope >= 0 or slope == 'inf':
        #     return_text.rotate(int(round(-angle, 0)))
        #     text_x, text_y = line_rect.center
        #     if value_type == 'score':
        #         # Score is on left
        #         text_x = text_x - 10
        #         text_y = text_y - 10
        #         text_anchor = 'midbottom'
        #     elif value_type == 'distance':
        #         # Distance is on right
        #         text_x = text_x + 10
        #         text_y = text_y + 10
        #         text_anchor = 'topbottom'
        # else:
        #     return_text.rotate(int(round(angle, 0)))
        #     text_x, text_y = line_rect.center
        #     if value_type == 'score':
        #         # Score is on left
        #         text_x = text_x - 10
        #         text_y = text_y - 10
        #         text_anchor = 'topbottom'
        #     elif value_type == 'distance':
        #         # Distance is on right
        #         text_x = text_x + 10
        #         text_y = text_y + 10
        #         text_anchor = 'midbottom'
        
        # return_text.move(x=text_x, y=text_y, anchor=text_anchor)
        # return(return_text)
        
    # def display_guess_score(self, window):
    #     self.score_text.display(window)
    
    # def display_distance_score(self, window):
    #     self.distance_text.display(window)