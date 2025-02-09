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

import os
from docx import Document
from parse_document import parse_document
import pandas as pd
import re
import random
from datetime import datetime
from pytz import timezone

#change the working directory to be TextExtraction for loading dummy docs later
#%cd C:\Users\amaamoun\Desktop\Kaplan\TextExtraction
os.getcwd() #double-check

#############################################################################
#        Get a list of all the interview documents 
#############################################################################

#check the interview folder and the folder with doc converted to docx
interview_folder_path = "C:/Users/Asser.Maamoun/Documents/Interviews"
converted_folder_path = "C:/Users/Asser.Maamoun/Documents/ConvertedInterviews"
interview_docs = [os.path.join(interview_folder_path, f) for f in os.listdir(interview_folder_path) if os.path.isfile(os.path.join(interview_folder_path, f))]
converted_docs = [os.path.join(converted_folder_path, f) for f in os.listdir(converted_folder_path) if os.path.isfile(os.path.join(converted_folder_path, f))]
all_docs = interview_docs + converted_docs

#keep a seperate list for just the docx files
doc_paths = []
docx_paths = []
for doc_id in range(len(all_docs)):
    #first read in the given document
    name = all_docs[doc_id]
    if (".docx" not in name) and (".DOCX" not in name):
        doc_paths.append(name)
    else:
        docx_paths.append(name)
print("Total documents not in docx:", len(doc_paths))
print("Total documents in docx:", len(docx_paths))


#############################################################################
#         Loop over and pull information
#############################################################################


############## INPUTS ######################
#docx_to_parse = docx_paths[0:10]
#docx_to_parse = random.sample(docx_paths, 10)
docx_to_parse = docx_paths
#tables_to_parse = ["info", "competencies"]
tables_to_parse = ["info"]
############################################

#Initialize the master dataframes
master_tracker = pd.DataFrame()
master_data = pd.DataFrame()
master_unseen_keys = []

for doc_id in range(len(docx_to_parse)):
    if doc_id % 100 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    #find the document path and parse for the tables wanted
    path = docx_to_parse[doc_id]
    if path == '~$A_Dematic_CEO_SA initial template_Pandya, Kash_2012-11-19.docx':
        continue
    print("doc_id: ", doc_id, " path: ", path)
    doc_data, table_tracker, doc_unseen_keys = parse_document(doc_id, path, tables_to_parse)
    #append the useful data to our master versions
    master_tracker = master_tracker.append(table_tracker, sort=True)
    master_data = master_data.append(doc_data, sort=True)
    for unseen_key in doc_unseen_keys:
        if unseen_key not in master_unseen_keys:
            master_unseen_keys.append(unseen_key)
    
#if errored, use this to keep appending
errored_doc = doc_id
next_doc = errored_doc + 1
total_docs = len(docx_to_parse)
for doc_id in range(next_doc,total_docs):
    if doc_id % 100 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    #find the document path and parse for the tables wanted
    path = docx_to_parse[doc_id]
    if path == '~$A_Dematic_CEO_SA initial template_Pandya, Kash_2012-11-19.docx':
        continue
    print("doc_id: ", doc_id, " path: ", path)
    doc_data, table_tracker, doc_unseen_keys = parse_document(doc_id, path, tables_to_parse)
    #append the useful data to our master versions
    master_tracker = master_tracker.append(table_tracker, sort=True)
    master_data = master_data.append(doc_data, sort=True)
    for unseen_key in doc_unseen_keys:
        if unseen_key not in master_unseen_keys:
            master_unseen_keys.append(unseen_key)
            



#############################################################################
#    Find number of Docs with Candidate Name and compare with past data
#############################################################################

#get unique names
master_data['candidate name'].count() #I have 3619 names from 3869-3=3866 docs
names_uniq = pd.DataFrame({'name':master_data['candidate name'].unique()})
names_uniq['first'] = [x.split(0) for x in names_uniq['name']]

#look at unique name_date pairings
name_date_uniq = master_data[['candidate name', 'date']]
name_date_uniq = name_date_uniq.dropna()
name_date_uniq = name_date_uniq.drop_duplicates() #2813 unique name-date combinations

#download the pre-2012 data
past_file_loc = "C:/Users/Asser.Maamoun/OneDrive - G.H. Smart and Company Inc/Documents/names.xlsx"
past_names = pd.read_excel(past_file_loc)
past_names_uniq = past_names['name'].unique()
len(past_names) #3014...they are already unique

#compare the two sets of names
names_both = names_uniq.merge(past_names, how='inner', on='name')


has_info = master_tracker['parsed'] == 0
no_info= master_tracker[has_info]
no_info_ids = no_info['doc_id'].tolist()

no_info_paths = []
for doc_id in range(len(docx_paths)):
    if doc_id in no_info_ids:
        no_info_paths.append(docx_paths[doc_id])

    



