# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 17:37:33 2020

@author: Asser.Maamoun
"""


#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
os.getcwd() #double-check


#add the relevant folders of code to the system path...so that python can access all the codes
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/PDFTools')

#import the codes that are needed
from clean_page import cleanPageDefault
from clean_page import cleanPageInfo
from clean_page import cleanPageScorecard

#import the relevant python libraries
import json
import pandas as pd
from datetime import datetime
from pytz import timezone


#############################################################################
#         file locations
#############################################################################


out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/outputLOCAL/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/Variables/"


#############################################################################
#  Get the docid mapping and load txts
#############################################################################


docid_mapping = pd.read_excel(out_local + "docid_mapping.xlsx")

master_txts = []
for i, row in docid_mapping.iterrows():
    doc_id = row['doc_id']
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "reading at", chi_time.strftime('%H:%M:%S'))
    #grab text
    txt_path = row['txt_path']
    text_file = open(txt_path, "r")
    #split into pages
    text_split = text_file.read().split('\n THIS IS A NEW PAGE \n')
    master_txts.append(text_split)
del txt_path, text_file, text_split, i, row, chi_time, doc_id


#############################################################################
#  Clean Txts the default method
#############################################################################


master_txtsCleanedDefault = []
doc_id = 0
for text_split in master_txts:
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "cleaning at", chi_time.strftime('%H:%M:%S'))
    cleanedPages = []
    for page in text_split:
        cleanedPages.append(cleanPageDefault(page))
    master_txtsCleanedDefault.append(cleanedPages)
    doc_id += 1
del text_split, cleanedPages, page, doc_id, chi_time


with open("C:/Users/Asser.Maamoun/Documents/master_txtsCleanedDefault.json","w") as outfile:
    json.dump(master_txtsCleanedDefault, outfile)
del master_txtsCleanedDefault, outfile



#############################################################################
#  Clean Txts for the Info extraction
#############################################################################


master_txtsCleanedInfo = []
doc_id = 0
for text_split in master_txts:
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "cleaning at", chi_time.strftime('%H:%M:%S'))
    cleanedPages = []
    for page in text_split:
        cleanedPages.append(cleanPageInfo(page))
    master_txtsCleanedInfo.append(cleanedPages)
    doc_id += 1
del text_split, cleanedPages, page, doc_id, chi_time


with open("C:/Users/Asser.Maamoun/Documents/master_txtsCleanedInfo.json","w") as outfile:
    json.dump(master_txtsCleanedInfo, outfile)
del master_txtsCleanedInfo, outfile
    

#############################################################################
#  Clean Txts for scorecard extraction
#############################################################################


master_txtsCleanedScorecard = []
doc_id = 0
for text_split in master_txts:
    if doc_id % 500 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "cleaning at", chi_time.strftime('%H:%M:%S'))
    cleanedPages = []
    for page in text_split:
        cleanedPages.append(cleanPageScorecard(page))
    master_txtsCleanedScorecard.append(cleanedPages)
    doc_id += 1
del text_split, cleanedPages, page, doc_id, chi_time


with open("C:/Users/Asser.Maamoun/Documents/master_txtsCleanedScorecard.json","w") as outfile:
    json.dump(master_txtsCleanedScorecard, outfile)
del master_txtsCleanedScorecard, outfile