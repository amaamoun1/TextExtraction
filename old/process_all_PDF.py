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
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/PDFTools')

#import the codes that are needed
from parse_pdf import parse_pdf
from clean_page import cleanPage
from MergeTools import overlapMatRaw
from MergeTools import overlapMatPercent
from MergeTools import checkMerge
from MergeTools import merge_vars
from shutil import copyfile

#import the relevant python libraries
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


out_git = "C:/Users/Asser.Maamoun/Documents/TextExtraction/outputGIT/str_"
out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/str_"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/Variables/"


#############################################################################
#       Import Keywords
#############################################################################

keywords_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/Variables/Keywords.xlsx"
competencies = pd.read_excel(keywords_path, sheet_name="competency")
comp_set = set([x.lower() for x in list(competencies['competency'])])

infos = pd.read_excel(keywords_path, sheet_name="info")
info_set = set([x.lower() for x in list(infos['info'])])
del competencies, infos, keywords_path

colleges_path ="C:/Users/Asser.Maamoun/Documents/TextExtraction/Universities/colleges_cleaned.xlsx"
colleges = pd.read_csv(colleges_path)
del colleges_path

bad_chars = ["’", "'", ",", ".", "\\", "ability to ", "able to ", "\u201f", \
             "\ufb03", "\u2010", "\uf0b7", "\u2022"]
bad_chars2 = ["’", "'", "\u201f", "\ufb03", "\u2010", "\uf0b7"]
space_chars = ["/"]

name_set = set(["candidate name", "candidate", "feedback recipient",
                    "leader Name", "executive name", "prepared for", "prepared by",
                    "purpose of this assessment", "purpose of this feedback process",
                    "executive assessment", "smart assessment®", "smartassessment®",
                    "smartfeedback® report", "smartfeedback®",
                    "developmental assessment", "smartassessment",
                    "smartassessment® report", "developmental report",
                    "executive report", 
                    "smartassessment report", "executive assessment report", 
                    "smart assessment® report", "developmental assessment report",
                    ])

clean_obs = (comp_set, info_set, name_set, bad_chars, space_chars, bad_chars2, colleges)
del comp_set, info_set, name_set, bad_chars, space_chars, bad_chars2, colleges



#############################################################################
#        Get a list of all the PDFs
#############################################################################

#Step 1: Get a list of all the original interview docs
#check the interview folder and the folder with doc converted to docx
interview_folder_path = "C:/Users/Asser.Maamoun/Documents/Interviews"
converted_folder_path = "C:/Users/Asser.Maamoun/Documents/ConvertedInterviews"
interview_docs = [os.path.join(interview_folder_path, f) for f in os.listdir(interview_folder_path) if os.path.isfile(os.path.join(interview_folder_path, f))]
converted_docs = [os.path.join(converted_folder_path, f) for f in os.listdir(converted_folder_path) if os.path.isfile(os.path.join(converted_folder_path, f))]
all_docs = interview_docs + converted_docs

#Step 2: Loop over and get corresponding .docx files and .pdf files
#This is done to ensure that docids are the same across pdfs and docx code
doc_paths = []
docx_paths = []
pdf_paths = []
txt_paths = []
for doc_id in range(len(all_docs)):
    #first read in the given document
    name = all_docs[doc_id]
    if "~$" in name:
        continue
    elif (".docx" not in name) and (".DOCX" not in name):
        doc_paths.append(name)
    else:
        docx_paths.append(name)
        pdf_path = re.sub("docx$","pdf", name, flags=re.IGNORECASE)
        txt_path = re.sub("docx$","txt", name, flags=re.IGNORECASE)
        if "ConvertedInterviews" in pdf_path:
            pdf_path = re.sub("ConvertedInterviews", "PDFs", pdf_path)
            txt_path = re.sub("ConvertedInterviews", "TXTs", txt_path)
        else:
            pdf_path = re.sub("Interviews", "PDFs", pdf_path)
            txt_path = re.sub("Interviews", "TXTs", txt_path)
        pdf_paths.append(pdf_path)
        txt_paths.append(txt_path)

