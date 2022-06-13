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

COLUMNS_TO_DROP = [
    'airconditioningtypeid',
    'architecturalstyletypeid',
    'basementsqft',
    'buildingclasstypeid',
    'buildingqualitytypeid',
    'decktypeid',
    'finishedfloor1squarefeet',
    'finishedsquarefeet13',
    'finishedsquarefeet15',
    'finishedsquarefeet50',
    'finishedsquarefeet6',
    'fireplacecnt',
    'garagecarcnt',
    'garagetotalsqft',
    'hashottuborspa',
    'heatingorsystemtypeid',
    'poolcnt',
    'poolsizesum',
    'pooltypeid10',
    'pooltypeid2',
    'pooltypeid7',
    'propertyzoningdesc',
    'regionidcity',
    'regionidneighborhood',
    'storytypeid',
    'threequarterbathnbr',
    'typeconstructiontypeid',
    'unitcnt',
    'yardbuildingsqft17',
    'yardbuildingsqft26',
    'numberofstories',
    'fireplaceflag',
    'taxdelinquencyflag',
    'taxdelinquencyyear',
    'taxamount',
    'structuretaxvaluedollarcnt',
    'landtaxvaluedollarcnt',
    'calculatedbathnbr', 
    'fullbathcnt', 
    'finishedsquarefeet12',
    'propertylandusetypeid',
    'regionidcounty', 
    'propertycountylandusecode',
    'regionidzip',
    'assessmentyear',
    'censustractandblock',
    'rawcensustractandblock',
    'roomcnt',
    'id'
 ]

def wrangle_zillow(df):
    df = zillow_drop_columns(df)
    df = prepare_zillow_data(df)
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

def zillow_drop_columns(df,
                        columns_to_drop = COLUMNS_TO_DROP):
    ''''
    Drops the columns from the zillow dataframe as determined in the final report.

    Args:
        df (dataframe) : a dataframe containging zillow data
        columns_to_drop (list) : a list of columns to drop, default = COLUMNS_TO_DROP module constant

    Return:
        (dataframe) : a dataframe with the specified columns dropped
    '''
    return df.drop(columns = columns_to_drop)

def clearing_fips(df):
    '''This function takes in a DataFrame of unprepared Zillow information and generates a new
    'county' column, with the county name based on the FIPS code. Drops the 'fips' column and returns
    the new DataFrame.

    Args:
        df (Dataframe) : dataframe containing zillow data
    Return:
        (DataFrame) : a dataframe with a cleared fips columns
    '''
    # create a list of our conditions
    fips = [
        (df['fips'] == 6037.0),
        (df['fips'] == 6059.0),
        (df['fips'] == 6111.0)
        ]
    # create a list of the values we want to assign for each condition
    counties = ['Los Angeles', 'Orange', 'Ventura']
    # create a new column and use np.select to assign values to it using our lists as arguments
    df['county'] = np.select(fips, counties)
    df = df.drop(columns = 'fips')
    return df

def prepare_zillow_data(df):
    '''Prepares the zillow data by dropping nulls and all rows with bedroomcnt > 0, bathroomcnt > 0
    and calculatedfinishedsquarefeet > 14
    
    Args:
        df (DataFrame) : dataframe to prepare
    Return:
        df (DataFrame) : prepared dataframe
    '''
    #drop the nulls
    df = df.dropna()
    #apply the boolean conditions
    #exclude very small houses
    df = df[(df.bedroomcnt > 0) & (df.bathroomcnt > 0) & (df.calculatedfinishedsquarefeet > 149)]
    #exclude very large houses
    df = df[(df.bedroomcnt < 7) & (df.bathroomcnt < 7)]
    #exclude large square feet houses
    df = df[df.calculatedfinishedsquarefeet <= 6000]
    #exlude large acreage
    df = df[df.lotsizesquarefeet < 2.178002e5]
    #cast datatypes appropriately
    df['bedroomcnt'] = df['bedroomcnt'].astype(np.uint8)
    df['calculatedfinishedsquarefeet'] = df['calculatedfinishedsquarefeet'].astype(np.uint)
    df['yearbuilt'] = df['yearbuilt'].astype(np.uint)
    df['taxvaluedollarcnt'] = df['taxvaluedollarcnt'].astype(np.uint)
    #map the fips code
    df = clearing_fips(df)
    #fix the latitude and longitude columns
    df['longitude'] = df['longitude']*(10**-6)
    df['latitude'] = df['latitude']*(10**-6)
    return df

