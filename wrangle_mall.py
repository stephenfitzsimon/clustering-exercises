import os

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from env import get_db_url

def mall_data():
    df = acquire_mall()
    df = encode_columns(df, ['gender'])
    df = handle_missing(df)
    df = mall_scale(df, ['age', 'annual_income', 'spending_score'])
    return df

def acquire_mall(query_db=False):
    #file name string literal
    #check if file exists and query_dg flag
    FILENAME = 'mall_data.csv'
    if os.path.isfile(FILENAME) and not query_db:
        #return dataframe from file
        print('Returning saved csv file.')
        return pd.read_csv(FILENAME).drop(columns = ['Unnamed: 0'])
    else:
        #query database 
        print('Querying database ... ')
        query = '''
        SELECT * FROM customers;
        '''
        #get dataframe from a 
        df = pd.read_sql(query, get_db_url('mall_customers'))
        print('Got data from the SQL database')
        #save the dataframe as a csv
        df.to_csv(FILENAME)
        print('Saved dataframe as a .csv!')
        #return the dataframe
        return df

def summarize_mall(df):
    print(df.describe())
    for col in df.select_dtypes(exclude='object').columns.tolist():
        df[col].hist()
        plt.title(col)
        plt.show()
    for col in df.select_dtypes(exclude='object').columns.tolist():
        df.boxplot(column=[col])
        plt.title(col)
        plt.show()
    for col in df.select_dtypes(include='object').columns.tolist():
        print(df[col].value_counts())

def get_outliers(col_name, multiplier = 1.5):
    '''
    Returns a tuple of the form (lower_IQR, upper_IQR) based on passed col_name
    '''
    stats = df[[col_name]].describe().T
    iqr = float(stats['75%']) - float(stats['25%'])
    upper_range = float(stats['75%']) + iqr*multiplier
    lower_range = float(stats['25%']) - iqr*multiplier
    return (lower_range, upper_range)

def split_data(df):
    '''splits the zillow dataframe into train, test and validate subsets
    
    Args:
        df (DataFrame) : dataframe to split
    Return:
        train, test, validate (DataFrame) :  dataframes split from the original dataframe
    '''
    RAND_SEED = 123
    #make train and test
    train, test = train_test_split(df, train_size = 0.8, random_state=RAND_SEED)
    #make validate
    train, validate = train_test_split(train, train_size = 0.7, random_state=RAND_SEED)
    return train, validate, test

def encode_columns(df,
                    column_names):
    '''encodes columns as passed in column_names'''
    #make dummies
    dummy_df = pd.get_dummies(df[column_names], drop_first=True)
    #add to the existing dataframe
    df = pd.concat([df, dummy_df], axis=1).drop(columns = column_names)
    return df

def handle_missing(df):
    return df.dropna()

def mall_scale(df,
                column_names,
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