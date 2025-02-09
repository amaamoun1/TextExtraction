# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 19:56:59 2021

@author: Asser.Maamoun
"""

import os
import re
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import dateutil


################
## PARAMETERS ##
################


search_type = "career"
ceos = 0

#############################################################################
#    set up information to loop over
#############################################################################

#set the output folder
if search_type=="university":
    path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping/01 university_company_scrape"
elif search_type=="career":
    path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping/02 career_onlyname_scrape"
elif search_type=="manual":
    path_out = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping/04 manual_search"

#select the proper results file
if ceos==1:
    results_df = pd.read_csv(path_out + "/results_ceo_cfos.csv")
    out_prefix = "extractions"
else:
    results_df = pd.read_csv(path_out + "/results_other.csv")
    out_prefix = "extractions_other"

#select the proper files
results_df = results_df[results_df['num_results']>0]
files = os.listdir("C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping/htmls/")
to_extract = []
for f in files:
    #get docid from file name
    docid = f[:-5]
    
    #check if document is in the right group
    curr = results_df[results_df['docid']==docid]
    if len(curr)>0:
        to_extract.append(f)
files = to_extract
del curr, f, to_extract

#############################################################################
#    Loop over all htmls and extract information
#############################################################################

#iterate over htmls
extractions = []
docnum = 0
for f in files:
    docnum+=1
    if docnum%100==1:
        print(docnum, datetime.datetime.now().strftime('%H:%M:%S'))
    
    #get docid from file name
    name_split = re.split("_|\\.", f)
    doc_id_old = int(name_split[1])
    doc_id_new = int(name_split[3])
    
    #make a bs object
    with open("C:/Users/Asser.Maamoun/Documents/TextExtraction/output/scraping/htmls/" + f, 'r') as infile: 
        html_string = infile.read()
    soup = BeautifulSoup(html_string, 'html.parser')
    
    #extracts name
    try:
        name = soup.select("div.profile-info > h1.searchable")[0].text.strip()
    except IndexError:
        extractions.append([doc_id_old, doc_id_new, "out_of_network", "", "", "", "", "", "", "", ""])
        continue
    info_vars = [doc_id_old, doc_id_new, name]
    
    #extracts experiences
    num = 0
    experiences = soup.select("div#profile-experience > div.module-body > ul >li > div.position-header")
    for item in experiences:
        num+=1
        title = item.select("h4.searchable")[0].text.strip()
        company = item.select("h5.searchable")[0].text.strip()
        date_range = item.select("p.date-range")[0].find(text=True, recursive=False).strip()
        start_date = date_range.split("\\xe2\\x80\\x93")[0].strip()
        try:
            end_date = date_range.split("\\xe2\\x80\\x93")[1].strip()
        except IndexError:
            end_date = start_date
        try:
            duration = item.select("p.date-range > span.duration")[0].text.strip()
        except IndexError:
            duration = ""
        try:
            location = item.select("p.date-range > span.location")[0].text.strip()
        except IndexError:
            location = ""
        position_results = info_vars + ["position", num, title, company, start_date, end_date, duration, location]
        extractions.append(position_results)
        
    #extracts education
    num = 0
    education = soup.select("div#profile-education > div.module-body > ul >li > div.position-header")
    for item in education:
        num+=1
        school = item.select("h4.searchable")[0].text.strip()
        try:
            degree = item.select("h5.searchable")[0].text.strip()
        except IndexError:
            degree=""
        position_results = info_vars + ["education", num, school, degree, "", "", "", ""]
        extractions.append(position_results)
        

extractions_df = pd.DataFrame(extractions, columns=['doc_id_old', 'doc_id_new', 'name', 'type', 'num', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6'])
extractions_df.to_excel(path_out + "/" + out_prefix + ".xlsx", index=False)


#############################################################################
#    Convert to wide format
#############################################################################

extractions_df = pd.read_excel(path_out + "/" + out_prefix + ".xlsx")
len(extractions_df.drop_duplicates(subset=['doc_id_new', 'doc_id_old']))

#experiences
exp = extractions_df[extractions_df['type']=="position"]
exp = exp[['doc_id_old', 'doc_id_new', 'name', 'num', 'v2', 'v1']]
exp['num'] = exp['num'].apply(lambda x: 'pos' + str(int(x)))
exp = exp.rename({'v2': 'company', 'v1':'title'}, axis=1)

exp = exp.set_index(['doc_id_old', 'doc_id_new', 'name', 'num'], inplace=False)
exp = exp.unstack(level=3)
exp.columns = exp.columns.map('_'.join).str.strip('_')
exp.columns = [x.replace("pos", "") for x in exp.columns]
exp = exp.reset_index()

num = int((len(exp.columns) - 3)/2)
exp = exp[['doc_id_old', 'doc_id_new', 'name'] + ['company_' + str(x) for x in range(1,num)]  + ['title_' + str(x) for x in range(1,num)]]

#education
edu = extractions_df[extractions_df['type']=="education"]
edu = edu[['doc_id_old', 'doc_id_new', 'name', 'num', 'v1']]
edu['num'] = edu['num'].apply(lambda x: 'edu' + str(int(x)))
edu = edu.rename({'v1': 'edu'}, axis=1)

edu = edu.set_index(['doc_id_old', 'doc_id_new', 'name', 'num'], inplace=False)
edu = edu.unstack(level=3)
edu.columns = edu.columns.droplevel(0)
edu = edu.reset_index()
num = int(len(edu.columns)-3)
edu = edu[['doc_id_old', 'doc_id_new', 'name'] + ['edu' + str(x) for x in range(1,num)]]

#merge and save
combined = exp.merge(edu, how='outer', on=['doc_id_old', 'doc_id_new', 'name'])
combined.to_excel(path_out + "/" + out_prefix + "_wide.xlsx", index=False)


#############################################################################
#    Convert to comparison format
#############################################################################

import numpy as np

#grab the information associated with each search
results_df['doc_id_old'] = results_df['docid'].apply(lambda x: int(re.split("_|\\.", x)[1]))
results_df['doc_id_new'] = results_df['docid'].apply(lambda x: int(re.split("_|\\.", x)[3]))
if search_type != "manual":
    results_df['is_namematch'] = results_df['is_namematch'].apply(lambda x: int(x) if x==True or x==False else 0)
    results_df = results_df[['doc_id_old', 'doc_id_new', 'keywords', 'search_type', 'num_results', 'is_namematch']]
    results_df.columns = ['doc_id_old', 'doc_id_new', 'linkedin_keywords', 'linkedin_searchtype', 'linkedin_numresults', 'linkedin_namematch']
else:
    results_df = results_df[['doc_id_old', 'doc_id_new']]
    results_df.columns = ['doc_id_old', 'doc_id_new']

#merge in the extractions
extract_df = pd.read_excel(path_out + "/" + out_prefix + ".xlsx")
results_df = results_df.merge(extract_df, how='outer')
results_df = results_df.replace(np.nan, "")

#prep the education entries
results_edu = results_df[results_df['type'] == "education"]
results_edu = results_edu.drop(['v3', 'v4', 'v5', 'v6'], axis=1)
results_edu = results_edu.rename({'name':'linkedin_name', 'v1':'place', 'v2':'position'}, axis=1)

#prep the position entries
results_pos = results_df[results_df['type']=="position"]
results_pos = results_pos.drop(['v5', 'v6'], axis=1)
results_pos = results_pos.rename({'name':'linkedin_name', 'v1':'position', 'v2':'place', 'v3':'date_start', 'v4':'date_end'}, axis=1)

#combine the two
results_full = results_pos.append(results_edu, ignore_index=True)
results_full = results_full.replace(np.nan,"none")

#create a single row for each candidate containing all of their linkedin information
results_full['combined'] = results_full['date_start'] + " - " + results_full['date_end'] + " || " + results_full['place'] + " || " + \
                results_full['position']
results_full['linkedin_info'] = results_full.groupby(['doc_id_old', 'doc_id_new'])['combined'].transform(lambda x : '\n'.join(x)) 
if search_type != "manual":
    results_full = results_full[['doc_id_old', 'doc_id_new', 'linkedin_keywords', 
                             'linkedin_searchtype', 'linkedin_numresults', 
                             'linkedin_namematch', 'linkedin_name', 'linkedin_info']]
else:
    results_full = results_full[['doc_id_old', 'doc_id_new','linkedin_name', 'linkedin_info']]

results_full = results_full.drop_duplicates()
results_full.to_excel(path_out + "/" + out_prefix + "_full.xlsx", index=False)



#add interview information to double check the scraping
if search_type != "manual":
    info = pd.read_excel(r"C:\Users\Asser.Maamoun\Documents\TextExtraction\output\extractions_merged.xlsx", sheet_name="Values")
    info = info[['doc_id_old', 'doc_id_new', 'date_clean', 'candidate_name_clean', 'company_clean', 'company_flag', 'title_clean', 'career_clean']]
    info = info.rename({'career_clean': 'career_interview'}, axis=1)
    
    
    results_compare = results_full.merge(info, on=['doc_id_new', 'doc_id_old'], how='left')
    results_compare = results_compare[['doc_id_old', 'doc_id_new', 'linkedin_keywords', 'linkedin_searchtype',
       'linkedin_numresults', 'linkedin_namematch', 'linkedin_name',
       'linkedin_info', 'candidate_name_clean', 'career_interview', 'date_clean', 'company_clean' ,'company_flag', 'title_clean']] 
    results_compare.to_excel(path_out + "/" + out_prefix + "_tocompare.xlsx", index=False)


#############################################################################
#    attempt at an automated checker
#############################################################################


suffixes = ['ag', 'co', 'company', 
            'corporation', 'corp', 'inc',
            'gp', 'grp', 'group',
            'holding', 'holdings',
            'international', 'intl', 
            'lc', 'llc', 'llp', 'lp',  
            'ltd', 'lte', 'limited', 'incorporated', 'pllc', 'plc', 'mfg', 'pc', 'pa']

stopwords = ["previously", "formerly", "known as", "acquired", "portfolio company", 
             'an', 'and', 'of', 'the', 'at', 'in', 'on', 'a', 'by', 'as']
             
def clean_company(c):
    #clean punctuations
    if pd.isnull(c):
        return ''
    c = c.lower()
    c = re.sub("[\\-\\/\\|\\,]", " ", c)
    c = re.sub("[^a-z\\s\\d]", "", c)
    
    #clean stopwords
    for x in stopwords:
        c = re.sub("\\b" + x + "\\b", "", c)
    
    #clean suffixes
    for x in suffixes:
        c = re.sub("\\b" + x + "\\b", "", c)
    
    #make all whitespace just a single space
    c = c.strip()
    c = re.sub("\\s+", " ", c)
    
    #the following loop combines adjacent letters, i.e. "t j max" becomes "tj max" and "t j max u s a" becomes "tj max usa"
    letters = re.search("\\b((?:\\S{1}\\s)+(?:\\S))\\b", c)
    while (pd.notnull(letters)):
        letters = letters[0]
        replacement = re.sub(" ", "", letters)
        c = re.sub("\\b" + letters + "\\b", replacement, c)
        letters = re.search("\\b((?:\\S{1}\\s)+(?:\\S))\\b", c)
    return c

def check_person(info, date_hire, company_hire, position_hire):
    if pd.isnull(company_hire) or pd.isnull(date_hire) or pd.isnull(position_hire):
        return 0, ""
    
    #prepare the inputs from the interview
    position_hire_list = position_hire.strip().split(" ")
    year_hire = int(re.match("[0-9]{4}", date_hire).group())
    date_hire = dateutil.parser.parse(date_hire)
    company_hire_clean = clean_company(company_hire)
    
    #check each jobn found on linkedin
    for job in info.split("\n"):
        
        #prepare the inputs from the job
        dates = job.lower().split("||")[0].strip()
        company = job.lower().split("||")[1].strip()
        position = job.lower().split("||")[2].strip()
        position = position.replace("chief financial officer", "cfo")
        position = position.replace("chief executive officer", "ceo")
        
        #first check if the company is the hiring company
        company_clean = clean_company(company)
        if company_clean=="":
            continue
        if company_clean in company_hire_clean or company_hire_clean in company_clean:
            
            #second check if the position lines up with the interview
            for ph in position_hire_list:
                if position in ph or ph in position:
                    
                    #third check that the position was held during the year of interview
                    start = dates.split("-")[0].strip()
                    
                    #need to have started in before or at the date of the interview
                    start_cond = False
                    if "present" in start: #assume that present means 2020 for leeway
                        if year_hire>=2020:
                            start_cond=True
                    elif len(start)==4:
                        start = int(re.search("[0-9]{4}", start).group(0))
                        if year_hire>=start:
                            start_cond=True
                    else:
                        start = dateutil.parser.parse(start)
                        if start - date_hire <= pd.Timedelta(180, unit='d'):
                            start_cond=True
                        
                    #need to have ended the job at least 30 days after the interview
                    end = dates.split("-")[1].strip()
                    end_cond = False
                    if "present" in end: #assume that present means 2021
                        if year_hire<=2021:
                            end_cond=True
                    elif len(end)==4:
                        end = int(re.search("[0-9]{4}", end).group(0))
                        if year_hire<=end:
                            end_cond=True
                    else:
                        end = dateutil.parser.parse(end)
                        if end - date_hire >= pd.Timedelta(30, unit='d'):
                            end_cond=True
                    
                    #both the start and end conditions need to be met
                    if start_cond and end_cond:
                        return 1, company
    return 0, ""

if search_type != "manual":
    results_compare = pd.read_excel(path_out + "/" + out_prefix + "_tocompare.xlsx")
    results_compare['auto_correct'], results_compare['company_linkedin'] = zip(*results_compare.apply(lambda row: check_person(row['linkedin_info'], \
                                                                                     row['date_clean'], \
                                                                                     row['company_clean'], \
                                                                                     row['title_clean']) , axis=1))
    
    results_compare.to_excel(path_out + "/" + out_prefix + "_tocompare_withautocheck.xlsx", index=False)
    
    # ####################
    # #    merge in past edits
    # ####################
    
    # past_edits = pd.read_excel(path_out + "/" + out_prefix + "_tocompare_withautocheck_edited.xlsx")
    # past_edits = past_edits[['doc_id_old', 'doc_id_new', 'correct', 'hired', 'company_linkedin']]
    # results_compare = results_compare.merge(past_edits, how='left', on=['doc_id_old', 'doc_id_new'], suffixes=['', '_y'])
    # results_compare['company_linkedin'] = np.where(results_compare['company_linkedin']=='', results_compare['company_linkedin_y'], results_compare['company_linkedin'])
    # results_compare = results_compare.drop('company_linkedin_y', axis=1)
    # results_compare.to_excel(path_out + "/" + out_prefix + "_tocompare_withautocheck.xlsx", index=False)




