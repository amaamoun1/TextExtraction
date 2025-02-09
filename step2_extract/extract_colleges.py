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
from parse_pdf import find_college
from parse_pdf import find_college_potentials

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


out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/colleges/"
out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
college_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/"


#############################################################################
#       Import colleges
#############################################################################

colleges_path = college_folder + "universities/colleges_final.xlsx"
colleges = pd.read_excel(colleges_path)
colleges = list(colleges['college_cleaned'])
colleges = [c.replace("|", "\\|") for c in colleges]
del colleges_path


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
    colleges_found = find_college(cleanedPages, colleges)
    if pd.isnull(colleges_found):
        potentials = find_college_potentials(cleanedPages, colleges)
        doc_data["college_potential"] = potentials
    doc_data["college_raw"] = colleges_found
    
    #append to master dictionaries
    master_colleges.append(doc_data)
t1 = time.time()
total_time = t1 - t0
print(total_time/ (60*60)) #time in hours not in second
del chi_time, t0, t1, total_time, pdf_path, doc_id
del cleanedPages, doc_data, colleges_found, potentials

#convert to df
master_colleges = pd.DataFrame(master_colleges)
master_colleges['college_potential'] = master_colleges['college_potential'].apply(lambda x: re.sub("\s+", " ", str(x).replace("NEW PAGE","")))
master_colleges['college_found'] = master_colleges['college_raw'].apply(lambda x: int(pd.notnull(x)))
print("mean", master_colleges['college_found'].mean())

#save df
master_colleges.to_excel(out_local + "bigsample_colleges.xlsx", sheet_name= "values", index=False)


#############################################################################
#  Get Counts by College
#############################################################################


master_colleges = pd.read_excel(out_local + "bigsample_colleges.xlsx", sheet_name= "values")
colleges_counts = []
for c in colleges:
    count = 0
    for found in master_colleges["college"]:
        if pd.isnull(found):
            continue
        else:
            found = found.split(" AND ")
            if c in found:
                count += 1
    colleges_counts.append({"college": c, "count":count})
colleges_counts = pd.DataFrame(colleges_counts)
colleges_counts.to_excel(out_local + "CollegesFinalCounts.xlsx", index=False)





