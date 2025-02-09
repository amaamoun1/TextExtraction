# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 19:08:27 2020

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



#############################################################################
#    Import Data
#############################################################################

TitleFinalCounts = pd.read_excel(out_local + "/titles/TitleFinalCounts.xlsx")
master_clean = pd.read_excel(out_local + "extractions_merged.xlsx", sheet_name = "Values")


#############################################################################
#    Find number of Teams
#############################################################################


#find rows with clean dates AND csuite or ceo/cfo
title_csuite = [x for x in TitleFinalCounts['title_clean'] if (re.search("^c", x)!=None) & (x!= "cofounder")]
title_ceocfo = ["ceo", "cfo"]
track_csuite = []
track_ceocfo = []
for i, row in master_clean.iterrows():
    csuite = False
    ceocfo = False
    curr = row['title_clean']
    if pd.notnull(row['date_clean']) and pd.notnull(curr):
        for x in curr.split(' AND '):
            if x in title_csuite:
                csuite = True
            if x in title_ceocfo:
                ceocfo = True
    track_csuite.append(csuite)
    track_ceocfo.append(ceocfo)
subset_csuite = master_clean[track_csuite].copy()
subset_ceocfo = master_clean[track_ceocfo].copy()
del i, row, csuite, ceocfo, x, curr, track_csuite, track_ceocfo


#find companies that have atlest 2 ceo or cfo candidates
subset_ceocfo_companies = subset_ceocfo.groupby('company_clean', as_index=False)['doc_id_new'].count()
subset_ceocfo_companies = subset_ceocfo_companies[subset_ceocfo_companies['doc_id_new']>1]
subset_ceocfo_companies = subset_ceocfo_companies[['company_clean']]
subset_ceocfo = subset_ceocfo.merge(subset_ceocfo_companies, how="right")
print("found:", len(subset_ceocfo_companies), "companies")


#find companiesw here we have both ceo and cfo interviews
team_number = 1
team_dict = {} #dictionary of docid - team_number
for company in subset_ceocfo_companies['company_clean']:
    rows = subset_ceocfo[subset_ceocfo['company_clean']==company].copy()
    new_ids = list(rows['doc_id_new'])
    old_ids = list(rows['doc_id_old'])
    unique_ids = [str(new_ids[i]) + "_" + str(old_ids[i]) for i in range(len(new_ids))]
    titles = " AND ".join(list(rows['title_clean']))
    titles = titles.split(" AND ")
    if len(unique_ids) > 1 and "ceo" in titles and "cfo" in titles: #teams need at least 2 people from diff disciplines
        for x in unique_ids: #add the docs to the team dict
            team_dict[x] = team_number
        team_number += 1
team_df = pd.DataFrame(team_dict.items(), columns=['doc_id', 'ceo_cfo_team'])
team_df.to_excel(out_local + "teams/ceo_cfo_teams.xlsx", index=False)
        


#find teams hired within x amount of days...not necessary
team_number = 1
team_dict = {} #dictionary of docid - team_number
for company in subset_ceocfo_companies['company_clean']:
    doc_ids = []
    dates = []
    titles = []
    rows = subset_ceocfo[subset_ceocfo['company_clean']==company].copy()
    rows = rows.sort_values(['date_clean'])
    for i, row in rows.iterrows():
        #grab title and doc_id
        curr_title = row['title_clean']
        curr_docid = row['doc_id']
        #turn date into datetime object
        curr_date =  [int(x) for x in row['date_clean'].split("-")]
        y = curr_date[0]
        m = curr_date[1]
        if len(curr_date)==2:
            d = 15
        else:
            d = curr_date[2]
        curr_date = date(y,m,d)
        
        if len(dates)==0: #check starting condition
            dates.append(curr_date)
            titles.append(curr_title)
            doc_ids.append(curr_docid)
        else:
            #check if we need to start a new team
            diff_days = (curr_date - dates[-1]).days
            if diff_days > 30: #this closes the last team
                titles_joined = " ".join(titles)
                if len(doc_ids) > 1 and "ceo" in titles_joined and "cfo" in titles_joined: #teams need at least 2 people from diff disciplines
                    for x in doc_ids: #add the docs to the team dict
                        team_dict[x] = team_number
                    team_number += 1
                #restart team
                doc_ids = [curr_docid]   
                dates = [curr_date]
                titles = [curr_title]
            else: #if the team is still open just append
                dates.append(curr_date)
                titles.append(curr_title)
                doc_ids.append(curr_docid)
del dates, titles, rows, i, row, curr_date, y, m, d, curr_title, diff_days
del curr_docid, doc_ids, x, company, titles_joined




