# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 21:55:01 2021

@author: Asser.Maamoun
"""
import pandas as pd
import re

vars_keep = ["i", "firstname", "lastname", "schools", "num_results", "is_namematch", "url"]
as_school = pd.read_csv("C:/Users/Asser.Maamoun/Documents/scraping_results_schoolasschool.csv")
as_school = as_school[vars_keep]
as_keyword = pd.read_csv("C:/Users/Asser.Maamoun/Documents/scraping_results_schoolaskeyword.csv")
as_keyword = as_keyword[vars_keep]

merged = as_school.merge(as_keyword, how='outer', suffixes=['_school', '_keyword'], on=["i", "firstname", "lastname", "schools"])

def same_value(row, column1, column2):
    return row[column1]==row[column2]

def get_profile(url):
    if pd.isnull(url):
        return 0
    return re.search("\\d+",url).group()

merged['profile_school'] = merged['url_school'].apply(get_profile)
merged['profile_keyword'] = merged['url_keyword'].apply(get_profile)

merged['same_numresults'] = merged.apply(lambda row: same_value(row, 'num_results_school', 'num_results_keyword'), axis=1)
merged['same_isnamematch'] = merged.apply(lambda row: same_value(row, 'is_namematch_school', 'is_namematch_keyword'), axis=1)
merged['same_profile'] = merged.apply(lambda row: same_value(row, 'profile_school', 'profile_keyword'), axis=1)

merged.to_csv("C:/Users/Asser.Maamoun/Documents/scraping_results_compared.csv", index=False)

