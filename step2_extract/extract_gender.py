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
from parse_pdf import find_gender

#import the relevant python libraries
import pandas as pd
import json
import numpy as np
import random
import re
import time
from datetime import datetime
from pytz import timezone


#############################################################################
#         output file locations
#############################################################################


out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/gender/"
out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################################################################
#       Import names
#############################################################################

df_names = pd.read_excel(out_folder + "infos/bigsample_infos_PDFDocFinal.xlsx")
df_names = df_names[['doc_id', 'candidate_name_raw', 'candidate_name_clean']]

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
#  Loop over all documents and get genders
#############################################################################


# pdfs_to_parse = sample_ids
pdfs_to_parse = list(range(len(pdf_paths)))
t0 = time.time()
master_genders = []
for doc_id in pdfs_to_parse:  
    #check time
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    
    #findname
    name = df_names[df_names['doc_id']==doc_id].squeeze()
    if pd.notnull(name['candidate_name_clean']):
        name = name['candidate_name_raw'] + " " + name['candidate_name_clean']
    else:
        name = np.nan
        
    #grab the text
    pdf_path = pdf_paths[doc_id]
    cleanedPages = master_txtsCleaned[doc_id]
    cleanedPages = "\n".join(cleanedPages)
    
    #grab college
    doc_data = {'doc_id': doc_id, 'doc_path': pdf_path, 'name':name}
    gender, method, male, female, flag = find_gender(cleanedPages, name)
    doc_data["gender"] = gender
    doc_data["method"] = method
    doc_data["male_count"] = male
    doc_data["female_count"] = female
    doc_data["flag"] = flag
    #append to master dictionaries
    master_genders.append(doc_data)
    
t1 = time.time()
total_time = t1 - t0
print(total_time/ (60*60)) #time in hours not in second
del chi_time, t0, t1, total_time, pdf_path, doc_id
del cleanedPages, doc_data, gender, method, male, female, flag

#convert to df
master_genders = pd.DataFrame(master_genders)
master_genders['gender_found'] = master_genders['gender'].apply(lambda x: int((x!="nf") and (x!="tie")))
master_genders = master_genders.sort_values(['method', 'gender', 'flag', 'name'])

print("mean found ", master_genders['gender_found'].mean())
print("mean flag", master_genders['flag'].mean())
print("mean flag name", master_genders[master_genders['method']=="find_names"]['flag'].mean())
print("mean flag all", master_genders[master_genders['method']=="find_pronouns"]['flag'].mean())

print(master_genders['method'].value_counts())
print(master_genders['gender'].value_counts())

#save df
master_genders.to_excel(out_local + "bigsample_genders.xlsx", sheet_name= "values", index=False)


master_genders = pd.read_excel(out_local + "bigsample_genders.xlsx", sheet_name= "values", index=False)
gender_counts = master_genders[['doc_id','gender', 'method']].groupby(['method', 'gender'], as_index=False).count()
gender_counts.columns = ['method','gender', 'count']
gender_counts.to_excel(out_local + "GenderFinalCounts.xlsx", sheet_name= "values", index=False)




