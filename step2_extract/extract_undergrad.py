# -*- coding: utf-8 -*-
"""
This script reads in many word documents.
It then creates a dictionary with subdictionaries for each table that is listed
in the tables_to_parse list. It also creates a dataframe with a row per
document and with entries corresponding to the identified variables in all of
the tables

To do:
    - Output the dataframe to an excel file. Preferably similar in structure
        to the excel file already created.

Notes:
    - info on the docx package: https://python-docx.readthedocs.io/en/latest/index.html
    - info on the pandas package: https://pandas.pydata.org/
"""

#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
os.getcwd() #double-check


#add the relevant folders of code to the system path...so that python can access all the codes
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_txt')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')

#import the codes that are needed
from parse_pdf import find_college_ba

#import the relevant python libraries
import pandas as pd
import numpy as np
import json
import random
import re
import time
from datetime import datetime
from pytz import timezone


#############################################################################
#         output file locations
#############################################################################

out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/colleges/"
college_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/"


#############################################################################
#       Import Keywords
#############################################################################

colleges_path = college_folder + "universities/colleges_final.xlsx"
colleges = pd.read_excel(colleges_path)
colleges = list(colleges['college_cleaned'])
colleges = [c.replace("|", "\\|") for c in colleges]
del colleges_path

colleges_filtered = []
to_drop = ['business', 'management', 'wharton', 'graduate', 'medical', 'law', 'nursing']
for c in colleges:
    bad = 0
    for t in to_drop:
        if re.search(t, c):
           bad = 1
    if bad==0:
        colleges_filtered.append(c)

colleges = pd.DataFrame(colleges_filtered, columns=['college'])
mbas = pd.read_excel(college_folder + "business_school/business_schools_final.xlsx")
colleges = colleges.merge(mbas[['school', 'college']], how='left')
colleges = [(row['college'], row['school']) for i, row in colleges.iterrows()]


ivies = pd.read_excel(college_folder + "universities/colleges_ivies.xlsx")
ivies.columns = ['undergrad', 'undergrad_ivy']

#############################
#  Get a list of all the PDFs
#############################

mapping_df = pd.read_excel(out_folder + "docid_mapping.xlsx", index=False)
mapping_df = mapping_df.sort_values('doc_id')
txt_paths = list(mapping_df['txt_path'])
pdf_paths = list(mapping_df['pdf_path'])


##############################
#  Get Documents and Sample
#############################

with open("C:/Users/Asser.Maamoun/Documents/master_txtsCleanedDefault.json") as data_file:
    master_txtsCleaned = json.load(data_file)
del data_file

random.seed(1234)
sample_ids = sorted(random.sample(range(len(txt_paths)), 20))
sample_pdfs = []
for pdf in sample_ids:
    sample_pdfs.append(master_txtsCleaned[pdf])
del pdf

#############################################################################
#  Loop over all documents and get colleges
#############################################################################




# pdfs_to_parse = sample_ids
pdfs_to_parse = list(range(len(pdf_paths)))
# pdfs_to_parse = sample_ids
t0 = time.time()
master_colleges = []
for doc_id in pdfs_to_parse:  
    #check time
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    
    #grab the text
    pdf_path = pdf_paths[doc_id]
    cleanedPages = master_txtsCleaned[doc_id]
    cleanedPages = "\n".join(cleanedPages)
    
    #grab college
    doc_data = {'doc_id': doc_id, 'doc_path': pdf_path}
    colleges_found = find_college_ba(cleanedPages, colleges)
    doc_data["undergrad_raw"] = colleges_found
    
    #append to master dictionaries
    master_colleges.append(doc_data)
t1 = time.time()
total_time = t1 - t0
print(total_time/ (60*60)) #time in hours not in second
del chi_time, t0, t1, total_time, pdf_path, doc_id
del cleanedPages, doc_data, colleges_found

