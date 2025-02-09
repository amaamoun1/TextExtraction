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
from parse_pdf import find_mba

#import the relevant python libraries
import json
import pandas as pd
import numpy as np
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

schools = pd.read_excel(college_folder + "business_school/business_schools_final.xlsx")
schools = [(row['school'], row['college'], row['needs_college']) for i, row in schools.iterrows()]


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

pdfs_to_parse = list(range(len(pdf_paths)))
t0 = time.time()
master_mba = []
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
    mba_found = find_mba(cleanedPages, schools)
    doc_data["mba_raw"] = mba_found
    
    #append to master dictionaries
    master_mba.append(doc_data)
t1 = time.time()
total_time = t1 - t0
print(total_time/ (60*60)) #time in hours not in second
del chi_time, t0, t1, total_time, pdf_path, doc_id
del cleanedPages, doc_data, mba_found

#convert to df
master_mba = pd.DataFrame(master_mba)
master_mba['mba_found'] = master_mba['mba_raw'].apply(lambda x: int(pd.notnull(x)))
master_mba['mba_multiple'] = master_mba['mba_raw'].apply(lambda x: int(" AND " in str(x)))
print("found:", master_mba['mba_found'].sum())
print("mean", master_mba['mba_found'].mean())
print("num multiples", master_mba['mba_multiple'].sum())

#save df
master_mba.to_excel(out_local + "bigsample_mba.xlsx", sheet_name= "values", index=False)




#clean the mba_raw column to only include the university names
master_mba = pd.read_excel(out_local + "bigsample_mba.xlsx", sheet_name= "values")

schools = pd.read_excel(college_folder + "business_school/business_schools_final.xlsx")
school_uni_dict =  {}
for i, row in schools.iterrows():
    school_uni_dict[row['school'].replace(".", "\\.?")] = row['college']
school_uni_dict["anderson school of management"] = "university of california, los angeles"

def clean_mba(c):
    if pd.isnull(c):
        return c
    else:
        # c = re.sub("\\.","", c)
        c = c.replace(" MBA","").replace(" YEARS","")
        # c = re.sub("[^a-zA-Z\\s]", " ", c)
        c = " ".join(c.split())
        if "UNI" in c:
            return re.sub(".*UNI ","", c)
        else:
            return school_uni_dict[re.sub("SCHOOL ","", c)]
    
def pick_mba(mbas):
    if pd.isnull(mbas):
        return np.nan
    elif " AND " not in mbas:
        return clean_mba(mbas)
    else:
        selected = [clean_mba(x) for x in mbas.split(" AND ")]
        new_selected = []
        #I checked docs with mutliplt mba found and they ALL were true MBAs
        #so no need to narrow results if more than 1 appeared
        for mba in selected:
            is_contained = 0
            for other in selected:
                if mba in other and mba!=other:
                    is_contained = 1
            if is_contained==0:
                if mba not in new_selected:
                    new_selected.append(mba)
        selected = new_selected
        return " AND ".join(selected)
    

master_mba['mba_clean'] = master_mba['mba_raw'].apply(pick_mba)
master_mba.to_excel(out_local + "bigsample_mba.xlsx", sheet_name= "values", index=False)

#############################################################################
#  Add the top14 dummy
#############################################################################

master_mba = pd.read_excel(out_local + "bigsample_mba.xlsx", sheet_name= "values")
top14 = pd.read_excel(college_folder + "business_school/business_schools_final.xlsx")
top14 = list(set(top14[top14['mba_top14']==1]['college']))

new_rows = []
for i, row in master_mba.iterrows():
    row["mba_top14"] = 0
    doc_mbas = row['mba_clean']
    if pd.notnull(doc_mbas):
        doc_mbas = doc_mbas.split(" AND ")
        for c in doc_mbas:
            if c in top14:
                row['mba_top14'] = 1
                break
    new_rows.append(row)
master_mba_top14 = pd.DataFrame(new_rows)
print(sum(master_mba_top14['mba_top14']))

master_mba_top14.to_excel(out_local + "bigsample_mba_top14.xlsx", sheet_name= "values", index=False)
del i, row, doc_mbas, c, top14, new_rows
#############################################################################
#  Get Counts by MBA program
#############################################################################


master_mba = pd.read_excel(out_local + "bigsample_mba.xlsx", sheet_name= "values")

schools = pd.read_excel(college_folder + "business_school/business_schools_final.xlsx")
schools = list(set(schools['college']))

mba_counts = []
for school in schools:
    count = 0
    for found in master_mba["mba_clean"]:
        if pd.isnull(found):
            continue
        else:
            found = found.split(" AND ")
            if school in found:
                count += 1
    mba_counts.append({"mba": school, "count":count})
mba_counts = pd.DataFrame(mba_counts)
print("Total Count:", sum(mba_counts['count']))
# colleges_counts = colleges_counts[colleges_counts['count'] > 0]
top14 = pd.read_excel(college_folder + "business_school/business_schools_final.xlsx")
top14 = top14[['college', 'mba_top14']]
top14.columns = ['mba', 'mba_top14']
top14 = top14.drop_duplicates()
mba_counts = mba_counts.merge(top14, how='left')
mba_counts = mba_counts.sort_values(["mba_top14", "count"], ascending=False)
mba_counts.to_excel(out_local + "MBAFinalCounts_withTop14.xlsx", index=False)




