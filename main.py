# -*- coding: utf-8 -*-
"""
All functions related to displaying and interacting with the gui
"""

import pygame

from database_class import Database
from gui_classes import GeoMap, Location, TopBand, Text, Button, FakeWindow, Line
from config import config_dict, color_dict
from helper import render_text, calculate_score

if __name__ == '__main__':
    # load some colors
    black = color_dict['black']
    white = color_dict['white']
    grey = color_dict['grey'] 
    red = color_dict['red']

    # Some base variable
    total_score = 0  # Cummulated score
    has_guessed = 0  # To control display if player just made a guess
    current_game_number = 1  # Game number to know when to end the game
    max_game_number = config_dict['max_game_number']
    has_game_ended = 0

    # pygame setup
    pygame.init()
    # Limit FPS to 60
    clock = pygame.time.Clock()
    max_fps = config_dict['max_fps']

    # Setup window
    window = pygame.display.set_mode((config_dict['WINDOW_WIDTH'], config_dict['WINDOW_HEIGHT']))
    pygame.display.set_caption("Geo game v2")

    # Load the map
    geo_map = GeoMap()

    # Create top band
    top_band = TopBand(height=geo_map.topleft_y)

    # Create marker assets to print
    marker_map_ratio = config_dict['marker_map_ratio']
    target_marker_file = config_dict['target_marker_file']
    player_marker_file = config_dict['player_marker_file']

    target_marker_surface = pygame.image.load(target_marker_file)
    player_marker_surface = pygame.image.load(player_marker_file)

    marker_width, marker_height = target_marker_surface.get_size()
    marker_dim_ratio = marker_height / marker_width
    
    # Scale marker size to map
    target_marker_surface = pygame.transform.scale(target_marker_surface, (geo_map.width * marker_map_ratio, geo_map.height * marker_map_ratio * marker_dim_ratio))
    player_marker_surface = pygame.transform.scale(player_marker_surface, (geo_map.width * marker_map_ratio, geo_map.height * marker_map_ratio * marker_dim_ratio))

    # Load and initialize city database
    database = Database()

    # Get first target data
    city_data = database.get_city_data()
    city_name = city_data['city_name_raw'].iloc[0]

    target_pos = Location(marker_surface=target_marker_surface,
                        loc=(city_data['longitude'].iloc[0], city_data['latitude'].iloc[0]),
                        coord_type='gps',
                        geo_map=geo_map)
    target_pos.gps2pixel()
    target_pos.name_marker(name=city_name)



    # Prepare text to display
    score_text = Text(
        text=f"Score: {total_score}",
        x=geo_map.width * 0.78,
        y=top_band.height / 2 - 0.2 * top_band.height,
        anchor='topleft')

    target_city_text = Text(
        text=f"{city_name}",
        x=geo_map.width * 0.01,
        y=score_text.y,
        anchor='topleft')

    guess_number_text = Text(
        text=f"Ville {current_game_number} / {max_game_number}",
        x=score_text.rect.bottomright[0] - geo_map.width * 0.2,
        y=score_text.rect.bottomright[1],
        anchor='bottomright')

    # Initial display of the screen
    # Clear the screen
    window.fill(white)
    # Draw the map
    window.blit(geo_map.surface, (geo_map.topleft_x, geo_map.topleft_y))

    # draw the topband
    window.blit(top_band.image, top_band.rect.topleft)
    # Display topband text
    score_text.display(window)
    target_city_text.display(window)
    guess_number_text.display(window)


    # prepare end of game assets (replay/quit window)
    game_end_window = FakeWindow(
        x = window.get_width() // 2,
        y = window.get_height() // 2,
        width = 300,
        height = 200,
        anchor = 'center'
        )

    replay_button = Button(
        text="Rejouer",
        x=game_end_window.rect.bottomleft[0] + 0.1 * game_end_window.width,
        y=game_end_window.rect.bottomleft[1] - 0.1 * game_end_window.height,
        width=0.3 * game_end_window.width,
        height=0.2 * game_end_window.height,
        anchor='bottomleft'
        )

    quit_button = Button(
        text = "Quitter",
        x = game_end_window.rect.bottomright[0] - 0.1 * game_end_window.width,
        y = game_end_window.rect.bottomright[1] - 0.1 * game_end_window.height,
        width = 0.3 * game_end_window.width,
        height = 0.2 * game_end_window.height,
        anchor = 'bottomright'
        )

    end_game_text = Text(
        text=f"Score final: {total_score}",
        x=game_end_window.rect.topleft[0] + 0.1 * game_end_window.width,
        y=game_end_window.rect.topleft[1] + 0.1 * game_end_window.height,
        anchor='topleft'
        )

    # Update the display
    pygame.display.update()

    # Main Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if has_game_ended == 1:
                # If game has ended all events go to the button
                replay_button.handle_event(event)
                quit_button.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONUP and has_guessed == 1:
                # If player click to go to next city
                has_guessed = 0
                # new target
                # city_data = database.get_city_data()
                city_data = database.get_city_data()
                city_name = city_data['city_name_raw'].iloc[0]
                target_city_text.text = f"{city_name}"  # update display
                target_pos = Location(marker_surface=target_marker_surface,
                                    loc=(city_data['longitude'].iloc[0], city_data['latitude'].iloc[0]),
                                    coord_type='gps',
                                    geo_map=geo_map)
                target_pos.gps2pixel()
                target_pos.name_marker(name=city_name)
                
                
                if current_game_number < max_game_number:
                    # Update game number
                    current_game_number += 1
                    guess_number_text.text = f"Ville {current_game_number} / {max_game_number}"
                else:
                    # End of current game
                    has_game_ended = 1
                    end_game_text.text = f"Score final: {total_score}"
                
            elif event.type == pygame.MOUSEBUTTONUP and has_guessed == 0:
                has_guessed = 1

                player_pos = Location(marker_surface=player_marker_surface,
                                    loc=pygame.mouse.get_pos(),
                                    coord_type='pixel',
                                    geo_map=geo_map)
                player_pos.pixel2gps()
                
                # calculate score
                distance = round(player_pos.calculate_distance((target_pos.x_gps, target_pos.y_gps)), 1)
                score = calculate_score(distance, config_dict)
                total_score += score
                
                player_pos.name_marker(name=f'{distance} km = {score} pts')
                
                # Update score
                score_text.text = f"Score: {total_score}"
        
        # Display loop when there is no event
        window.fill(white)  # Clear the screen
        geo_map.display(window)  # Draw the map
        top_band.display(window)  # draw the topband
        
        score_text.update()
        score_text.display(window)  # display score
        if not has_game_ended:
            target_city_text.update()
            target_city_text.display(window)  # display target name
        guess_number_text.update()
        guess_number_text.display(window)  # current game number

        if has_game_ended:
            game_end_window.display(window)
            replay_button.display(window)
            quit_button.display(window)
            end_game_text.update()
            end_game_text.display(window)
            
            # Check if end game button clicked
            if quit_button.clicked == True:
                running = False
            elif replay_button.clicked == True:
                # restart the variables
                    # score displayed
                total_score = 0
                score_text.text = f"Score: {total_score}"
                    # Game number
                current_game_number = 1
                guess_number_text.text = f"Ville {current_game_number} / {max_game_number}"
                
                    # Reset variables
                has_guessed = 0
                has_game_ended = 0
                replay_button.clicked = False
                replay_button.hovered = False
                replay_button.update()
                
        # Display marker if relevant
        if has_guessed == 1:
            # display line between markers
            # Do it first to be under markers
            # Add score along the line with km distance
            error_line = Line(window=window,
                            marker_A=player_pos,
                            marker_B=target_pos)
            # error_line.find_score_distance_positions()
            
            # Display marker
            player_pos.place_marker(window)
            target_pos.place_marker(window)
            
            # display score and distance
            # error_line.display_distance_score(window)
            # error_line.display_guess_score(window)
            
        # Update the display
        pygame.display.update()     
        clock.tick(max_fps)

    # Quit Pygame
    pygame.quit()

