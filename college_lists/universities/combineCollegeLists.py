# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:59:24 2020

@author: Asser.Maamoun
"""

import pandas as pd
import re

# Read in the lists
past_colleges_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/from_pre2012Dataset/pre2012_colleges_cleanEDITED.xlsx"
past_colleges = pd.read_excel(past_colleges_path, sheet_name="Sheet1")
past_colleges = list(past_colleges[past_colleges['to_drop']==0]["colleges"])

us_colleges_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/scraped/us.csv"
us_colleges = pd.read_csv(us_colleges_path)
us_colleges = list(us_colleges["University"])

ca_colleges_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/scraped/ca.csv"
ca_colleges = pd.read_csv(ca_colleges_path)
ca_colleges = list(ca_colleges["University"])

top_colleges_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/scraped/top-universities-world.csv"
top_colleges = pd.read_csv(top_colleges_path)
top_colleges = list(top_colleges["University"])
del past_colleges_path, us_colleges_path, ca_colleges_path, top_colleges_path

# Combine the lists
combined_colleges = list(set(past_colleges)|set(us_colleges)|set(top_colleges)|set(ca_colleges))
del past_colleges, us_colleges, top_colleges, ca_colleges

# Clean the entries
# dropped = []
clean_colleges = set()
for c in combined_colleges:
    c = c.strip().lower()
    c = re.sub("^the ", "", c)
    # #only save colleges and universities
    # if ("college" not in c) and ("university" not in c):
    #     dropped.append(c)
    #     continue
    clean_colleges.add(c)
    #also add teh common u.c. abbreviation
    if re.search("^university of california,", c):
        clean_colleges.add(c.replace("university of california,", "u.c."))
del c
clean_colleges = sorted(list(clean_colleges))

#save
clean_colleges_df = pd.DataFrame(clean_colleges, columns=['college_cleaned'])
clean_colleges_df.to_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/colleges_final.xlsx", index=False)
del clean_colleges, combined_colleges

#check for those college names that are contained in others
#the smaller one will get picked more frequently
all_matches = []
for c0 in list(clean_colleges_df['college_cleaned']):
    for c1 in list(clean_colleges_df['college_cleaned']):
        if (" " + c0 in c1) or (c0 + " " in c1):
            all_matches.append([c0, c1])
all_matches = pd.DataFrame(all_matches, columns=['small', 'big'])
del all_matches, c0, c1

