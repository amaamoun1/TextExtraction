# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:07:36 2020

@author: Asser.Maamoun
"""
import pandas as pd

#read in all the colleges from the previous survey
colleges_unclean_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/from_pre2012Dataset/pre2012_colleges_unclean.xlsx"
colleges = pd.read_excel(colleges_unclean_path, sheet_name="Sheet1")

#grab all colleges
colleges_set = set()
for x in list(colleges['College Name']):
    #make lowercase, and strip of whitespace
    x = str(x).lower().strip()
    #skip empty entries
    if x=="." or pd.isnull(x): continue
    #fix univ to be university    
    if "univ." in x: x = x.replace("univ.", "university")
    #add to the set
    colleges_set.add(x)
del colleges_unclean_path, colleges, x

#save in a new excel
colleges_clean_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/from_pre2012Dataset/pre2012_colleges_clean.xlsx"
colleges_list = sorted(list(colleges_set))
colleges_df = pd.DataFrame(colleges_list, columns=['colleges'])
colleges_df.to_excel(colleges_clean_path, index=False)