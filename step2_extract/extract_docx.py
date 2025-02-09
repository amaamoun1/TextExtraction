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
from parse_document import parse_document
from convert_structure import convert_docx
from flatten_structure import flatten_tables
from utilities import move_docid
from utilities import clear_folder
from toc_helper import tocCleaner
from toc_helper import docTocChecker

#import the relevant python libraries
import pickle
import pandas as pd
import numpy as np
import re
import random
from datetime import datetime
from pytz import timezone


#############################################################################
#         Output locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/docx/bigsample_"
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

master_tables = []
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
    master_tables.append(flatten_tables(result[0]))
del doc_id, chi_time, path, result


 
###############################################################################
#  Loop over all documents and get find potential competency vars
###############################################################################

############## INPUTS ######################
    
docx_to_parse = list(range(len(master_paths)))
tables_to_parse = ["info", "competency"]
out_name = ''.join(tables_to_parse)



###############################################################################
#  Loop over all documents and get info/competency vars
###############################################################################

#Initialize the master dataframes
master_tracker = pd.DataFrame()
master_data = pd.DataFrame()
master_unclean_entries = {} #tracks competency entries without a clear rating


curr_doc = 0
for doc_id in docx_to_parse:
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
    #parse for the tables wanted
    curr_path = master_paths[doc_id]
    curr_tables = master_tables[doc_id]
    # curr_string = master_strings[doc_id]
    doc_data, table_tracker, doc_unclean_entries = \
        parse_document(curr_doc, doc_id, curr_path, curr_tables, tables_to_parse, clean_obs)
    #append the useful data to our master versions
    master_tracker = master_tracker.append(table_tracker, sort=False)
    master_data = master_data.append(doc_data, sort=False)
    #add the unclean entries to our dictionary for double checking
    for unclean_entry in doc_unclean_entries:
        if unclean_entry not in master_unclean_entries:
            master_unclean_entries[unclean_entry] = 1
        else:
            master_unclean_entries[unclean_entry] += 1
    curr_doc+=1

del chi_time, doc_data, table_tracker, curr_path, curr_tables, \
    doc_id, curr_doc, unclean_entry, doc_unclean_entries


#track the number of non-missing entries per document
master_data['Non_Missing'] = len(master_data.columns) - 2 - master_data.apply(lambda x: x.isnull().sum(), axis='columns')


############################################
#  variable counts
############################################


master_dataCounts = pd.DataFrame(len(master_data) - master_data.apply(lambda x: x.isnull().sum(), axis='rows'))
master_dataCounts.sort_values(0, ascending=False, inplace=True)
master_dataCounts = master_dataCounts.drop('Non_Missing', axis=0)

print("max", master_data['Non_Missing'].max())
print("mean", master_data['Non_Missing'].mean())
print("min", master_data['Non_Missing'].min())
print("std", master_data['Non_Missing'].std())


with pd.ExcelWriter(out_local + out_name + "_raw.xlsx") as writer:
    master_data.to_excel(writer, sheet_name= "values")
    master_dataCounts.to_excel(writer, sheet_name= "counts")


############################################
#  documents that need to be checked
############################################

# =============================================================================
# To Watch out for:
#  - master_tracker...issue == "multiple info" ... these tend to be a master 
#                document of compiled sub-documents
#  - master_tracker...issue == "multiple competency" ...  need to check that 
#               these only occur with documents on multiple candidates
#  - master_tracker...parsed != 1, 2, 5 ... either a competency table is 
#               singular and on either one or stretching into two pages
#               or the competencies are in a grid of 4 categories
# =============================================================================


# #list of documents that have the above "to watch out for"
# master_toCheck = master_tracker.copy()
# master_toCheck = master_toCheck[(master_toCheck['issue'] == "multiplecompetency") | ([x not in [0, 1, 2, 5] for x in master_toCheck['parsed']])]
# short_paths = [re.sub(r"C:/Users/Asser.Maamoun/Documents/Interviews\\", "", master_paths[x]) for x in master_toCheck['doc_id']]
# master_toCheck['path'] = short_paths
# master_toCheck = master_toCheck[["path", "parsed", "unclean", "doc_id", "table", "unclean", "string_parsed"]]

# #copy the to_check documents into a separate folder
# clear_folder("Interviews_toCheck")
# for doc_id in master_toCheck['doc_id']:
#     move_docid(doc_id, "Interviews_toCheck", master_paths)
# del doc_id, short_paths



############################################
# Double Check that we have found all competencies
############################################

# #compares with a simple string search for a competency section
# notfoundComp = set()
# comp_to_check = list(master_tracker[(master_tracker['parsed']==0) & (master_tracker['string_parsed']==1)]['doc_id'])
# for x in comp_to_check: notfoundComp.add(docx_paths[x])    

# #check that we found competency tables in all documents with competency in the TOC
# comp_to_check = docTocChecker(master_tracker, master_cleanedTOC, docx_paths, 'competency')
# for x in comp_to_check: notfoundComp.add(x) 

# #total documents incorrectly without competencies
# notfoundComp = sorted(list(notfoundComp))
# print("missed", len(notfoundComp), "competency tables out of", len(docx_paths))

# #write the file_paths to a text file to check
# tocheckFile = open(r"outputLOCAL\\toCheck.txt", "w")
# for path in notfoundComp: 
#     tocheckFile.write(path)
#     tocheckFile.write("\n")
# tocheckFile.close()
# del tocheckFile, notfoundComp, path


# #after checking the documents, create a cleaned version for Github
# notFoundReasons_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/notFoundReasons.xlsx"
# notFoundReasons = pd.read_excel(notFoundReasons_path, sheet_name="Sheet1")
# notFoundReasons['Doc_id'] = [master_paths.index(x) for x in notFoundReasons['Path']]
# notFoundReasons.drop(['Path', 'Unnamed: 6'], axis=1, inplace=True)
# notFoundReasonsClean_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/outputGIT/notFoundReasonsClean.xlsx"
# notFoundReasons.to_excel(notFoundReasonsClean_path, index=False)

# del notFoundReasons_path, notFoundReasons, notFoundReasonsClean_path, x


############################################
# Take a sample of documents without competencies
############################################
    
#identify a random subset
# random.seed(1234)
# noCompID = list(master_tracker[(master_tracker['table']=="competency") & (master_tracker['parsed']==0)]['doc_id'])
# noCompSample = sorted(random.sample(noCompID, 30))

# #copy interviews to a new folder
# for doc_id in noCompSample:
#     move_docid(doc_id, "Sample_without_Competencies", master_paths)
# del noCompID, noCompSample, doc_id



    