def split_zillow_data(df):
    '''splits the zillow dataframe into train, test and validate subsets
    
    Args:
        df (DataFrame) : dataframe to split
    Return:
        train, test, validate (DataFrame) :  dataframes split from the original dataframe
    '''
    #make train and test
    train, test = train_test_split(df, train_size = 0.8, random_state=RAND_SEED)
    #make validate
    train, validate = train_test_split(train, train_size = 0.7, random_state=RAND_SEED)
    return train, validate, test

def zillow_scale(df,
                column_names = ['bathroomcnt', 'bedroomcnt', 'calculatedfinishedsquarefeet','latitude', 'longitude', 'lotsizesquarefeet', 'yearbuilt', 'bed_bath_ratio', 'min_rooms'],
                scaler_in=MinMaxScaler(),
                return_scalers=False):
    '''
    Returns a dataframe of the scaled columns
    
    Args:
        df (DataFrame) : The dataframe with the columns to scale
        column_names (list) : The columns to scale
        scaler_in (sklearn.preprocessing) : scaler to use, default = MinMaxScaler()
        return_scalers (bool) : boolean to return a dictionary of the scalers used for 
            the columns, default = False
    Returns:
        df_scaled (DataFrame) : A dataframe containing the scaled columns
        scalers (dictionary) : a dictionary containing 'column' for the column name, 
            and 'scaler' for the scaler object used on that column
    '''
    #variables to hold the returns
    scalers = []
    df_scaled = df[column_names]
    for column_name in column_names:
        #determine the scaler
        scaler = scaler_in
        #fit the scaler
        scaler.fit(df[[column_name]])
        #transform the data
        scaled_col = scaler.transform(df[[column_name]])
        #store the column name and scaler
        scaler = {
            'column':column_name,
            'scaler':scaler
        }
        scalers.append(scaler)
        #store the transformed data
        df[f"{column_name}_scaled"] = scaled_col
    #determine the correct varibales to return
    if return_scalers:
        return df.drop(columns = column_names), scalers
    else:
        return df.drop(columns = column_names)

def make_X_and_y(df,
                target_column = 'taxvaluedollarcnt'):
    '''Makes a X and y sets based on the target column passed as a list'''
    #drop relevant columns
    X_train = df.drop(columns = ['taxvaluedollarcnt', 'parcelid'])
    #make y_Train
    y_train = df['taxvaluedollarcnt']
    return X_train, y_train

def add_custom_columns(df):
    '''creates the columns for a dataframe as defined in the explore section of final_report'''
    #make the bed/bath ratio
    df['bed_bath_ratio'] = df['bedroomcnt']/df['bathroomcnt']
    #make min_rooms
    df['min_rooms'] = df['bedroomcnt'] + df['bathroomcnt']
    #make luxury homes column
    seventy_percentile = df['taxvaluedollarcnt'].quantile(0.75)
    df['luxury_house'] = (df['taxvaluedollarcnt'] >= seventy_percentile)
    return df

def encode_columns(df,
                    column_names = ['county', 'luxury_house']):
    '''encodes columns as passed in column_names'''
    #make dummies
    dummy_df = pd.get_dummies(df[column_names], drop_first=True)
    #add to the existing dataframe
    df = pd.concat([df, dummy_df], axis=1).drop(columns = column_names)
    return df