#convert to df
master_colleges = pd.DataFrame(master_colleges)
master_colleges['undergrad_found'] = master_colleges['undergrad_raw'].apply(lambda x: int(pd.notnull(x)))
print("mean", master_colleges['undergrad_found'].mean())

#save df
master_colleges.to_excel(out_local + "bigsample_undergrad.xlsx", sheet_name= "values", index=False)

#if multiple colleges found, pick those that are most likely to be the true undergrad
master_colleges = pd.read_excel(out_local + "bigsample_undergrad.xlsx", sheet_name= "values")

def clean_undergrad(c):
    if pd.isnull(c):
        return c
    else:
        c = re.sub("\\.","", c)
        c = re.sub("[^a-zA-Z\\s]", " ", c)
        c = " ".join(c.split())
        return c.replace(" BA","").replace(" YEARS", "")
    
def pick_undergrad(colleges):
    if pd.isnull(colleges):
        return np.nan
    elif " AND " not in colleges:
        return clean_undergrad(colleges)
    else:
        selected = colleges.split(" AND ")
        new_selected = []
        score = 0
        for to_select in [" BA", " YEARS"]:
            if to_select in " AND ".join(selected):
                score += 1
                for college in selected:
                    if to_select in college:
                        new_selected.append(clean_undergrad(college))
                selected = new_selected
                new_selected = []
        if score == 0:
            return np.nan
        new_selected = []
        for college in selected:
            is_contained = 0
            for other in selected:
                if college in other and college!=other:
                    is_contained = 1
            if is_contained==0:
                if college not in new_selected:
                    new_selected.append(college)
        selected = new_selected
        return " AND ".join(selected)


master_colleges['undergrad_clean'] = master_colleges['undergrad_raw'].apply(pick_undergrad)
master_colleges['undergrad_multiple'] = master_colleges['undergrad_clean'].apply(lambda x: int(" AND " in str(x)))
master_colleges.to_excel(out_local + "bigsample_undergrad.xlsx", sheet_name= "values", index=False)


#############################################################################
#  Get Counts by College
#############################################################################

master_colleges = pd.read_excel(out_local + "bigsample_undergrad.xlsx", sheet_name= "values")

colleges_counts = []
for c in colleges_filtered:
    c_clean = clean_undergrad(c)
    count = 0
    for found in master_colleges["undergrad_clean"]:
        if pd.isnull(found):
            continue
        else:
            found = found.split(" AND ")
            if c_clean in found:
                count += 1
    colleges_counts.append({"undergrad": c, "count":count})
colleges_counts = pd.DataFrame(colleges_counts)
print(sum(colleges_counts['count']))


colleges_counts = colleges_counts.merge(ivies, how='left')
colleges_counts = colleges_counts.sort_values(['undergrad_ivy', 'count'], ascending=False)
colleges_counts.to_excel(out_local + "UndergradFinalCounts_withIvies.xlsx", index=False)


#############################################################################
#  Add the ivy dummy
#############################################################################

master_colleges = pd.read_excel(out_local + "bigsample_undergrad.xlsx", sheet_name= "values")

ivies = [clean_undergrad(x) for x in list(ivies[ivies['undergrad_ivy']==1]['college'])]

new_rows = []
for i, row in master_colleges.iterrows():
    row["undergrad_ivy"] = 0
    doc_colleges = row['undergrad_clean']
    if pd.notnull(doc_colleges):
        doc_colleges = doc_colleges.split(" AND ")
        for c in doc_colleges:
            if c in ivies:
                row['undergrad_ivy'] = 1
                break
    new_rows.append(row)
master_colleges_ivies = pd.DataFrame(new_rows)
print(sum(master_colleges_ivies['undergrad_ivy']))

master_colleges_ivies.to_excel(out_local + "bigsample_undergrad_ivies.xlsx", sheet_name= "values", index=False)
del i, row, doc_colleges, c, ivies, new_rows





