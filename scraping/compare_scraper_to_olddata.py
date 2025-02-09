# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 14:46:30 2021

@author: Asser.Maamoun
"""
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linking')

from fuzzy_merge_functions import clean_company

import numpy as np
import pandas as pd
import xlwings as xw
import re

#############################################################################
#    Helper functions
#############################################################################

# extracts the old docid given the oldid_XXX_newid_XXX string
def extract_docidold(x):
    return int(re.search("_([-\\d]+)_", x).group(1))

def extract_docidnew(x):
    return int(re.search("([-\\d]+)$", x).group(1))

# extracts linkedin profile id from url
def extract_profileid(x):
    if x=="":
        return "none"
    match = re.search("profile\/(\\d+)", x)
    if match:
        return match.group(1)
    match = re.search("profile\/view\?id=(\\d+)", x)
    if match:
        return match.group(1)
    match = re.search("people\/show\/(\\d+)", x)
    if match:
        return match.group(1)
    match = re.search("linkedin\.com\/pub\/[^\/]+\/([^\/]+)\/([^\/]+)\/([^\/]+)", x)
    if match:
        return match.group(3) + match.group(2) + match.group(1)
    print(x)
    return "error"

#given that the old data has two linkedin links, pick the second one when available
def reconcile_profiles(p1, p2):
    if p1=="none":
        return p2
    elif p2=="none":
        return p1
    elif p1==p2:
        return p1
    else:
        print(p1, p2)
        return p2

#assigns how similar or how different the profiles are
def check_profiles(pscrape, pold):
    if pscrape==pold:
        if pscrape=="none":
            return "same_none"
        else:
            return "same_prof"
    else:
        if pscrape=="none":
            return "diff_noscrape"
        elif pold=="none":
            return "diff_noold"
        else:
            return "diff_prof"

#checks if the scraped individuals has similar positions to the old data
def same_positions(row):
    found = 0
    for oldcol in [x for x in row.index if pd.notnull(re.search("^company_[0-9]+_old$", x))]:
        pos_old = row[oldcol]
        if pos_old=="":
            continue
        for newcol in [x for x in row.index if pd.notnull(re.search("^company_[0-9]+$", x))]:
            pos_new = row[newcol]
            # print(pos_old, pos_new)
            if pos_new=="":
                continue
            if (pos_old in pos_new) or (pos_new in pos_old):
                found+=1
    return found
            

#############################################################################
#    Import Data and Basic cleaning
#############################################################################
    
path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping/v5"

############################################
#  Clean scraped individuals
############################################
    
# prep the scraped data
scrape = pd.read_csv(path_out + "/results.csv")
scrape = scrape.drop(['i', 'start_time'], axis=1)
scrape = scrape.replace(np.nan, '', regex=True)
scrape['doc_id_old'] = scrape['docid'].apply(extract_docidold)
scrape['doc_id_new'] = scrape['docid'].apply(extract_docidnew)
scrape['profile'] = scrape['url'].apply(extract_profileid)
# scrape = scrape[['doc_id_old', 'doc_id_new', 'firstname', 'lastname', 'schools','schools_type', 'num_results', 'is_namematch', 'url', 'profile']]
scrape = scrape[['doc_id_old', 'doc_id_new', 'firstname', 'lastname', 'company', 
                 'company_flag', 'schools','schools_type', 'keywords',
                 'search_type', 'num_results', 'is_namematch', 'url', 'profile']]

# grab the extractions
extract = pd.read_excel(path_out + "/extractions_wide.xlsx")
extract = extract.replace(np.nan, '', regex=True)
for col in [x for x in extract.columns if "company" in x]:
    extract[col] = extract[col].apply(clean_company)
scrape = scrape.merge(extract, how='left', on=['doc_id_old', 'doc_id_new'])
scrape = scrape.replace(np.nan, '', regex=True)


############################################
#  Clean old data
############################################

# prep the old data
wb = xw.Book(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\linking_pastdata\Post Current.xlsx")
sheet = wb.sheets["candidates.052512.csv"]
old = sheet['A1:DS3027'].options(pd.DataFrame, index=False, header=True, dtype=str).value

old = old.iloc[:,[8,13,56,60,63,66,69,75,78,83,86,91,94,99,102,118,121]]
old.columns = ["doc_id_old", "url1", "hired", "title_0", "company_0", "title_1", "company_1",
               "title_2", "company_2", "title_3", "company_3", "title_4", "company_4",
               "title_5", "company_5", "url2", "successful"]

old = old[[pd.notnull(x) for x in old['doc_id_old']]]
old = old[old['doc_id_old'] != "ID"]
old['doc_id_old'] = old['doc_id_old'].astype(float).astype(int)
old = old.replace(np.nan, '', regex=True)
old = old.replace(".", "")
for col in [x for x in old.columns if "company" in x]:
    old[col] = old[col].apply(clean_company)
    
old['profile1'] =old['url1'].apply(extract_profileid)
old['profile2'] =old['url2'].apply(extract_profileid)
old['profile'] = old.apply(lambda row: reconcile_profiles(row['profile1'], row['profile2']), axis=1)
old = old[["doc_id_old", "url1", "url2", "profile1", "profile2", "profile",
           "title_0", "title_1", "title_2", "title_3", "title_4", "title_5",
           "company_0", "company_1", "company_2", "company_3", "company_4", "company_5"]]
old.columns = ['doc_id_old'] +[x + "_old" for x in old.columns[1:]]


############################################
#  Merge and check overlap
############################################


# merge the old data to the new data
check = scrape.merge(old, how='inner', on=['doc_id_old'], suffixes=['_scrape', '_old'])
check['same_profile'] = check.apply(lambda row: check_profiles(row['profile'], row['profile_old']), axis=1)
check['same_positions'] = check.apply(same_positions, axis=1)
check['has_same_positions'] = check['same_positions'].apply(lambda x: int(x>0))
check.to_csv(path_out + "/check_vs_old.csv", index=False)


#check overlap between same_profile and same_positions
check.groupby(['same_profile', 'has_same_positions']).size().reset_index(name="Count")


