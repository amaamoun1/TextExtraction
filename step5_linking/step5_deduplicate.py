# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 13:53:41 2020

@author: Asser.Maamoun
"""


#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linkedin')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')

from merge_functions import overlapMatRaw

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


#load the linkages and the new data
master_dups = pd.read_excel(out_local + "extractions_merged_anonymized.xlsx")

#deduplicate
master_clean = master_dups[master_dups['is_duplicate']==0]


###############################################################################
# Competency Counts over time
###############################################################################

def check_date(date):
    if pd.isnull(date):
        return False
    elif re.match('^(\\d{4})\\-(\\d{2})\\-(\\d{2})$', date):
        return True
    else:
        return False

#format the dates from the info files
to_keep = [check_date(date) for date in master_clean['date_clean']]
copy = master_clean.copy()[to_keep]
copy['year'] = copy['date_clean'].apply(lambda x: int(x[:4]))
copy = copy[copy['year']<2020]
copy = copy.drop(['date_clean'], axis=1)
del to_keep

#create counts by year
copy_raw = copy[['doc_id_new', 'year'] + [x for x in copy if "comp_raw_" in x]]
copy_raw = pd.melt(copy_raw, id_vars=['doc_id_new', 'year'], value_name='rating')
copy_raw = copy_raw[pd.notnull(copy_raw['rating'])]
raw_year_counts = pd.DataFrame(copy_raw.groupby(['year', 'variable']).size()).reset_index()
raw_year_counts.columns = ['year', 'competency', 'count']
raw_year_counts = raw_year_counts.set_index(['competency', 'year'])['count'].unstack().reset_index()

copy_merged = copy[['doc_id_new', 'year'] + [x for x in copy if "comp_merged_" in x]]
copy_merged = pd.melt(copy_merged, id_vars=['doc_id_new', 'year'], value_name='rating')
copy_merged = copy_merged[pd.notnull(copy_merged['rating'])]
merged_year_counts = pd.DataFrame(copy_merged.groupby(['year', 'variable']).size()).reset_index()
merged_year_counts.columns = ['year', 'competency', 'count']
merged_year_counts = merged_year_counts.set_index(['competency', 'year'])['count'].unstack().reset_index()
del copy, copy_raw, copy_merged

#get overlapping matrix and write a raw and percent version
comp_vars = [x for x in master_clean.columns if "comp_raw_" in x]
overlaps_raw = overlapMatRaw(master_clean.rename({'doc_id_new':'doc_id'}, axis=1)[['doc_id'] + comp_vars])

comp_vars = [x for x in master_clean.columns if "comp_merged_" in x]
overlaps_merged_raw = overlapMatRaw(master_clean.rename({'doc_id_new':'doc_id'}, axis=1)[['doc_id'] + comp_vars])


############################################
#  Write Information to excels
############################################


#create counts of the merged variables
master_cleanCounts = pd.DataFrame(len(master_clean) - master_clean.apply(lambda x: x.isnull().sum(), axis='rows'))
master_cleanCounts = master_cleanCounts.reset_index()
master_cleanCounts.columns = ['variable', 'count']

master_purposeCounts = pd.DataFrame(master_clean['purpose_clean'].value_counts())
master_purposeCounts = master_purposeCounts.loc[['hire no hire', 'promotion',
                                                 'due diligence', 'candidate',
                                                 'go no go', 'general assessment',
                                                 'wrong extraction', 'other']]
master_purposeCounts = master_purposeCounts.reset_index()
master_purposeCounts.columns = ['purpose_clean', 'count']
master_purposeCounts['description'] = ['hiring an individual', 
                                       'promoting an individual',
                                       'interview of key individual before possible investment or m&a', 
                                       'evaluation of individual, unclear if new hire or promotion', 
                                       'evaluation of individual, unclear if part of investment or m&a',
                                       'evaluation of individual, unclear if candidate is being considered for another role',
                                       'something went bad while extracting the purpose',
                                       'code did not classify']

# CompanyFinalCounts = master_clean[["company_clean", "company_raw"]].copy()
# CompanyFinalCounts = CompanyFinalCounts.groupby('company_clean', as_index=False).count()
# CompanyFinalCounts.columns = ['company_clean', 'count']
# CompanyFinalCounts = CompanyFinalCounts.merge(master_clean[['company_clean', 'company_flag']].drop_duplicates(), how='left')

TitleFinalCounts = {}
for titles in master_clean['title_clean']:
    if pd.isnull(titles):
        continue
    titles = titles.split(" AND ")
    for t in titles:
        if t in TitleFinalCounts:
            TitleFinalCounts[t] += 1
        else:
            TitleFinalCounts[t] = 1 
TitleFinalCounts = pd.DataFrame(TitleFinalCounts.items(), columns = ['title_clean', 'count'])
TitleFinalCounts = TitleFinalCounts.sort_values('title_clean')

PrepByFinalCounts={}
for x in master_clean['prepared_by_clean']:
    if pd.notnull(x):
        people = x.split(" AND ")
        for p in people:
            if p not in PrepByFinalCounts:
                PrepByFinalCounts[p] = 1
            else:
                PrepByFinalCounts[p] += 1
del x, people, p
PrepByFinalCounts = pd.DataFrame(PrepByFinalCounts.items(), columns = ["prepared_by_clean", "count"])
PrepByFinalCounts = PrepByFinalCounts.sort_values('prepared_by_clean')

GenderFinalCounts = master_clean[['doc_id_new','gender', 'gender_method']].groupby(['gender_method', 'gender'], as_index=False).count()
GenderFinalCounts.columns = ['method','gender', 'count']

CollegesFinalCounts={}
for x in master_clean['college_raw']:
    if pd.notnull(x):
        colleges = x.split(" AND ")
        for c in colleges:
            if c not in CollegesFinalCounts:
                CollegesFinalCounts[c] = 1
            else:
                CollegesFinalCounts[c] += 1
del x, colleges, c
CollegesFinalCounts = pd.DataFrame(CollegesFinalCounts.items(), columns = ["college_raw", "count"])
CollegesFinalCounts = CollegesFinalCounts.sort_values('college_raw')

UndergradFinalCounts={}
for x in master_clean['undergrad_clean']:
    if pd.notnull(x):
        colleges = x.split(" AND ")
        for c in colleges:
            if c not in UndergradFinalCounts:
                UndergradFinalCounts[c] = 1
            else:
                UndergradFinalCounts[c] += 1
del x, colleges, c
UndergradFinalCounts = pd.DataFrame(UndergradFinalCounts.items(), columns = ["undergrad_clean", "count"])
UndergradFinalCounts = UndergradFinalCounts.sort_values('undergrad_clean')
UndergradFinalCounts = UndergradFinalCounts.merge(master_clean[['undergrad_clean', 'undergrad_ivy']].drop_duplicates(), how='left')
UndergradFinalCounts['undergrad_ivy'] = UndergradFinalCounts['undergrad_ivy'].fillna(0)

MBAFinalCounts={}
for x in master_clean['mba_clean']:
    if pd.notnull(x):
        colleges = x.split(" AND ")
        for c in colleges:
            if c not in MBAFinalCounts:
                MBAFinalCounts[c] = 1
            else:
                MBAFinalCounts[c] += 1
del x, colleges, c
MBAFinalCounts = pd.DataFrame(MBAFinalCounts.items(), columns = ["mba_clean", "count"])
MBAFinalCounts = MBAFinalCounts.sort_values('mba_clean')
MBAFinalCounts = MBAFinalCounts.merge(master_clean[['mba_clean', 'mba_top14']].drop_duplicates(), how='left')
MBAFinalCounts['mba_top14'] = MBAFinalCounts['mba_top14'].fillna(0)

CompMergers = pd.read_excel(var_path + 'mergers.xlsx', sheet_name="competency_complete")
CompTemplate = pd.read_excel(var_path + 'keywords.xlsx', sheet_name="competency")
CompTemplate = CompTemplate.drop('main',axis=1).sort_values('competency')

CompTemplateCounts = master_clean[['doc_id_new','comp_template']].groupby(['comp_template'], as_index=False).count()
CompTemplateCounts.columns = ['template', 'count']

ScorecardResults = pd.read_excel(out_local + "scorecard/clustering/scorecard_evalresults.xlsx")

def split_topic(topic, num):
    split = topic.split("_")
    if len(split)==1:
        split += split
    return split[num]

ScorecardKeys = pd.read_excel(out_local + "scorecard/clustering/scorecard_finalcleanCounts.xlsx")
ScorecardKeys = ScorecardKeys.drop(['count'], axis=1)
ScorecardFinalCounts = master_clean[['doc_id_new', 'doc_id_old'] + [x for x in master_clean.columns if re.search("^sc.*topic$", x)]]
ScorecardFinalCounts.columns = ['doc_id_new', 'doc_id_old'] + ["sc_topic" + str(x) for x in range(1, 19)]
ScorecardFinalCounts = pd.wide_to_long(ScorecardFinalCounts, "sc_topic", ["doc_id_new", 'doc_id_old'], "order").reset_index()
ScorecardFinalCounts = ScorecardFinalCounts[[pd.notnull(x) for x in ScorecardFinalCounts['sc_topic']]]
ScorecardFinalCounts = ScorecardFinalCounts.drop_duplicates(subset=['doc_id_new', 'doc_id_old', 'sc_topic'], keep='first')
ScorecardFinalCounts = ScorecardFinalCounts[['doc_id_new','sc_topic']].groupby(['sc_topic'], as_index=False).count()
ScorecardFinalCounts.columns = ['sc_topic', 'num_docs']
ScorecardFinalCounts['topic'] = ScorecardFinalCounts['sc_topic'].apply(lambda x: split_topic(x, 0))
ScorecardFinalCounts['subtopic'] = ScorecardFinalCounts['sc_topic'].apply(lambda x: split_topic(x, 1))
ScorecardFinalCounts = ScorecardFinalCounts.merge(ScorecardKeys)

#write the ratings and counts to local
with pd.ExcelWriter(out_local + "extractions_merged_anonymized_deduplicated.xlsx") as writer:
    master_clean.to_excel(writer, sheet_name="Values", index=False)
    master_cleanCounts.to_excel(writer, sheet_name="Counts", index=False)
    # CompanyFinalCounts.to_excel(writer, sheet_name="CompanyCounts", index=False)
    TitleFinalCounts.to_excel(writer, sheet_name="TitleCounts", index=False)
    PrepByFinalCounts.to_excel(writer, sheet_name="PrepbyCounts", index=False)
    master_purposeCounts.to_excel(writer, sheet_name="PurposeCounts", index=False)
    GenderFinalCounts.to_excel(writer, sheet_name="GenderCounts", index=False)
    CollegesFinalCounts.to_excel(writer, sheet_name="CollegeCounts", index=False)
    UndergradFinalCounts.to_excel(writer, sheet_name="UndergradCounts", index=False)
    MBAFinalCounts.to_excel(writer, sheet_name="MBACounts", index=False)
    CompTemplate.to_excel(writer, sheet_name="CompTemplates", index=False)
    CompTemplateCounts.to_excel(writer, sheet_name="CompTemplateCounts", index=False)
    CompMergers.to_excel(writer, sheet_name="CompMergers", index=False)
    overlaps_raw.to_excel(writer, sheet_name="CompRawOverlaps")
    raw_year_counts.to_excel(writer, sheet_name="CompRawCountsYear", index=False)
    overlaps_merged_raw.to_excel(writer, sheet_name="CompMergedOverlaps")
    merged_year_counts.to_excel(writer, sheet_name="CompMergedCountsYear", index=False)
    ScorecardResults.to_excel(writer, sheet_name="ScorecardTrainingResults", index=False)
    ScorecardFinalCounts.to_excel(writer, sheet_name="ScorecardTopics", index=False)
del writer

