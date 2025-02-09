# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 11:10:30 2019

@author: amaamoun
"""
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import re


folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/business_school"
web_page = "https://en.wikipedia.org/wiki/List_of_business_schools_in_the_United_States"


html_file = urllib.request.urlopen(web_page)
html_soup = BeautifulSoup(html_file)
#scrape the table
table = html_soup.find('table')
all_rows = []
col_names = []
state_count = 0
for row in table.find_all("tr"):
    header = [re.sub("\n", "", th.get_text()).lower() for th in row.find_all("th")]
    contents = [re.sub("\n","", re.sub("\\[.*\\]", "", td.get_text())).lower() for td in row.find_all("td")]
    
    if len(header)>0 & len(all_rows)==0: #wait until we have seen a header
        col_names = header
    elif len(col_names)>0: #if we have seen a header start recording rows
        if state_count == 0:
            first_cell = row.find("td")
            if first_cell:
                if 'rowspan' in first_cell.attrs:
                    state_count = int(first_cell['rowspan']) - 1
                    state = [contents[0]]
                else:
                    if len(contents)==5:
                        contents = state+contents
                    else:
                        state_count = 0
                        state = contents[0]
                all_rows.append(contents)
                continue
            else:
                raise ValueError
        all_rows.append(state + contents[:4])
        state_count -= 1
        print(state, state_count)
    else: #skip any rows before the header 
        pass
#convert to DataFrame and save as csv
df = pd.DataFrame(all_rows, columns = col_names)
df.to_excel(folder + "/business_schools.xlsx", index=False)


school_count = {}
for x in list(df['school']):
    if x in school_count:
        school_count[x] += 1
    else:
        school_count[x] = 1








