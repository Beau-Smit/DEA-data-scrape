'''
Beau Smit
12/29/2020

This module formats the information extracted from the ARCOS report 1. Specifically, the information
begins as a dictionary where page numbers are keys and the information they hold are the values.
'''

import os
import re
import pandas as pd
from pickle import load
from utils import fill_blanks

YEAR = 2015 # 2015 2016 2017

report1_header = ['REGISTRANT ZIP CODE 3', '1ST QUARTER', '2ND QUARTER', '3RD QUARTER', '4TH QUARTER', 'TOTAL GRAMS']
root = r'C:/Users/bsmit/Projects/scrape_PDF'
# \\mathematica.Net\NDrive\Project\50723_OEWC\DC1\3 Future Research\COVID\Analysis\data\raw\ARCOS
in_path = os.path.join(root, 'input', f'{YEAR}')
out_path = os.path.join(root, 'output', f'{YEAR}')

with open(os.path.join(in_path, f'pdf_txt_{YEAR}.pkl'), 'rb') as f:
    pdf_txt = load(f)

drug_lst = [] # gather all drug names
combined_df = pd.DataFrame(columns=report1_header)

report_1 = re.split(r'REPORT 2', pdf_txt)[0]

for d in report_1.split(r'DRUG CODE:'):
    match = re.search(r'DRUG NAME:\s?(?P<drug>[A-Z ]+)', d)
    if match:
        drug_lst.append(match.group('drug'))

report_1_rows = [row for row in report_1.split('\n') if row != '']
all_rows = []

drug_num = 0
for row in report_1_rows:

    if re.search('STATE:|DRUG CODE:', row):
        if re.search('DRUG CODE:', row):
            drug_match = re.search(r'DRUG CODE: ?(?P<code>.+)DRUG NAME: ?(?P<drug>.+)', row)
            code = drug_match.group('code')
            drug = drug_match.group('drug')
            drug_num += 1
        if re.search('STATE:', row):
            state_match = re.search(r'STATE: ?(?P<state>.+)', row)
            state = state_match.group('state')

    else:
        # skip all rows until the first drug table
        if drug_num == 0:
            continue
        
        if not re.search(r'ZIP|DATE|Run|REPORTING', row):
            row_vals = row.split()
            row_vals.append(drug)
            row_vals.append(state)
            all_rows.append(row_vals)

combined_df = pd.DataFrame(all_rows, columns=report1_header + ['drug_name', 'state'])
# sometimes there's an error with the data, so here, I print out the rows that were cut
# from the combined_df. You should check to see if these rows need to be added to the output.
print(combined_df.loc[pd.isnull(combined_df.state)])
combined_df = combined_df.loc[pd.notnull(combined_df.state)] # remove empty rows

# import pdb; pdb.set_trace()
# print(combined_df.loc[combined_df['REGISTRANT ZIP CODE 3'] != 'REPORTING'])

def fix_cols_alt(ser):
    # take out all the commas to convert into a float
    ser = ser.apply(lambda x: re.sub(',', '', str(x)))
    # remove any extra periods
    return ser.astype('float')

combined_df['1ST QUARTER'] = fix_cols_alt(combined_df['1ST QUARTER'])
combined_df['2ND QUARTER'] = fix_cols_alt(combined_df['2ND QUARTER'])
combined_df['3RD QUARTER'] = fix_cols_alt(combined_df['3RD QUARTER'])
combined_df['4TH QUARTER'] = fix_cols_alt(combined_df['4TH QUARTER'])
combined_df['TOTAL GRAMS'] = fix_cols_alt(combined_df['TOTAL GRAMS'])

combined_df['flag_totals'] = combined_df['REGISTRANT ZIP CODE 3'].str.contains('TOTAL').astype(int)

combined_df = combined_df.applymap(lambda x: fill_blanks(x))

combined_df.to_excel(os.path.join(out_path, f'ALL_STATES_report1_{YEAR}.xlsx'), index=False)

for state_name in combined_df.state.unique():
    state_df = combined_df.loc[combined_df.state == state_name, :]

    state_name = re.sub(' ', '_', str(state_name))
    state_df.to_excel(os.path.join(out_path, f'{state_name}_report1_{YEAR}.xlsx'), index=False)
