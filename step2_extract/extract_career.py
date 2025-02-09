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
from parse_page import extract_career
from parse_pdf import identifyCareerPages

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
out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/career/"


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

with open("C:/Users/Asser.Maamoun/Documents/master_txtsCleanedScorecard.json") as data_file:
    master_txtsCleaned = json.load(data_file)
del data_file

random.seed(1234)
sample_ids = sorted(random.sample(range(len(txt_paths)), 20))
sample_pdfs = []
sample_paths = []
for pdf in sample_ids:
    sample_pdfs.append(master_txtsCleaned[pdf])
    sample_paths.append(pdf_paths[pdf])
del pdf

sample_df = pd.DataFrame(zip(sample_ids, sample_paths), columns=['sample_id', 'sample_path'])
sample_df.to_excel(out_local + "sample.xlsx", sheet_name= "values", index=False)
sample_df = pd.read_excel(out_local + "sample_evaluated.xlsx")

#############################################################################
#  Loop over all documents and get careers
#############################################################################


# pdfs_to_parse = sample_ids
pdfs_to_parse = list(range(len(pdf_paths)))
# pdfs_to_parse = list(range(500))


#Initialize the master dataframes
master_Pages = []
master_Text = []

chi_time = datetime.now(timezone('America/Chicago'))
print("starting at", chi_time.strftime('%H:%M:%S'))
for doc_id in pdfs_to_parse:
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    #grab the path and the cleaned text
    pdf_path = pdf_paths[doc_id]
    cleanedPages = master_txtsCleaned[doc_id]
    
    #identify the pages and grab the scorecard ones
    pagesIdentified = identifyCareerPages(cleanedPages)
    if 'career' in pagesIdentified:
        Pages = pagesIdentified['career']
    else:
        Pages = []
    master_Pages.append(Pages)
    
    #combined the scorecard pages
    Text = ""
    for page_id in Pages:
        Text += cleanedPages[page_id] + "\n NEW PAGE \n\n"
    Text = re.sub("\n NEW PAGE \n\n$", "", Text)
    master_Text.append(Text)
del pdf_path, cleanedPages, pagesIdentified, Pages, Text, doc_id, page_id
chi_time = datetime.now(timezone('America/Chicago'))
print("ending at", chi_time.strftime('%H:%M:%S'))

# sample_pages = pd.DataFrame(zip(sample_ids, master_Pages), columns=['sample_id', 'pages'])
# sample_check = sample_df.merge(sample_pages, how="left")
# sample_check.to_excel(out_local + "sample_check.xlsx" , index=False)

t0 = time.time()
master_career = []
for idx in range(len(pdfs_to_parse)):
    if idx % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(idx, "parsing at", chi_time.strftime('%H:%M:%S'))
    
    #grab the path and the pages
    doc_id = pdfs_to_parse[idx]
    pdf_path = pdf_paths[pdfs_to_parse[idx]]
    Text = master_Text[idx]
    
    #grab career
    doc_data = {'doc_id': doc_id, 'doc_path': pdf_path, 'found_career_section': int(Text!="")}
    doc_data["career_raw"] = extract_career(Text)
    
    #append to master dictionaries
    master_career.append(doc_data)
    
t1 = time.time()
total_time = t1 - t0
print(total_time/ (60*60)) #time in hours not in second
del chi_time, t0, t1, total_time, pdf_path, doc_id, doc_data

#convert to df
master_career = pd.DataFrame(master_career)
master_career['career_found'] = master_career['career_raw'].apply(lambda x: int(x!=""))
print("mean", master_career['career_found'].mean())

#save df
master_career.to_excel(out_local + "career.xlsx", sheet_name= "values", index=False)



#############################################################################
#  Clean results
#############################################################################

bad_starts = ["(reasons for )?leaving", "gpa", "internship", "summer jobs", 
              "gmat",  "\\(?self-reported", "junior year", "senior year",
              "next steps", "sat/act", "weaker areas", "comments"]

def clean_career(career):
    if pd.isnull(career):
        return ""
    jobs = career.split(" AND \n")
    clean_jobs = []
    for j in jobs:
        if pd.isnull(j) or j=="" or j==" ":
            continue
        clean_j = re.sub("\\s*NEW PAGE\\s*", "", j)
        # for b in bad_starts:
        #     clean_j = re.sub("^.*?\\|{2}\\s*" + b + ".*?\\|{2}", "||", clean_j)
        if re.search("\\|{2}\\s*years.*$", clean_j):
            clean_j = re.search("\\|{2}\\s*years.*$", clean_j).group(0)
        if re.search("\\|{2}\\s*\\d{4}.*$", clean_j):
            clean_j = re.search("\\|{2}\\s*\\d{4}.*$", clean_j).group(0)
        if re.search("\\|{2}\\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec)\\b.*$", clean_j):
            clean_j = re.search("\\|{2}\\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec)\\b.*$", clean_j).group(0)
        if re.search("\\|{2}\\s*(?:january|february|march|april|may|june|july|august|september|october|november|december)\\b.*$", clean_j):
            clean_j = re.search("\\|{2}\\s*(?:january|february|march|april|may|june|july|august|september|october|november|december)\\b.*$", clean_j).group(0)

        clean_j = re.sub("\\|{2}\\s*\\|{2}", "||", clean_j)
        clean_j = re.sub("\\|{3,}", "||", clean_j)
        while re.search("^\\|{2}\\s{4,}.*?\\|{2}", clean_j):
            clean_j = re.sub("^\\|{2}\\s{4,}.*?\\|{2}", "||", clean_j)
        clean_jobs.append(clean_j)
    if len(clean_jobs)==0:
        return ""
    return " AND \n".join(clean_jobs)

    

master_career = pd.read_excel(out_local + "career.xlsx")
master_career['career_clean'] = master_career['career_raw'].apply(clean_career)

print("mean", master_career['career_found'].mean())
master_career['career_found'] = master_career['career_clean'].apply(lambda x: int(x!=""))
print("mean", master_career['career_found'].mean())

master_career.to_excel(out_local + "career_clean.xlsx", sheet_name= "values", index=False)








