# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 20:09:49 2020

@author: Asser.Maamoun
"""

#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")

from datetime import date
import pandas as pd
import numpy as np
import re


#############################################################################
#         File locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"



#############################################################################
#    Import Data
#############################################################################

master_clean = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name = "Values")

master_cleanCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="Counts")
master_compCounts = []
for i, row in master_cleanCounts.iterrows():
    if re.search("comp_merged_",row['variable']):
        master_compCounts.append(row)
master_compCounts = pd.DataFrame(master_compCounts)
del i, row

#############################################################################
#    Find number of Docs with competency sets
#############################################################################


def numAllCol(df, columns):
    temp = df.copy()
    temp = temp[columns]
    num_null = list(temp.apply(lambda x: x.isnull().sum(), axis='columns'))
    total_obs = num_null.count(0)
    return total_obs

#the following were taken from morten's keywords file
pastPulled = ['Hires A players', 'Develops people', 'Removes underperformers', 'Treats people with respect',
            'Efficiency of execution', 'Network of talented people', 'Flexible adaptable', 'Integrity honesty', 
            'Organization and planning', 'Calm under pressure', 'Commercial', 'Aggressive', 'Moves fast',
            'Follows through on commitments', 'Brainpower learns quickly', 'Analysis skills', 
            'Strategic thinking visioning', 
            'Creative innovative', 'Attention to detail', 'Enthusiasm motivate others', 'Persistent', 
            'Proactivity takes initiative', 'Work ethic',
            'Sets high standards' , 'Listening skills', 'Open to criticism and others ideas',
            'Written communications',
            'Oral communication', 'Teamwork', 'Persuasion', 'Holds people accountable', 'Sales' ,'Marketing',
            'Information technology', 'Finance', 'Human resources', 'Knows the industry']
pastPulled = ["comp_merged_" + x.lower().replace(" ","_") for x in pastPulled]
pastNotUsed = ['Commercial', 'Sales' ,'Marketing', 'Information technology', 'Finance', 'Human resources', 'Knows the industry', 'Written communications']
pastNotUsed = ["comp_merged_" + x.lower().replace(" ","_") for x in pastNotUsed]
pastUsed = [x for x in pastPulled if x not in pastNotUsed]

master_compCounts['pastPulled'] = [x in pastPulled for x in master_compCounts['variable']]
master_compCounts['pastUsed'] = [x in pastUsed for x in master_compCounts['variable']]


#The past competencies (37 pulled, 29 used) are not well represented in the current set
print(len(pastPulled), "comps in past pulled;", numAllCol(master_clean, pastPulled), "docs with all") #392
print(len(pastUsed), "comps in past used;", numAllCol(master_clean, pastUsed), "docs with all") #3740



#The competency counts trail off substantially after 5100 so lets check the numberof docs with these
compAbove5100 = list(master_compCounts[(master_compCounts['count']>6000)]['variable'])
print(len(compAbove5100), "comps above 5100;", numAllCol(master_clean, compAbove5100), "docs with all") #5,359

master_nodups = master_clean[master_clean['is_duplicate']==0].copy()
print(len(compAbove5100), "comps above 5100;", numAllCol(master_nodups, compAbove5100), "non dup docs with all") #4,552

print("comps in 5100:", [x for x in pastUsed if x in compAbove5100])
print("comps not in 5100:", [x for x in pastUsed if x not in compAbove5100])