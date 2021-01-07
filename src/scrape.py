'''
Beau Smit
12/29/2020

This module will scrape the tables and text from the ARCOS retail drug report pdfs. It 
is only meant to gather the information from report 1 of 2018, 2019, and 2020. scrape_alt.py
extracts the information from the 2015 - 2017.
'''

import re
import os
from PyPDF2 import PdfFileReader
from tabula import read_pdf
from pickle import dump
from utils import fix_header, fix_header_2020

YEAR = 2019 # 2018 2019 2020

root = r'C:/Users/bsmit/Projects/scrape_PDF' # TODO: change to 
# \\mathematica.Net\NDrive\Project\50723_OEWC\DC1\3 Future Research\COVID\Analysis\data\raw\ARCOS
in_path = os.path.join(root, 'input', f'{YEAR}')

if YEAR == 2020:
    pdf_path = os.path.join(in_path, f'report_mid_yr_{YEAR}.pdf')
    header_func = fix_header_2020
else:
    pdf_path = os.path.join(in_path, f'report_yr_{YEAR}.pdf')
    header_func = fix_header

# read pdf with PyPDF2
file_obj = open(pdf_path, 'rb')
pdf = PdfFileReader(file_obj)

pdf_dict = {} # gather all pages in dictionary
report1_bool = True
pg_num = 1

# iterate through the pages of the pdf
while report1_bool:
    try:
        pg = pdf.getPage(pg_num)
        pg_txt = pg.extractText()
    except IndexError:
        # no more pages to read
        report1_bool = False
        continue

    print(pg_num)

    # only extracting from report 1
    report1_bool = re.search('ARCOS 3 - ?REPORT 0?1', pg_txt, flags=re.I)
    if (not report1_bool) and (YEAR != 2015): # 2015 has only report 1
        report1_bool = False
        continue

    # read pdf tables with tabula
    tables = read_pdf(pdf_path, pages=pg_num+1, encoding='latin1', stream=True)

    # headers should have "REGISTRANT ZIP CODE 3" as the first column name
    if not re.search(r'REGISTRANT', tables[0].columns[0]):
        tables[0] = header_func(tables[0])
    
    pdf_dict[pg_num] = [pg_txt, tables]
    pg_num += 1

file_obj.close()

# pickle for fast usage
with open(os.path.join(in_path, f'pdf_dict_{YEAR}.pkl'), 'wb') as f:
    dump(pdf_dict, f)
