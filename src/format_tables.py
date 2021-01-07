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
from utils import fill_blanks, fix_cols

YEAR = 2019 # 2018 2019 2020

report1_header = ['REGISTRANT ZIP CODE 3', '1ST QUARTER', '2ND QUARTER', '3RD QUARTER', '4TH QUARTER', 'TOTAL GRAMS']
root = r'C:/Users/bsmit/Projects/scrape_PDF'
# \\mathematica.Net\NDrive\Project\50723_OEWC\DC1\3 Future Research\COVID\Analysis\data\raw\ARCOS
in_path = os.path.join(root, 'input', f'{YEAR}')
out_path = os.path.join(root, 'output', f'{YEAR}')

with open(os.path.join(in_path, f'pdf_dict_{YEAR}.pkl'), 'rb') as f:
    pdf_dict = load(f)

drug_lst = [] # gather all drug names
combined_df = pd.DataFrame(columns=report1_header)

# first, combine all the tables 
for pg_num, info in pdf_dict.items():

    print(pg_num)
    pg_txt, tables = info

    for t in range(len(tables)):
        tables[t] = tables[t].dropna(axis=1)

        if len(tables[t].columns) < 6:
            # some of the columns got smashed together on the read in
            merged_col = tables[t].iloc[:, -1]
            sep_cols = pd.DataFrame(merged_col.str.split().tolist())
            tables[t] = pd.concat([tables[t].iloc[:, 0], sep_cols], axis=1)
        
        tables[t].columns = report1_header
    
    drugs = re.findall(r'DRUG:(.+)', pg_txt)
    assert len(drugs) <= 1
    if len(drugs) == 1:
        drug_number, drug_name = drugs[0].split(' - ')
        drug_number, drug_name = drug_number.strip(), drug_name.strip()
        drug_lst.append(drug_name)
    
    page_df = pd.concat(tables).reset_index(drop=True)
    combined_df = pd.concat([combined_df, page_df])

combined_df.reset_index(drop=True, inplace=True)

# now, I can separate by state because all the final
combined_df['REGISTRANT ZIP CODE 3'] = combined_df['REGISTRANT ZIP CODE 3'].astype(str)

# getting things like 1.21.1 - remove the 2nd period and anything after
combined_df['1ST QUARTER'] = fix_cols(combined_df['1ST QUARTER'])
combined_df['2ND QUARTER'] = fix_cols(combined_df['2ND QUARTER'])
combined_df['3RD QUARTER'] = fix_cols(combined_df['3RD QUARTER'])
combined_df['4TH QUARTER'] = fix_cols(combined_df['4TH QUARTER'])
combined_df['TOTAL GRAMS'] = fix_cols(combined_df['TOTAL GRAMS'])

final_row_expr = r'(?P<state_abbr>[A-Z]{2}) - (?P<state_name>.+) -'
if YEAR == 2020:
    final_row_expr = r'(?P<state_abbr>[A-Z]{2})'
    
    # make sure Q3 and Q4 have all 0 values
    combined_df['3RD QUARTER'] = 0.0
    combined_df['4TH QUARTER'] = 0.0

combined_df['flag_totals'] = combined_df['REGISTRANT ZIP CODE 3'].str.contains(final_row_expr).astype(int)

for idx, row in combined_df[::-1].iterrows():
    m = re.search(final_row_expr, row['REGISTRANT ZIP CODE 3'])
    if m:
        state = m.group('state_abbr')
        if state == 'WY': # new drug to record
            drug = drug_lst.pop()

    combined_df.loc[idx, 'state_abbr'] = state
    combined_df.loc[idx, 'drug_name'] = drug

combined_df = combined_df.applymap(lambda x: fill_blanks(x))

combined_df.to_excel(os.path.join(out_path, f'ALL_STATES_report1_{YEAR}.xlsx'), index=False)

for state in combined_df.state_abbr.unique():
    state_df = combined_df.loc[combined_df.state_abbr == state, :]
    state_df.to_excel(os.path.join(out_path, f'{state}_report1_{YEAR}.xlsx'), index=False)
