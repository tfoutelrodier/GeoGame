# -*- coding: utf-8 -*-
"""
Gather all functions related to establishing a database for all city in france

Data is stored in a csv file

Data with geographical position where downloaded from
https://www.data.gouv.fr/fr/datasets/villes-de-france/#/community-resources
(data updated september 2022)
Data is a json file with following information
            "insee_code": "25620",
            "city_code": "ville du pont",
            "zip_code": "25650",
            "label": "ville du pont",
            "latitude": "46.999873398",
            "longitude": "6.498147193",
            "department_name": "doubs",
            "department_number": "25",
            "region_name": "bourgogne-franche-comt\u00e9",
            "region_geojson_name": "Bourgogne-Franche-Comt\u00e9"

Population data was taken from the 2021 INSEE census.
Data is divided stored in xslx files, one per department, named after department number

A table with correspondance between department name and number was also made. 

Merge all databases to have the following informations at minimal:
    city name: str
    lat : str
    lon : str
    population : int
    dpt name : str
    dpt nb : int
    extra_state : str (prefecture, sous prefecture...) --> optional
    


"""

import pandas as pd
import os
import json
from helper import csv2dict


def load_nb2name_dict():
    # Import name/department table
    nb2name_dict = csv2dict(os.path.join('raw_data/dpt_numer2_name_table.csv'),
                             separator = ";",
                             header = True)
    return(nb2name_dict)


def load_loc_data():
    # Import localization data
    with open(os.path.join('raw_data/cities_location.json'), 'r') as f:
        loc_dict = json.load(f, encoding = 'latin1')
    loc_df = pd.DataFrame(loc_dict['cities'])
    return(loc_df)


def clean_loc_data(loc_df):
    '''
    Only keep town in metropolitan area
    '''
    loc_df = loc_df[loc_df['department_number'].str.len() < 3]

    # Drop unneeded columns
    col_to_drop = [
        'insee_code',
        'zip_code',
        'region_geojson_name',
        'label'
        ]
    loc_df.drop(columns=col_to_drop, inplace = True)
    loc_df = loc_df.drop_duplicates()  # remove duplicates
    return(loc_df)


def load_population_data():
    # Import population data
    df_lst = []
    for dpt_number in nb2name_dict:
        df = pd.read_excel(os.path.join("".join(['raw_data/department_population/dep', dpt_number, '.xlsx']))
                           ,sheet_name='Communes',
                           skiprows = 7)
        df['department_number'] = dpt_number
        df['department_name'] = nb2name_dict[dpt_number] 
        df_lst.append(df)

    # Concatenate all
    population_df = pd.concat(df_lst)
    return(population_df)


def clean_population_data(population_df):
    # remove duplicates
    # create a column to clean city name before merge with location data
    # returns cleaned dataset
    population_df['cleaned_name']= population_df['Nom de la commune']
    population_df['cleaned_name']= population_df['cleaned_name'].str.lower()
    # Pattern to change to make loc and pop data match
    pattern_lst = [
        [r"[\' ]", " "],
        [r'[éèêë]','e'],
        [r'œ','oe'],
        [r'ñ','n'],
        [r'ÿ','y'],
        [r'\bsaint\b','st'],
        [r'\bsainte\b','ste'],
        [r'[ûùúü]','u'],
        [r'[îìíï]','i'],
        [r'[ôòóõö]','o'],
        [r'[àâáãä]','a'],
        [r'[ç]','c'],
        [r'-',' '],
        [r' +',' ']]
    for search, replace in pattern_lst:
        population_df['cleaned_name'] = population_df['cleaned_name'].str.replace(search,replace, regex=True)    
    
    #remove uneeded columns
    col_to_drop = [
        'Code arrondissement',
        'Code canton',
        'Code commune',
        'Population comptée à part',
        'Population totale'
        ]
    population_df.drop(columns=col_to_drop, inplace = True)
    population_df = population_df.drop_duplicates()
    
    return(population_df)


def extract_big_city_pop_data(city, discarded_pop_df):
    # city = city name (str)
    city_lower = city.lower()
    regex = r''.join([city_lower, '\s[0-9]+(?:e|er)\sarrondissement'])
    city_pop_df = discarded_pop_df[discarded_pop_df['cleaned_name'].str.contains(regex)]
    city_data = city_pop_df.iloc[0,:].copy()
    # Change manually the required values
    city_data['Nom de la commune'] = city
    city_data['cleaned_name'] = city_lower
    city_data['Population municipale'] = sum(city_pop_df['Population municipale'].to_list())
    return(city_data)


def extract_big_city_loc_data(city, discarded_loc_df):
    # city = city name (str)
    city_lower = city.lower()
    regex = r''.join([city_lower, '\s[0-9]+'])
    city_loc_df = discarded_loc_df[discarded_loc_df['city_code'].str.contains(regex)]
    city_data = city_loc_df.iloc[0,:].copy()
    # Change manually the required values
    city_data['city_code'] = city_lower
    return(city_data)


def extract_big_city_data(city, merge_df, population_df, location_df):
    # Returns a pandas series with the proper data for cities with arrondissements
    
    discarded_loc_df = loc_df[ ~loc_df['city_code'].isin(merge_df['city_code'])]
    discarded_pop_df = population_df[ ~population_df['cleaned_name'].isin(merge_df['cleaned_name'])]
    
    #rename and drop colums to match the merge df
    discarded_loc_df = discarded_loc_df.rename(columns={'department_name': 'department_name_x'})
    discarded_pop_df = discarded_pop_df.rename(columns={'department_name': 'department_name_y'})
    discarded_pop_df = discarded_pop_df.drop(columns='department_number')
    
    pop_data = extract_big_city_pop_data(city, discarded_pop_df)
    loc_data = extract_big_city_loc_data(city, discarded_loc_df)
    
    city_data = pd.concat([pop_data, loc_data], axis=0)
    return(city_data)



'''
Dataset generation
'''
if __name__ == '__main__':

    # load and clean a bit data
    nb2name_dict = load_nb2name_dict()
    loc_df = load_loc_data()
    loc_df = clean_loc_data(loc_df)

    population_df = load_population_data()
    population_df = clean_population_data(population_df)

    merge_df = pd.merge(left=loc_df,
                        right=population_df,
                        left_on=['city_code', 'department_number'],
                        right_on=['cleaned_name', 'department_number']
                        )

    # add data for big cities with arrondissement
    big_cities_lst = ['Paris', 'Marseille', 'Lyon']
    for city in big_cities_lst:
        city_data = extract_big_city_data(city, merge_df, population_df, loc_df)
        # add to merge df
        merge_df = pd.concat([merge_df, pd.DataFrame([city_data])], ignore_index=True)
        # print(city_data)

    # Change columns names to final names for usages
    merge_df = merge_df.drop(columns=['department_name_y',
                                    'cleaned_name',
                                    'Code département'])
    merge_df = merge_df.rename(columns={'department_name_x': 'department_name',
                                        'Code région':'region_number',
                                        'Nom de la région':'region_name_raw',
                                        'Nom de la commune':'city_name_raw',
                                        'Population municipale':'city_population',
                                        'city_code':'city_name'})

    # save merge df:
    merge_df.to_csv('data/cities_data.csv', sep = ";",
                    header = True, index=False)
