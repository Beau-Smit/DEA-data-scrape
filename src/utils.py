'''
Beau Smit
12/29/2020

This module contains utility functions to help the other modules.
'''

import pandas as pd
import re

report1_header = ['REGISTRANT ZIP CODE 3', '1ST QUARTER', '2ND QUARTER', '3RD QUARTER', '4TH QUARTER', 'TOTAL GRAMS']

def fill_blanks(x):
    if pd.isnull(x):
        return 0.0
    return x

def fix_cols(ser):
    # take out all the commas to convert into a float
    ser = ser.apply(lambda x: re.sub(',', '', str(x)))
    # remove any extra periods
    return ser.str.extract(r'^(\d+\.\d+)').astype('float')

def fix_header(df):
    row1_data = pd.DataFrame([df.columns]).dropna(axis=1)
    if row1_data.shape[1] > 6:
        # drop any columns that are 'Unnamed'
        col_list = [col for col in df.columns if not re.search('Unnamed', col)]
        df = df.loc[:, col_list]
        row1_data = pd.DataFrame([df.columns]).dropna(axis=1)
    row1_data.columns = report1_header
    df.columns = report1_header
    return pd.concat([row1_data, df]).reset_index(drop=True)

def fix_header_2020(df):
    df.dropna(axis=1, inplace=True)
    if len(df.columns) > 6:
        # drop any column whose name is not a number or a state abbreviation
        col_list = [col for col in df.columns if re.search(r'(\b[A-Z]{2}\b)|[0-9.]', col)]
        df = df.loc[:, col_list]
        return fix_header(df)
    elif len(df.columns) > 5:
        return fix_header(df)
    else:
        expanded = pd.DataFrame(df.iloc[:,1].str.split(' ').tolist())
        combined = pd.concat([df.iloc[:,0], expanded], axis=1)
        combined.columns = report1_header
        return combined

