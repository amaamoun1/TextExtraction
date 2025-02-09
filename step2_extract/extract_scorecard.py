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
from parse_pdf import identifyAllPages
from clean_page import cleanPageScorecard
from parse_scorecardText import parse_scorecardText

#import the relevant python libraries
import json
import numpy as np
import pandas as pd
import random
import re
from datetime import datetime
from pytz import timezone


#############################################################################
#         output file locations
#############################################################################

out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scorecard/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################################################################
#       Import Keywords
#############################################################################

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


# master_outcomes = pd.read_excel(out_local + "scorecard_raw.xlsx", sheet_name="values")
# no_outcomes = list(master_outcomes[pd.isnull(master_outcomes['1_desc'])]['doc_id'])
# check_ids = sorted(random.sample(no_outcomes, 20))
# check_pdfs = []
# for pdf in check_ids:
#     check_pdfs.append(master_txtsCleaned[pdf])    
# del pdf


#############################################################################
#  Loop over all documents and get scorecard
#############################################################################


#select which pdfs we want to parse
pdfs_to_parse = list(range(len(pdf_paths)))

############################################
#  Loop over and extract from documents
############################################

#Initialize the master dataframes
master_scorecardPages = []
master_scorecardText = []

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
    pagesIdentified = identifyAllPages(cleanedPages)
    if 'scorecard' in pagesIdentified:
        scorecardPages = pagesIdentified['scorecard']
    else:
        scorecardPages = []
    master_scorecardPages.append(scorecardPages)
    
    #combined the scorecard pages
    scorecardText = ""
    for page_id in scorecardPages:
        scorecardText += cleanedPages[page_id] + "\n NEW PAGE \n\n"
    scorecardText = re.sub("\n NEW PAGE$", "", scorecardText)
    master_scorecardText.append(scorecardText)
del pdf_path, cleanedPages, pagesIdentified, scorecardPages, scorecardText
chi_time = datetime.now(timezone('America/Chicago'))
print("ending at", chi_time.strftime('%H:%M:%S'))



master_scorecard_dict = []
chi_time = datetime.now(timezone('America/Chicago'))
print("starting at", chi_time.strftime('%H:%M:%S'))
for idx in range(len(pdfs_to_parse)):
    if idx % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(idx, "parsing at", chi_time.strftime('%H:%M:%S'))
    #grab the path and the scorecard pages
    pdf_path = pdf_paths[pdfs_to_parse[idx]]
    scorecard_text = master_scorecardText[idx]
    scorecard_dict = parse_scorecardText(scorecard_text)
    scorecard_dict["doc_id"] = idx
    scorecard_dict["scorecard_present"] = int(scorecard_text!="")
    master_scorecard_dict.append(scorecard_dict)

chi_time = datetime.now(timezone('America/Chicago'))
print("ending at", chi_time.strftime('%H:%M:%S'))

master_scorecard_df = pd.DataFrame(master_scorecard_dict)
cols = list(master_scorecard_df)
cols.insert(0, cols.pop(cols.index('doc_id')))
cols.insert(1, cols.pop(cols.index('scorecard_present')))
master_scorecard_df = master_scorecard_df.reindex(columns= cols)


checking1 = list(master_scorecard_df[pd.notnull(master_scorecard_df['14_desc'])]['doc_id'])
checking2 = list(master_scorecard_df[master_scorecard_df['scorecard_present'] & pd.isnull(master_scorecard_df['1_desc'])]['doc_id'])

    
#############################################################################
# check the number of variables found per document
#############################################################################

#the first 2 accounts for doc_id and scorecard_present divide by 2 because descr + rating
master_scorecard_df['Outcomes_Amount'] = master_scorecard_df.apply(lambda x: (x.notnull().sum() - 2)/2, axis='columns')

print("max", master_scorecard_df['Outcomes_Amount'].max())
print("mean", master_scorecard_df['Outcomes_Amount'].mean())
print("min", master_scorecard_df['Outcomes_Amount'].min())
print("std", master_scorecard_df['Outcomes_Amount'].std())

master_dataCounts = pd.DataFrame(len(master_scorecard_df) - master_scorecard_df.apply(lambda x: x.isnull().sum(), axis='rows'))
master_dataCounts.sort_values(0, ascending=False, inplace=True)
master_dataCounts = master_dataCounts.drop('Outcomes_Amount', axis=0)

with pd.ExcelWriter(out_local + "bigsample_scorecard_raw.xlsx") as writer:
    master_scorecard_df.to_excel(writer, sheet_name= "values", index=False)
    master_dataCounts.to_excel(writer, sheet_name= "counts", index=True)


#############################################################################
# clean scorecard ratings
#############################################################################

def clean_rating(entry):
    # print(entry)
    if pd.isnull(entry):
        return np.nan
    rating = np.nan
    find_rating = re.match("^\s*(a|b|c){1}\s*(\+|-)?(?:[^a-z].*)*$", entry, flags=re.DOTALL) #also grabs the suffix i.e."+\-"
    if find_rating:
        rating=find_rating.group(1)
        suffix = find_rating.group(2)
        if suffix:
            rating= rating + suffix
    return rating

master_scorecard_clean = master_scorecard_df.copy()
to_clean = [x for x in master_scorecard_clean if "rating" in x]
for col in to_clean:
    master_scorecard_clean[col] = master_scorecard_df[col].apply(clean_rating)

master_dataCountsClean = pd.DataFrame(len(master_scorecard_clean) - master_scorecard_clean.apply(lambda x: x.isnull().sum(), axis='rows'))
master_dataCountsClean.sort_values(0, ascending=False, inplace=True)


with pd.ExcelWriter(out_local + "bigsample_scorecard_clean.xlsx") as writer:
    master_scorecard_clean.to_excel(writer, sheet_name= "values", index=False)
    master_dataCountsClean.to_excel(writer, sheet_name= "counts", index=True)
