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
from shutil import copyfile

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


out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/stregths_weaknesses/"
out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################
#  Import Keywords
#############################

keywords_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/keywords.xlsx"
competencies = pd.read_excel(keywords_path, sheet_name="competency")
comp_set = set([x.lower() for x in list(competencies['competency'])])
del competencies, keywords_path


bad_chars = ["’", "'", ",", ".", "\\", "ability to ", "able to ", "\u201f", \
             "\ufb03", "\u2010", "\uf0b7", "\u2022"]
space_chars = ["/"]


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
sample_pdfs = {}
for pdf in sample_ids:
    sample_pdfs[pdf] = master_txtsCleaned[pdf]
    path = mapping_df[mapping_df['doc_id']==pdf].squeeze()['docx_path']
    new_path = re.sub("/Pre2012Docs\\\\", "/Sample/docid_" + str(pdf) + "_", path)
    new_path = re.sub("/Interviews\\\\", "/Sample/docid_" + str(pdf) + "_", new_path)
    copyfile(path, new_path)
del pdf


#############################################################################
#  Loop over all documents and get competencies
#############################################################################

#select which pdfs we want to parse
pdfs_to_parse = list(range(len(pdf_paths)))

############################################
#  Loop over and extract from documents
############################################

#Initialize the master dataframes
master_compPages = []
master_compText = []

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
    if 'competency' in pagesIdentified:
        compPages = pagesIdentified['competency']
    else:
        compPages = []
    master_compPages.append(compPages)
    
    #combined the scorecard pages
    compText = ""
    for page_id in compPages:
        compText += cleanedPages[page_id] + "\n NEW PAGE \n\n"
    compText = re.sub("\n NEW PAGE$", "", compText)
    master_compText.append(compText)
del pdf_path, cleanedPages, pagesIdentified, compPages, compText, doc_id, page_id
chi_time = datetime.now(timezone('America/Chicago'))
print("ending at", chi_time.strftime('%H:%M:%S'))



# master_comp_dict = []
# chi_time = datetime.now(timezone('America/Chicago'))
# print("starting at", chi_time.strftime('%H:%M:%S'))
# for idx in range(len(pdfs_to_parse)):
#     if idx % 500 == 0:
#         chi_time = datetime.now(timezone('America/Chicago'))
#         print(idx, "parsing at", chi_time.strftime('%H:%M:%S'))
#     #grab the path and the scorecard pages
#     pdf_path = pdf_paths[pdfs_to_parse[idx]]
#     compText = master_compText[idx]
#     comp_dict = extractCompetencies(compText, comp_set, bad_chars, space_chars)
#     comp_dict["doc_id"] = idx
#     comp_dict["doc_path"] = pdf_path
#     comp_dict["comp_present"] = int(compText!="")
#     master_comp_dict.append(comp_dict)

# chi_time = datetime.now(timezone('America/Chicago'))
# print("ending at", chi_time.strftime('%H:%M:%S'))
# del idx, pdf_path, compText, comp_dict, chi_time

# master_comp_df = pd.DataFrame(master_comp_dict)
# cols = list(master_comp_df)
# cols.insert(0, cols.pop(cols.index('doc_id')))
# cols.insert(1, cols.pop(cols.index('comp_present')))
# master_data = master_comp_df.reindex(columns= cols)
# del cols

# #############################################################################
# # check the number of variables found per document
# #############################################################################


# #the 2 accounts for doc_id and doc_path
# master_data['Non_Missing'] = master_data.apply(lambda x: x.notnull().sum(), axis='columns') - 1

# print("max", master_data['Non_Missing'].max())
# print("mean", master_data['Non_Missing'].mean())
# print("min", master_data['Non_Missing'].min())
# print("std", master_data['Non_Missing'].std())

# master_dataCounts = pd.DataFrame(len(master_data) - master_data.apply(lambda x: x.isnull().sum(), axis='rows'))
# master_dataCounts.sort_values(0, ascending=False, inplace=True)
# master_dataCounts = master_dataCounts.drop('Non_Missing', axis=0)

# with pd.ExcelWriter(out_local + "bigsample_competencies_raw.xlsx") as writer:
#     master_data.to_excel(writer, sheet_name= "values", index=False)
#     master_dataCounts.to_excel(writer, sheet_name= "counts")