del interview_folder_path, converted_folder_path, interview_docs, converted_docs, all_docs
del doc_paths, doc_id, name, pdf_path, txt_path




#############################################################################
#  Loop over all documents, grab text, and clean
#############################################################################

master_txts = []
master_txtsCleaned = []
for txt_path in txt_paths:
    #grab text
    text_file = open(txt_path, "r")
    #split into pages
    text_split = text_file.read().split('\n THIS IS A NEW PAGE \n')
    master_txts.append(text_split)
    #clean each page
    cleanedPages = []
    for page in text_split:
        cleanedPages.append(cleanPage(page))
    master_txtsCleaned.append(cleanedPages)
del txt_path, text_file, text_split, cleanedPages, page

#############################################################################
#  grab a random sample to test things out on
#############################################################################

random.seed(1234)
sample_ids = sorted(random.sample(range(len(pdf_paths)), 20))
sample_pdfs = []
for pdf in sample_ids:
    #copyfile(pdf_paths[pdf], re.sub("PDFs", "PDFSample", pdf_paths[pdf]))
    sample_pdfs.append(master_txtsCleaned[pdf])
    
del pdf


#############################################################################
#  Loop over all documents and get competencies
#############################################################################

############################################
############## INPUTS ######################
############################################

#select which pdfs we want to parse
pdfs_to_parse = list(range(len(pdf_paths)))
#pdfs_to_parse = sample_ids

#select which tables we want to parse
#tables_to_parse = ["info", "competency", "scorecard"]
tables_to_parse = ["info", "competency"]

#this will be the name included in any file output
out_name = ''.join(tables_to_parse)

############################################
#  Loop over and extract competencies from documents
############################################

#Initialize the master dataframes
master_tracker = pd.DataFrame()
master_data = pd.DataFrame()
master_unclean = {}


for doc_id in pdfs_to_parse:
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    #parse for the tables wanted
    pdf_path = pdf_paths[doc_id]
    cleanedPages = master_txtsCleaned[doc_id]
    (doc_data, table_tracker, doc_unclean) = parse_pdf(doc_id, pdf_path, cleanedPages, tables_to_parse, clean_obs)
    #append to master dataframes
    master_tracker = master_tracker.append(table_tracker, sort=False)
    master_data = master_data.append(doc_data, sort=False)


del chi_time, doc_data, table_tracker, pdf_path, doc_id, doc_unclean

outcome_cols = [x for x in master_data.columns if "outcome" in x]
doc_cols = ['doc_id', 'doc_path']
comp_cols = [x for x in master_data.columns if x not in outcome_cols and x not in doc_cols]

master_data = master_data[doc_cols + outcome_cols + comp_cols]
del outcome_cols, doc_cols, comp_cols

#############################################################################
# check the number of variables found per document
#############################################################################


#the 2 accounts for doc_id and doc_path
master_data['Non_Missing'] = len(master_data.columns) - 2 - master_data.apply(lambda x: x.isnull().sum(), axis='columns')

print("max", master_data['Non_Missing'].max())
print("mean", master_data['Non_Missing'].mean())
print("min", master_data['Non_Missing'].min())
print("std", master_data['Non_Missing'].std())

master_dataCounts = pd.DataFrame(len(master_data) - master_data.apply(lambda x: x.isnull().sum(), axis='rows'))
master_dataCounts.sort_values(0, ascending=False, inplace=True)
master_dataCounts = master_dataCounts.drop('Non_Missing', axis=0)

with pd.ExcelWriter(out_local + out_name + "_raw.xlsx") as writer:
    master_data.to_excel(writer, sheet_name= "values")
    master_dataCounts.to_excel(writer, sheet_name= "counts")



###############################################################################
# Merge together variables
###############################################################################


