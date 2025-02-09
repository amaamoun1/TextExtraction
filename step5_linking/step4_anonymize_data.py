# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 20:32:02 2020

@author: Asser.Maamoun
"""


#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")

from datetime import date
import pandas as pd
import numpy as np
import re


#############################################################################
#         File locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################################################################
#    Import Data
#############################################################################

master_clean = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name = "Values")


#############################################################################
#         Take out Candidate and Company Names
#############################################################################


############################################
#  encode the candidate name and company names
############################################

labels, levels = pd.factorize(master_clean["candidate_name_raw"])
master_clean["candidate_name_raw_code"] = labels

labels, levels = pd.factorize(master_clean["candidate_name_clean"])
master_clean["candidate_name_clean_code"] = labels

labels, levels = pd.factorize(master_clean["candidate_firstname"])
master_clean["candidate_firstname_code"] = labels

labels, levels = pd.factorize(master_clean["candidate_lastname"])
master_clean["candidate_lastname_code"] = labels

labels, levels = pd.factorize(master_clean["company_raw"])
master_clean["company_raw_code"] = labels

labels, levels = pd.factorize(master_clean["company_clean"])
master_clean["company_clean_code"] = labels

del labels, levels


############################################
#  remove name from recommendation, prepared for, and scorecard entries
############################################

names_dont_clean = ['formatted table', 'dr', 'md', 'mba', 'cfa', 'cpa', 'phd',
             'mr', 'mrs', 'ms', 'rev', 'jr', 'sr', 'ii', 'iii', 'iv']

#collect all words part of candidate or company name
names_clean = []
for i, row in master_clean.iterrows():
    #drop non-letters and non-spaces
    if pd.notnull(row["candidate_name_raw"]):
        clean1 = re.sub("[^\\sa-z]","", row["candidate_name_raw"])
        if pd.notnull(row["candidate_name_clean"]):
            clean1 += " " + row["candidate_name_clean"]
        for x in names_dont_clean:
            clean1 = re.sub("\\b" + x + "\\b", "", clean1)
    else:
        clean1 = ""
    names_clean.append(clean1)
    if pd.notnull(row["company_raw"]):
        clean2 = re.sub("[^\\sa-z]","", row["company_raw"])
        if pd.notnull(row['company_clean']):
            clean2 += " " + re.sub("[^\\sa-z]","", row["company_clean"])
        clean2 = re.sub("\\binc\\b", "", clean2)
    else:
        clean2 = ""
    names_clean.append(re.sub("\\s+", " ", clean1 + " " + clean2))
del clean1, clean2, i, row, names_dont_clean

#split the names into a list of words
names_split = [re.split("\\s", x) for x in names_clean]
names_parts = []
for x in names_split:
    names_parts.append(list(set(x)))
del names_clean, names_split, x

#clean from the columns in to_clean
to_clean = ["rating", "recommendation", "prepared_for"] + [x for x in master_clean.columns if ("sc" in x and "desc" in x)]
for col in to_clean:
    old = list(master_clean[col])
    new = []
    i = 0
    while i < len(old):
        name = names_parts[i]
        curr = old[i]
        if pd.notnull(curr):
            for x in name:
                if x != "":
                    curr = re.sub(x, "[name]", curr)
        new.append(curr)
        i+=1
    master_clean[col] = new

del new, old, names_parts, i, name, curr, x, to_clean, col




##########################
#  save a safe version for steve/morten
##########################

to_drop = ["doc_name", "candidate_name_raw",
           "candidate_name_clean", "candidate_firstname",
           "candidate_lastname", "company_raw", "company_clean", "career_clean",
           "career_clean_olddata", "career_found", 'linkedin_link', 'businessweek_link',
           'other_link_1', 'other_link_2', 'career_info', 'hired_new_company', 'bvdid', 'success_old_detail', 'success_new_detail', 'pitchbook_link'
           ]
master_safe = master_clean.copy()
master_safe.drop(columns=to_drop, axis=1, inplace=True)
cols = ['doc_id_old', 'doc_id_new', 'is_pre2012', 'info_present', 'candidate_name_raw_code',
             'candidate_name_clean_code', 'candidate_firstname_code', 'candidate_lastname_code', 
             'candidate_flag', 'company_raw_code', 'company_clean_code', 'company_flag']
cols += list(master_safe.columns)[6:-6]
master_safe = master_safe[cols]
master_safe = master_safe.sort_values(["doc_id_new", "doc_id_old"])
master_safeCounts = pd.DataFrame(master_safe.apply(lambda x: x.notnull().sum(), axis='index'))
master_safeCounts.reset_index(level=0, inplace=True)
master_safeCounts.columns = ["variable", "count"]

TitleFinalCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="TitleCounts")
PrepByFinalCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="PrepbyCounts")
GenderFinalCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="GenderCounts")
PurposeFinalCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="PurposeCounts")
CollegesFinalCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CollegeCounts")
UndergradFinalCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="UndergradCounts")
MBAFinalCounts =  pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="MBACounts")
CompTemplate = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CompTemplates")
CompTemplateCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CompTemplateCounts")
CompMergers = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CompMergers")
CompRawOverlaps = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CompRawOverlaps")
CompMergedOverlaps = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CompMergedOverlaps")
CompRawCountsYear = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CompRawCountsYear")
CompMergedCountsYear = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="CompMergedCountsYear")
ScorecardResults = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="ScorecardTrainingResults")
ScorecardFinalCounts = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name="ScorecardTopics")

#write to excel
with pd.ExcelWriter(out_local + "extractions_merged_anonymized.xlsx") as writer:
    master_safe.to_excel(writer, sheet_name="Values", index=False)
    master_safeCounts.to_excel(writer, sheet_name="Counts", index=False)
    TitleFinalCounts.to_excel(writer, sheet_name="TitleCounts", index=False)
    PrepByFinalCounts.to_excel(writer, sheet_name="PrepbyCounts", index=False)
    PurposeFinalCounts.to_excel(writer, sheet_name="PurposeCounts", index=False)
    GenderFinalCounts.to_excel(writer, sheet_name="GenderCounts", index=False)
    CollegesFinalCounts.to_excel(writer, sheet_name="CollegeCounts", index=False)
    UndergradFinalCounts.to_excel(writer, sheet_name="UndergradCounts", index=False)
    MBAFinalCounts.to_excel(writer, sheet_name="MBACounts", index=False)
    CompTemplate.to_excel(writer, sheet_name="CompTemplates", index=False)
    CompTemplateCounts.to_excel(writer, sheet_name="CompTemplateCounts", index=False)
    CompMergers.to_excel(writer, sheet_name="CompMergers", index=False)
    CompRawOverlaps.to_excel(writer, sheet_name="CompRawOverlaps", index=False)
    CompRawCountsYear.to_excel(writer, sheet_name="CompRawCountsYear", index=False)
    CompMergedOverlaps.to_excel(writer, sheet_name="CompMergedOverlaps", index=False)
    CompMergedCountsYear.to_excel(writer, sheet_name="CompMergedCountsYear", index=False)
    ScorecardResults.to_excel(writer, sheet_name="ScorecardTrainingResults", index=False)
    ScorecardFinalCounts.to_excel(writer, sheet_name="ScorecardTopics", index=False)
del writer
