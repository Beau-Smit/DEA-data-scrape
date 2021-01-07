Data extraction programs written by Beau Smit. December 31, 2020 is my last day - please reach out to 
beau.h.smit@gmail.com for any questions about the programs. 

To extract 2018-2020 data, run:
> pipenv run python scrape.py
	1. make sure you have changed the YEAR variable.
	2. if you do not have pipenv, run 
		> pip install pipenv
		if still having trouble, reach out to colleagues, as many of them use pipenv

To extract 2015-2017 data, run: 
> pipenv run python scrape_alt.py
	it is a new program because the pdf structures are completely different

The extracted data are in the pkl files (serialized).
Now, the data has been extracted from the pdfs, but they need to be placed into dataframes with 
proper formats. 

To format 2018-2020 data, run:
> pipenv run python format_tables.py

To format 2015-2017 data, run:
> pipenv run python format_tables_alt.py

The folders should populate with excel files where each state is in its own file.
