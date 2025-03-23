# -*- coding: utf-8 -*-
"""
Helper classes
"""
from helper import load_database
import pandas as pd

class Database:
    def __init__(self) -> None:
        # set game mode parameters
        
        # Maybe get to top 3 or 5 cities for each department
        # self.pop_threshold = 30000
        self.top_city_to_keep = 2  # Number of city per group (eg department) to keep
        
        # load subset of database according to gamemode
        self.database = load_database()
        # Sort by dpt and pop
        self.database = self.database.sort_values(by = ['department_number', 'city_population'],
                                      ascending = [True, False])
        # Group by dpt and only keep top sities after sorting
        grouped_db = self.database.groupby('department_number')
        self.database = grouped_db.head(self.top_city_to_keep)
        
        
    def get_city_data(self) -> pd.DataFrame:
        '''
        return a random city data 
        '''
        sample_df = self.database.sample(n=1)
        # only keep relevant columns
        sample_df = sample_df.loc[:,['city_name_raw', 'latitude', 'longitude']]
        return(sample_df)
    
    
    def get_paris_data(self) -> pd.DataFrame:
        '''
        test function that always return paris data if possible
        '''
        sample_df = self.database.loc[self.database['city_name_raw'] == 'Paris']
        # only keep relevant columns
        sample_df = sample_df.loc[:,['city_name_raw', 'latitude', 'longitude']]
        return(sample_df)