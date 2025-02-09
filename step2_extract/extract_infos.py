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
from parse_page import extractInfos
from parse_pdf import identifyAllPages

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


out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/infos/"
out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/Variables/"


#############################
#  Import Keywords
#############################

keywords_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/keywords.xlsx"
infos = pd.read_excel(keywords_path, sheet_name="info")
info_set = set([x.lower() for x in list(infos['info'])])
del infos, keywords_path

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


#############################
#  Get Documents and Sample
#############################

with open("C:/Users/Asser.Maamoun/Documents/master_txtsCleanedInfo.json") as data_file:
    master_txtsCleaned = json.load(data_file)
del data_file

random.seed(1234)
sample_ids = sorted(random.sample(range(len(txt_paths)), 20))
sample_pdfs = []
for pdf in sample_ids:
    sample_pdfs.append(master_txtsCleaned[pdf])
del pdf


#############################################################################
#  Loop over all documents and get infos
#############################################################################

#select which pdfs we want to parse
pdfs_to_parse = list(range(len(txt_paths)))

############################################
#  Loop over and extract from documents
############################################

#Initialize the master dataframes
master_infoPages = []
master_infoText = []

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
    if 'info' in pagesIdentified:
        infoPages = pagesIdentified['info']
    else:
        infoPages = []
    master_infoPages.append(infoPages)
    
    #combined the scorecard pages
    infoText = ""
    for page_id in infoPages:
        infoText += cleanedPages[page_id] + "\n NEW PAGE \n\n"
    infoText = re.sub("\n NEW PAGE$", "", infoText)
    master_infoText.append(infoText)
del pdf_path, cleanedPages, pagesIdentified, infoPages, infoText
chi_time = datetime.now(timezone('America/Chicago'))
print("ending at", chi_time.strftime('%H:%M:%S'))



master_info_dict = []
chi_time = datetime.now(timezone('America/Chicago'))
print("starting at", chi_time.strftime('%H:%M:%S'))
for idx in range(len(pdfs_to_parse)):
    if idx % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(idx, "parsing at", chi_time.strftime('%H:%M:%S'))
    #grab the path and the scorecard pages
    pdf_path = pdf_paths[pdfs_to_parse[idx]]
    infoText = master_infoText[idx]
    info_dict = extractInfos(infoText, info_set, bad_chars, space_chars)
    info_dict["doc_id"] = idx
    info_dict["doc_path"] = pdf_path
    info_dict["info_present"] = int(infoText!="")
    master_info_dict.append(info_dict)
chi_time = datetime.now(timezone('America/Chicago'))
print("ending at", chi_time.strftime('%H:%M:%S'))
del idx, pdf_path, infoText, info_dict, chi_time

master_info_df = pd.DataFrame(master_info_dict)
cols = list(master_info_df)
cols.insert(0, cols.pop(cols.index('doc_id')))
cols.insert(1, cols.pop(cols.index('info_present')))
master_data = master_info_df.reindex(columns= cols)
del cols

#############################################################################
# check the number of variables found per document
#############################################################################


#the 2 accounts for doc_id and doc_path
front = ['doc_id', 'doc_path', 'info_present']
reorder = front + sorted([x for x in master_data.columns if x not in front])
master_data = master_data[reorder]
del front, reorder

master_data['Non_Missing'] = master_data.apply(lambda x: x.notnull().sum(), axis='columns') - 3 #subtract docid, present, docpath

print("max", master_data['Non_Missing'].max())
print("mean", master_data['Non_Missing'].mean())
print("min", master_data['Non_Missing'].min())
print("std", master_data['Non_Missing'].std())

master_dataCounts = pd.DataFrame(len(master_data) - master_data.apply(lambda x: x.isnull().sum(), axis='rows'))
master_dataCounts.sort_values(0, ascending=False, inplace=True)
master_dataCounts = master_dataCounts.drop('Non_Missing', axis=0)

with pd.ExcelWriter(out_local + "bigsample_infos_raw.xlsx") as writer:
    master_data.to_excel(writer, sheet_name= "values", index=False)
    master_dataCounts.to_excel(writer, sheet_name= "counts")





