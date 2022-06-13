#ziilow wrangle module
#stephen fitzsimon

import os

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from env import get_db_url

RAND_SEED = 987
FILENAME = 'zillow_clustering_data.csv'

def wrangle_data():
    df = get_zillow_data()
    df = filter_properties(df)
    df = handle_missing_values(df, 0.99, 0.99)
    return df

def get_zillow_data(query_db=False):
    '''Acquires the zillow data from the database or the .csv file if if is present

    Args:
        query_db = False (Bool) :  Forces a databse query and a resave of the data into a csv.
    Return:
        df (DataFrame) : a dataframe containing the data from the SQL database or the .csv file
    '''
    #file name string literal
    #check if file exists and query_dg flag
    if os.path.isfile(FILENAME) and not query_db:
        #return dataframe from file
        print('Returning saved csv file.')
        return pd.read_csv(FILENAME).drop(columns = ['Unnamed: 0'])
    else:
        #query database 
        print('Querying database ... ')
        query = '''
        SELECT predictions_2017.logerror, e.transdate, 
                properties_2017.*, 
                typeconstructiontype.typeconstructiondesc, 
                storytype.storydesc, 
                propertylandusetype.propertylandusedesc, 
                heatingorsystemtype.heatingorsystemdesc, 
                airconditioningtype.airconditioningdesc, 
                architecturalstyletype.architecturalstyledesc, 
                buildingclasstype.buildingclassdesc
            FROM (SELECT max(transactiondate) AS transdate, parcelid FROM predictions_2017 GROUP BY parcelid) AS e
                JOIN predictions_2017 ON predictions_2017.transactiondate = e.transdate AND predictions_2017.parcelid = e.parcelid
                JOIN properties_2017 ON properties_2017.parcelid = predictions_2017.parcelid
                LEFT JOIN airconditioningtype USING (airconditioningtypeid)
                LEFT JOIN architecturalstyletype USING (architecturalstyletypeid)
                LEFT JOIN buildingclasstype USING (buildingclasstypeid)
                LEFT JOIN heatingorsystemtype USING (heatingorsystemtypeid)
                LEFT JOIN propertylandusetype USING (propertylandusetypeid)
                LEFT JOIN storytype USING (storytypeid)
                LEFT JOIN typeconstructiontype USING (typeconstructiontypeid);
        '''
        #get dataframe from a 
        df = pd.read_sql(query, get_db_url('zillow'))
        print('Got data from the SQL database')
        #save the dataframe as a csv
        df.to_csv(FILENAME)
        print('Saved dataframe as a .csv!')
        #return the dataframe
        return df

def return_col_percent_null(df, max_null_percent = 1.0):
    '''Returns a dataframe with columns of the column of df, the percent nulls in the column, and the count of nulls.

    Args:
        df (dataframe) : a dataframe 
        max_null_percent = 1.0 (float) : returns all columns with percent nulls less than max_null_percent
    Return:
        (dataframe) : dataframe returns with df column names, percent nulls, and null count
    '''
    outputs = [] #to store output
    for column in df.columns: #loop through the columns
        #store and get information
        output = {
            'column_name': column,
            'percent_null' : round(df[column].isna().sum()/df[column].shape[0], 4),
            'count_null' : df[column].isna().sum()
        }
        #append information
        outputs.append(output)
    #make a dataframe
    columns_percent_null = pd.DataFrame(outputs)
    #return the dataframe with the max_null_percent_filter
    return columns_percent_null[columns_percent_null.percent_null <= max_null_percent]

def handle_missing_values(df, prop_required_column, prop_required_row):
    '''Returns a dataframe that is filtered by the percent of non-null values in the columns and the rows
    
    Args:
        df (dataframe) : a zillow dataframe
        prop_required_column (float) : the percent of the column values that are not null
        prop_required_row (float) : the percent of the row values that are not null
    Returns:
        df (dataframe) : a filtered dataframe
    '''
    #get the proportion of nulls in each column
    null_proportion_df = return_col_percent_null(df)
    #get the columns to keep
    columns_to_keep = null_proportion_df[null_proportion_df['percent_null'] < ( 1 - prop_required_column)]['column_name'].tolist()
    # get the columns from the dataframe
    df = df[columns_to_keep]
    #filter the rows
    df = df[(df.isnull().sum(axis=1)/df.shape[1] < (1 - prop_required_row))]
    return df

def filter_properties(df):
    df = df[df['unitcnt'] == 1]
    filter_cols = ['Single Family Residential', 'Mobile Home', 'Manufactured, Modular, Prefabricated Homes', 'Residential General', 'Townhouse']
    df = df[df['propertylandusedesc'].isin(filter_cols)]
    return df