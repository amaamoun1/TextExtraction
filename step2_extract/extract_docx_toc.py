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
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_docx/DocxInterpreter')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_docx/DocxExtractor')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_docx/DocxString')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')


#import the codes that are needed
from convert_structure import convert_docx
from flatten_structure import flatten_tables
from utilities import move_docid
from utilities import clear_folder
from toc_helper import tocCleaner

#import the relevant python libraries
import pandas as pd
import numpy as np
import re
import random
from datetime import datetime
from pytz import timezone


#############################################################################
#         Output locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/docx/"
out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################################################################
#       Import Keywords
#############################################################################

keywords_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/keywords.xlsx"
competencies = pd.read_excel(keywords_path, sheet_name="competency")
comp_set = set([x.lower() for x in list(competencies['competency'])])

infos = pd.read_excel(keywords_path, sheet_name="info")
info_set = set([x.lower() for x in list(infos['info'])])
del competencies, infos, keywords_path

bad_chars = ["’", "'", ",", ":", ";", " goes here", "tag start ", "*", "#", "=", "+", ".", "\\", \
             "ability to ", "able to ", "\u201f", "\ufb03", "\u2010", "\uf0b7"]
space_chars = ["/", "-"]


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


clean_obs = (comp_set, info_set, name_set, bad_chars, space_chars)
del comp_set, info_set, name_set, bad_chars, space_chars

#############################################################################
#        Get a list of all the interview documents 
#############################################################################

mapping_df = pd.read_excel(out_folder + "docid_mapping.xlsx", index=False)
mapping_df = mapping_df.sort_values('doc_id')



###############################################################################
#  Loop over all documents and get docx structure
###############################################################################

master_tocs = []
master_paths = []

for i, row in mapping_df.iterrows():
    doc_id = row['doc_id']
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    #find the document path and parse for the tables wanted
    path = row['docx_path']
    master_paths.append(path)
    result = convert_docx(path)
    master_tocs.append(result[1])
del doc_id, chi_time, path, result


 
###############################################################################
#  Loop over all documents and get toc entries
###############################################################################   

#create dictionaries that track TOC counts
toc_rawCounts={}
toc_cleanCounts = {}
master_cleanedTOC = {}
duplicates = set()
doc_id = 0
total_TOC = 0
for toc in master_tocs:
    curr_clean = {}
    master_cleanedTOC[doc_id] = set()
    if len(toc)>0:
        total_TOC +=1
    for section_info in toc:
        #create a dictionary of raw TOC entries
        section = section_info[0].lower()
        if section == "":
            continue
        if section not in toc_rawCounts.keys():
            toc_rawCounts[section]=1
        else:
            toc_rawCounts[section]+=1
        #create a dictionary of cleaned TOC entries 
        section_clean = tocCleaner(section)
        #keep track of and do not not double count duplicates
        if section_clean in curr_clean.keys():
            if section != curr_clean[section_clean]:
                duplicates.add(''.join(["<", section_clean, "> found in <", section, "> and <", curr_clean[section_clean], ">"]))
            continue
        curr_clean[section_clean] = section
        #add to cleaned dictionary
        if section_clean not in toc_cleanCounts.keys():
            toc_cleanCounts[section_clean] = 1
        else:
            toc_cleanCounts[section_clean] += 1
        #add to master_cleanedTOC
        master_cleanedTOC[doc_id].add(section_clean)
    doc_id += 1

#print duplicates
for x in sorted(list(duplicates)):
    print(x)
del toc, section, section_info, section_clean, doc_id, x, curr_clean


#transform variable counts to dataframes
toc_rawCounts = pd.DataFrame(toc_rawCounts.items(), columns=["Entry", "Count"])
toc_rawCounts.sort_values(by="Count", axis=0, ascending=False, inplace=True)
toc_cleanCounts = pd.DataFrame(toc_cleanCounts.items(), columns=["Entry", "Count"])
toc_cleanCounts.sort_values(by="Count", axis=0, ascending=False, inplace=True)
toc_rawCounts["Percent"] = toc_rawCounts['Count'] / total_TOC * 100
toc_cleanCounts["Percent"] = toc_cleanCounts['Count'] / total_TOC * 100

#export the variable counts to excel
with pd.ExcelWriter(out_local + "bigsample_tocCounts.xlsx") as writer:
    toc_rawCounts.to_excel(writer, sheet_name = "raw_counts", index=False)
    toc_cleanCounts.to_excel(writer, sheet_name = "merged_counts", index=False)



