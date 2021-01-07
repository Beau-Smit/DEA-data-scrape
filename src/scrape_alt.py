'''
Beau Smit
12/29/2020

This module will scrape the tables and text from the ARCOS retail drug report pdfs. It 
is only meant to gather the information from report 1 of each year. 
'''

import os
from tika import parser
from pickle import dump

YEAR = 2015 # 2015 2016 2017

root = r'C:/Users/bsmit/Projects/scrape_PDF'
# \\mathematica.Net\NDrive\Project\50723_OEWC\DC1\3 Future Research\COVID\Analysis\data\raw\ARCOS
in_path = os.path.join(root, 'input', f'{YEAR}')

pdf_path = os.path.join(in_path, f'report_yr_{YEAR}.pdf')

# read pdf with tika
raw = parser.from_file(pdf_path)
pdf_txt = raw['content']

# pickle for fast usage
with open(os.path.join(in_path, f'pdf_txt_{YEAR}.pkl'), 'wb') as f:
    dump(pdf_txt, f)
