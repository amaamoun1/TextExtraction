# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 11:10:30 2019

@author: amaamoun
"""
from bs4 import BeautifulSoup
import urllib
import pandas as pd



folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/scraped"
base_link = "https://www.4icu.org/"
countries = ["us", "ca", "top-universities-world"]

for c in countries:
    #navigate to page
    file = base_link + c + "/"
    html_file = urllib.request.urlopen(file)
    html_soup = BeautifulSoup(html_file)
    #scrape the table
    table = html_soup.find('table')
    all_rows = []
    col_names = []
    for row in table.find_all("tr"):
        header = [th.get_text() for th in row.find_all("th")]
        contents = [td.get_text() for td in row.find_all("td")]
        if len(header)>0 & len(all_rows)==0: #wait until we have seen a header
            col_names = header
        elif len(col_names)>0: #if we have seen a header start recording rows
            all_rows.append(contents)
        else: #skip any rows before the header 
            pass
    #convert to DataFrame and save as csv
    df = pd.DataFrame(all_rows, columns = col_names)
    df.to_csv(folder + "/" + c + ".csv", index=False)









