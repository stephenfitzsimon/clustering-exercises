import pandas as pd
import numpy as np
from scipy import stats
from itertools import product

ALPHA = 0.05

def t_test_greater(df, column_cat = 'county', subcat_val = 'Orange', column_cont = 'logerror', alpha = ALPHA):
    category_x = df[df[column_cat] == subcat_val][column_cont]
    not_category_x = df[~(df[column_cat] == subcat_val)][column_cont].mean()
    t, p = stats.ttest_1samp(category_x, not_category_x)
    output = {
        'category_name':column_cat,
        'category_value':subcat_val,
        'p':p,
        'reject_null': p/2 < alpha
    }
    return pd.DataFrame([output])

def t_test_by_cat(df,
                columns_cat=['county'],
                columns_cont=['logerror'],
                alpha = ALPHA
                ):
    '''Performs a t-test for all subcategories of columns_cat and paored with every column in columns cat
    returns results as a dataframe'''
    outputs = []
    pairs_by_cat = {}
    #get pairs for every sub_Cat
    for category in columns_cat:
        #get subcategory names
        subcats = df[category].unique().tolist()
        #make the pairs
        pairs = list(product(subcats, columns_cont))
        pairs_by_cat[category] = pairs
    for category in columns_cat:
        pairs = pairs_by_cat[category]
        for pair in pairs:
            #subset into county_x and not county_x
            category_x = df[df[category] == pair[0]][pair[1]]
            not_category_x = df[~(df[category] == pair[0])][pair[1]].mean()
            #do the stats test
            t, p = stats.ttest_1samp(category_x, not_category_x)
            output = {
                'category_name':pair[0],
                'column_name':pair[1],
                'p':p,
                'reject_null': p < alpha
            }
            outputs.append(output)
    #return as a dataframe
    return pd.DataFrame(outputs)