#get overlapping matrix and write a raw and percent version
overlaps_raw = overlapMatRaw(master_data)
overlaps_percent = overlapMatPercent(overlaps_raw)



############################################
#  Perform the merge
############################################

#load the variables to merge
mergers_list = []
for table in tables_to_parse:
    mergers_list.append(pd.read_excel(var_path + 'varMergersMain.xlsx', sheet_name=table+"_complete"))
mergers_df = pd.concat(mergers_list, axis=0, join='outer', ignore_index=True, sort=False)
del table, mergers_list

#create a dictionary of variables that we can merge
mergers_dict = checkMerge(master_data, overlaps_raw, mergers_df)
del mergers_df

#merge together the non-overlapping variables in master_merged
master_merged = master_data.copy()
for name in mergers_dict.keys():
    master_merged = merge_vars(master_merged, mergers_dict[name], name)
del name, mergers_dict



############################################
#  Cleaned Merge: Discard any non-ratings
############################################

#only keep the letter ratings
to_replace = ["n/a", "no issues", "limited experience", "NF", "asterisk", "limited", "na"]
master_mergedClean = master_merged.replace(to_replace, np.nan)
unclean = set()
for x in clean_obs[0]:
    if x in master_mergedClean.columns:
        d = master_mergedClean[x].value_counts()
        for e in d.keys():
            if e not in ["a+", "a", "a-", "b+", "b", "b-", "c", "c+", "c-"]:
                unclean.add(e)
print("unclean:", list(unclean))
del x, d, e, unclean, to_replace



############################################
#  Counts and Overlaps on merged data
############################################

#create counts of the merged variables
master_mergedCounts = pd.DataFrame(len(master_merged) - master_merged.apply(lambda x: x.isnull().sum(), axis='rows'))
master_mergedCounts.sort_values(0, ascending=False, inplace=True)
master_mergedCounts = master_mergedCounts.drop('Non_Missing', axis=0)

#create counts of the mereed clean variables
master_mergedCleanCounts = pd.DataFrame(len(master_mergedClean) - master_mergedClean.apply(lambda x: x.isnull().sum(), axis='rows'))
master_mergedCleanCounts.sort_values(0, ascending=False, inplace=True)
master_mergedCleanCounts = master_mergedCleanCounts.drop('Non_Missing', axis=0)

#create overlaps of the merged (unclean) variables
overlaps_merged_raw = overlapMatRaw(master_merged)
overlaps_merged_percent = overlapMatPercent(overlaps_merged_raw)


############################################
#  Write Information to excels
############################################

#write unmerged uncleaned overlaps
with pd.ExcelWriter(out_git + out_name + "_overlapsMerged.xlsx") as writer:
    overlaps_merged_raw.to_excel(writer, sheet_name="overlaps_raw")
    overlaps_merged_percent.to_excel(writer, sheet_name="overlap_percent")
del writer

#write merged uncleaned overlaps
with pd.ExcelWriter(out_git + out_name + "_overlapsMerged.xlsx") as writer:
    overlaps_merged_raw.to_excel(writer, sheet_name="overlaps_raw")
    overlaps_merged_percent.to_excel(writer, sheet_name="overlap_percent")
del writer

#write the cleaned ratings and counts to local
with pd.ExcelWriter(out_local + out_name + "_merged.xlsx") as writer:
    master_mergedClean.to_excel(writer, sheet_name="values")
    master_mergedCleanCounts.to_excel(writer, sheet_name="counts")
del writer

#write cleaned and uncleaned counts to outputGIT
with pd.ExcelWriter(out_git + out_name + "_mergedCounts.xlsx") as writer:
    master_allCounts = pd.concat([master_mergedCounts, master_mergedCleanCounts], axis=1, join='outer', ignore_index=True, sort=False)
    master_allCounts.columns = ["including_nan", "excluding_nan"]
    master_allCounts.to_excel(writer, sheet_name="variable counts")
del writer





