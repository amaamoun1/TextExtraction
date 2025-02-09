# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 16:06:27 2021

@author: Asser.Maamoun
"""

import os
import re
import pandas as pd
import datetime
import dateutil
import numpy as np
import openpyxl
import sys

sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/scraping')

from helper_functions_career import find_tenure, get_hyperlinks, clean_excel_date, \
    clean_company, find_hiring_dates, find_tenure, was_will_position

path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping"



#############################################################################
#    Find out who was successfully scraped
#############################################################################

#this was the scraping with name + university
scrape01 = pd.read_excel(path_out + "/03 evaluations/step1_university_checked.xlsx")
results01 = pd.read_csv(path_out + "/01 university_company_scrape/results_ceos_cfos.csv")
results01['doc_id_old'] = results01['docid'].apply(lambda x: int(re.split("_|\\.", x)[1]))
results01['doc_id_new'] = results01['docid'].apply(lambda x: int(re.split("_|\\.", x)[3]))
results01 = results01.rename({'url': 'linkedin_url'}, axis=1)
scrape01 = scrape01.merge(results01[['doc_id_old', 'doc_id_new', 'linkedin_url']])

scrape01b = pd.read_excel(path_out + "/01 university_company_scrape/extractions_other_tocompare_withautocheck.xlsx")
results01b = pd.read_csv(path_out + "/01 university_company_scrape/results_other.csv")
results01b['doc_id_old'] = results01b['docid'].apply(lambda x: int(re.split("_|\\.", x)[1]))
results01b['doc_id_new'] = results01b['docid'].apply(lambda x: int(re.split("_|\\.", x)[3]))
results01b = results01b.rename({'url': 'linkedin_url'}, axis=1)
scrape01b = scrape01b.merge(results01b[['doc_id_old', 'doc_id_new']])

scrape01b = scrape01b.rename({'auto_correct': 'hired'}, axis=1)
scrape01b['correct'] = 1


#this was the scraping with name + most recent job
scrape02 = pd.read_excel(path_out + "/03 evaluations/step2_career_checked.xlsx")
results02 = pd.read_csv(path_out + "/02 career_onlyname_scrape/results_ceos_cfos.csv")
results02['doc_id_old'] = results02['docid'].apply(lambda x: int(re.split("_|\\.", x)[1]))
results02['doc_id_new'] = results02['docid'].apply(lambda x: int(re.split("_|\\.", x)[3]))
results02 = results02.rename({'url': 'linkedin_url'}, axis=1)
scrape02 = scrape02.merge(results02[['doc_id_old', 'doc_id_new', 'linkedin_url']])

scrape02b = pd.read_excel(path_out + "/02 career_onlyname_scrape/extractions_other_tocompare_withautocheck.xlsx")
results02b = pd.read_csv(path_out + "/02 career_onlyname_scrape/results_other.csv")
results02b['doc_id_old'] = results02b['docid'].apply(lambda x: int(re.split("_|\\.", x)[1]))
results02b['doc_id_new'] = results02b['docid'].apply(lambda x: int(re.split("_|\\.", x)[3]))
results02b = results02b.rename({'url': 'linkedin_url'}, axis=1)
scrape02b = scrape02b.merge(results02b[['doc_id_old', 'doc_id_new']])

scrape02b = scrape02b.rename({'auto_correct': 'hired'}, axis=1)
scrape02b['correct'] = 1


#this was the scraping after looking for people on linkedin that we ce couldnt scrape initially
scrape03 = pd.read_excel(path_out + "/04 manual_search/extractions_full.xlsx")
file1 = r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\04 manual_search\manual_search_yann.xlsx"
file2 = r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\04 manual_search\manual_search_neil.xlsx"
manual_checked1 = pd.read_excel(file1)
manual_checked1 = manual_checked1[manual_checked1['assigned']=="Yann"]
manual_checked2 = pd.read_excel(file2)
manual_checked2 = manual_checked2[manual_checked2['assigned']=="Neil"]
wb = openpyxl.load_workbook(file2)
ws = wb['Sheet1']
manual_checked2['linkedin_link'] = get_hyperlinks(ws, 16, 497)
results03 = manual_checked1.append(manual_checked2)
results03 = results03.rename({'linkedin_link':'linkedin_url', 'linkedin_company':'company_linkedin'}, axis=1)
scrape03 = scrape03.merge(results03)
scrape03['correct'] = 1


#combine and keep those that are correct
scrape_combined = scrape01.append(scrape02).append(scrape03)
scrape_combined = scrape_combined.append(scrape01b).append(scrape02b)
scrape_success = scrape_combined[scrape_combined['correct']==1].copy()
scrape_success = scrape_success[scrape_success['hired']!="."].copy()

#add variables for previous or future ceo/cfo experience
scrape_success['past_ceo'], scrape_success['past_cfo'], scrape_success['future_ceo'], scrape_success['future_cfo'] = \
    zip(*scrape_success.apply(lambda row: was_will_position(row['linkedin_info'], \
                                          row['date_clean'], company_linkedin=row['company_linkedin']) , axis=1))

#add a variable for tenure
scrape_hired = scrape_success[scrape_success['hired']==1]
scrape_hired['hired_start'], scrape_hired['hired_end'] = zip(*scrape_hired.apply( \
                                            lambda row: find_hiring_dates(row['linkedin_info'], \
                                            row['company_linkedin'], row['title_clean']) , axis=1))
scrape_hired['tenure_before'], scrape_hired['tenure_after'] = zip(*scrape_hired.apply( \
                                            lambda row: find_tenure(row['date_clean'], \
                                            row['hired_start'], row['hired_end']) , axis=1))


scrape_nothired = scrape_success[scrape_success['hired']==0]
scrape_success = scrape_hired.append(scrape_nothired)
scrape_success = scrape_success[['doc_id_old', 'doc_id_new', 'linkedin_url', 'linkedin_info', 'company_linkedin', 
                               'hired', 'hired_start', 'hired_end', 'tenure_before',
                               'tenure_after', 'flag', 'past_ceo', 
                               'past_cfo', 'future_ceo', 'future_cfo']]
scrape_success.to_excel(path_out + "\scrape_success.xlsx", index=False)


#############################################################################
#    output those people without a successfully scaped linkedin
#############################################################################


def is_ceo_cfo(titles):
    ceo = 0
    for title in titles.split(" AND "):
        if ("ceo" not in title) and ("cfo" not in title):
            continue
        if re.match("(ceo succession|deputy|division|region|assistant|office of)", title):
            continue
        ceo=1
    return ceo

#read in extractions and select pre or post 2012
candidates = pd.read_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\extractions_merged.xlsx")
has_factors = pd.read_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\has_factors.xlsx")

#only search relevant people, no duplicates!
candidates = candidates.replace(np.nan, '', regex=True)
candidates = candidates[candidates['is_duplicate']==0]
candidates = candidates[candidates['candidate_flag']!=1]

#designate those that are ceos
candidates['ceo_cfo'] = candidates['title_clean'].apply(is_ceo_cfo)
candidates = candidates[candidates['ceo_cfo']==1]

#set up variables for scraping loop
candidates = candidates[["doc_id_old", "doc_id_new", "candidate_firstname", 
                         "candidate_lastname", "date_clean", "company_clean", 
                         "title_clean", "undergrad_clean", "mba_clean",  
                         "career_clean", "career_clean_olddata"]]
candidates = candidates.reset_index(drop=True)

#those that failed are ceos/cfos that are not in success
scrape_fail = candidates.merge(scrape_success[['doc_id_old', 'doc_id_new']], how='left', indicator=True)
scrape_fail = scrape_fail[scrape_fail['_merge']=='left_only']
scrape_fail = scrape_fail.drop('_merge', axis=1)
scrape_fail = scrape_fail.merge(has_factors, how='left')
scrape_fail['has_factors'] = scrape_fail['has_factors'].fillna(0) #the four people with NA are duplicates


def extract_filename(filepath):
    filepath = filepath.replace("\\", "/")
    groups = re.split("[\/]", filepath)
    return groups[-1]

def extract_folder(filepath):
    filepath = filepath.replace("\\", "/")
    groups = re.split("[\/]", filepath)
    return groups[-2]

docid_mapping = pd.read_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\docid_mapping.xlsx")
docid_mapping = docid_mapping[['doc_id', 'docx_path']]
docid_mapping.columns = ['doc_id_new', 'docx_path']
docid_mapping['folder'] = docid_mapping['docx_path'].apply(extract_folder)
docid_mapping['filename'] = docid_mapping['docx_path'].apply(extract_filename)
docid_mapping = docid_mapping.drop('docx_path', axis=1)
scrape_fail = scrape_fail.merge(docid_mapping, how='left')

old = pd.read_excel(path_out + "/04 manual_search\scrape_fail_manualcheck.xlsx")
old['old'] = 1
scrape_fail = scrape_fail.merge(old[['doc_id_old', 'doc_id_new', 'old']], on = ['doc_id_old', 'doc_id_new'], how='left')

sum(scrape_fail['has_factors'])
scrape_fail[scrape_fail['has_factors']==1].to_excel(path_out + "/04 manual_search\scrape_fail_manualcheck.xlsx", index=False)



#############################################################################
#    output those people without a linkedin after manual linkedin checking
#############################################################################


file1 = r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\04 manual_search\manual_search_yann.xlsx"
file2 = r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\scraping\04 manual_search\manual_search_neil.xlsx"

manual_checked1 = pd.read_excel(file1)
manual_checked1 = manual_checked1[manual_checked1['assigned']=="Yann"]
manual_checked2 = pd.read_excel(file2)
manual_checked2 = manual_checked2[manual_checked2['assigned']=="Neil"]
manual = manual_checked1.append(manual_checked2)

manual_fail1 = manual[manual['linkedin_link']=="."]
manual_fail2 = manual[(manual['linkedin_link']!=".") & (manual['hired']==".")]
manual_fail = manual_fail1.append(manual_fail2)
manual_fail = manual_fail[manual_fail.columns[:14]]
manual_fail.to_excel(path_out + "/no_linkedin.xlsx", index=False)


#############################################################################
#    merge in the variables from the manual checking (outside of linkedin)
#############################################################################

def format_date(date):
    if pd.isnull(date) or date=="" or date==".":
        return np.nan
    date = date[:min(10, len(date))]
    return date


    
        

#load files
career_manual = pd.read_excel(path_out + "\manual_search2_neil_3.xlsx", dtype={'date_clean': str})
wb = openpyxl.load_workbook(path_out + "\manual_search2_neil_3.xlsx")
ws = wb['Sheet1']

#clean hyperlinks
career_manual['linkedin_link'] = get_hyperlinks(ws, 16, 401)
career_manual['businessweek_link'] = get_hyperlinks(ws, 17, 401)
career_manual['other_link'] = get_hyperlinks(ws, 18, 401)
career_manual['other links'] = get_hyperlinks(ws, 19, 401)
career_manual = career_manual.rename({'other_link':'other_link_1', 'other links': 'other_link_2'}, axis=1)

career_not_found = career_manual[career_manual['hired']=="."].copy()
career_not_found = career_not_found[pd.notnull(career_not_found['candidate_firstname'])]
career_not_found = career_not_found[pd.notnull(career_not_found['candidate_lastname'])]
career_not_found = career_not_found[pd.notnull(career_not_found['company_clean'])]
career_not_found = career_not_found[pd.notnull(career_not_found['date_clean'])]
career_not_found = career_not_found.drop(["folder", "filename", "has_factors", "assigned", "career_clean_olddata", "linkedin_link", "businessweek_link", "other_link_1", "other_link_2"], axis=1)
career_not_found = career_not_found.replace(to_replace=".", value=np.nan)
career_not_found.to_excel(path_out + "/career_manual_not_found.xlsx", index=False)


#clean "."
career_manual = career_manual.replace(to_replace=".", value=np.nan)

#clean dates
career_manual['date_clean'] = career_manual['date_clean'].apply(format_date)
for x in ["P" + str(i) + "_start" for i in range(1,12)] + ["P" + str(i) + "_end" for i in range(1,12)]:
    career_manual[x] = career_manual[x].apply(clean_excel_date)
    

#combine the position variables to create a single career_info variable
career_manual['career_info'] = ''
for i in range(1,12):
    career_manual['career_info'] = career_manual['career_info'] + \
        career_manual['P' + str(i) + '_start'].fillna('none').astype(str) + " - " + \
        career_manual['P' + str(i) + '_end'].fillna('none').astype(str) + " || " + \
        career_manual['P' + str(i) + '_company'].fillna('').astype(str) + " || " + \
        career_manual['P' + str(i) + '_title'].fillna('').astype(str) + " AND\n"
career_manual['career_info'] = career_manual['career_info'].apply(lambda x: re.sub("none \\- none \\|\\|  \\|\\|  AND\\n", "", x))
career_manual['career_info'] = career_manual['career_info'].apply(lambda x: x.strip().strip(" AND"))



#add variables for previous or future ceo/cfo experience
career_manual['past_ceo'], career_manual['past_cfo'], career_manual['future_ceo'], career_manual['future_cfo'] = \
    zip(*career_manual.apply(lambda row: was_will_position(row['career_info'], \
                                          row['date_clean'], hired_position=row['hired_position']) , axis=1))


#add a variable for tenure
career_manual_hired = career_manual[career_manual['hired']==1]
career_manual_hired['hired_start'], career_manual_hired['hired_end'] = zip(*career_manual_hired.apply( \
                                            lambda row: find_hiring_dates(row['career_info'], \
                                            hired_position = row['hired_position']) , axis=1))
career_manual_hired['tenure_before'], career_manual_hired['tenure_after'] = zip(*career_manual_hired.apply( \
                                            lambda row: find_tenure(row['date_clean'], \
                                            row['hired_start'], row['hired_end']) , axis=1))
    
def find_hired_company(row):
    try:
        return row["P" + str(row["hired_position"]) + "_company"]
    except:
        print("FAILED:", row['hired_position'])
        return np.nan
        
career_manual_hired['hired_company'] = career_manual_hired.apply(find_hired_company, axis=1)


career_manual_nothired = career_manual[career_manual['hired']==0]
career_manual_final = career_manual_hired.append(career_manual_nothired)
career_manual_final = career_manual_final[['doc_id_old', 'doc_id_new', 'linkedin_link', 'businessweek_link',
                                             'other_link_1', 'other_link_2', 'career_info', 'hired_company', 
                               'hired', 'hired_start', 'hired_end', 'tenure_before',
                               'tenure_after', 'past_ceo', 
                               'past_cfo', 'future_ceo', 'future_cfo']]
career_manual_final.to_excel(path_out + "/career_manual_final.xlsx", index=False)

    
#merge the information into the master dataset
scrape_success = pd.read_excel(path_out + "\scrape_success.xlsx")
scrape_success = scrape_success.rename({'company_linkedin':'hired_company', 
                                        'linkedin_url':'linkedin_link', 
                                        'linkedin_info':'career_info'}, axis=1)


scrape_final = career_manual_final.append(scrape_success)
scrape_final.to_excel(path_out + "\career_full_final.xlsx", index=False)



#select the the companies that we need to manually check
to_find = scrape_final[scrape_final['hired']==1]
to_find = to_find[to_find['doc_id_old']==-1]












