# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 14:51:54 2020

@author: Asser.Maamoun
"""


#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/step3_finalize')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linkedin')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/scraping')

from helper_functions_career import find_tenure, clean_excel_date, \
    clean_company, find_tenure, was_will_position

from clean_date import cleanDateSingle
import pandas as pd
import xlwings as xw
import re
import numpy as np
import datetime

#############################################################################
#         File locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################################################################
#    Helper functions
#############################################################################


def make_lowercase(datum):
    if pd.isnull(datum):
        return np.nan
    return str(datum).lower()

#############################################################################
#    Import Data and Basic cleaning
#############################################################################
    
# load the previous dataset
wb = xw.Book(out_local + "linking_pastdata/master_old_dates_fixed.xlsx")
sheet = wb.sheets["candidates.052512.csv"]
master_old = sheet['A1:HK3027'].options(pd.DataFrame, index=False, header=True).value

#keep columns and rename
oldvars_tokeep = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linking/oldvars_tokeep.xlsx")
master_old = master_old.iloc[:,list(oldvars_tokeep['column_index'])]
master_old.columns = list(oldvars_tokeep['column_newname'])
del wb, sheet, oldvars_tokeep

#we only want rows with data
master_old = master_old[[pd.notnull(x) for x in master_old['candidate_firstname']]]
master_old = master_old[[pd.notnull(x) for x in master_old['candidate_lastname']]]
master_old = master_old[master_old['candidate_name_raw'] != "candidatename"]

#make lowercase
for var in ['candidate_name_raw', 'candidate_firstname', 'candidate_lastname',
            'prepared_for', 'prepared_by', 'purpose_of_this_assessment', 
            'company_raw', 'title_raw', 'rating', 'recommendation',
            'undergrad_raw', 'mba_raw', 'sc_1_desc', 'sc_2_desc', 'sc_3_desc', 'sc_4_desc',
            'sc_5_desc', 'sc_6_desc', 'sc_7_desc', 'sc_8_desc']:
    print("lowercasing", var)
    master_old[var] = master_old[var].apply(make_lowercase)
del var

#make "." np.nan
master_old = master_old.replace(".", np.nan)




################# grab the career info from the Post Current spreadsheet


# load data
oldvars_tokeep = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linking/oldvars_tokeep_career.xlsx")

#wb = xw.Book(out_local + "linking_pastdata/Post Current.xlsx")
wb = xw.Book(out_local + "linking_pastdata/Decety CEO Spreadsheet New.xlsx")
sheet = wb.sheets["candidates.052512.csv"]
master_old_career = sheet['A1:DX3027'].options(pd.DataFrame, index=False, header=True).value

master_old_career = master_old_career.iloc[:,list(oldvars_tokeep['column_index'])]
master_old_career = master_old_career.iloc[12:,]
master_old_career.columns = list(oldvars_tokeep['column_newname'])

master_old_career = master_old_career.fillna(".")
master_old_career['date_clean_old'] = master_old_career['date_clean_old'].apply(cleanDateSingle)


for col in [x for x in master_old_career.columns if "j" in x]:
    master_old_career[col] = master_old_career[col].astype(str)
    master_old_career[col] = master_old_career[col].apply(lambda x: x.replace(" 00:00:00", ""))


# clean up the career variables
master_old_career['career_clean_olddata'] = "||" + master_old_career['j6_s'] + " - " + \
            master_old_career['j6_e'] + "||" + master_old_career['j6_c'] + "||" + master_old_career['j6_p'] + "||\n" + \
            "||" + master_old_career['j5_s'] + " - " + master_old_career['j5_e'] + \
            "||" + master_old_career['j5_c'] + "||" + master_old_career['j5_p'] + "||\n" + \
            "||" + master_old_career['j4_s'] + " - " + master_old_career['j4_e'] + \
            "||" + master_old_career['j4_c'] + "||" + master_old_career['j4_p'] + "||\n" + \
            "||" + master_old_career['j3_s'] + " - " + master_old_career['j3_e'] + \
            "||" + master_old_career['j3_c'] + "||" + master_old_career['j3_p'] + "||\n" + \
            "||" + master_old_career['j2_s'] + " - " + master_old_career['j2_e'] + \
            "||" + master_old_career['j2_c'] + "||" + master_old_career['j2_p']
master_old_career['career_clean_olddata'] = master_old_career['career_clean_olddata'].apply(lambda x: x.replace("||. - .||.||.||\n", ""))
master_old_career['career_clean_olddata'] = master_old_career['career_clean_olddata'].apply(lambda x: x.replace("|| ||.||.", ""))

# create career variables to merge with new data
master_old_career['hired_company_old'] = np.where(master_old_career['hired_old']==1, master_old_career['j2_c'], np.nan)
master_old_career['hired_start_old'] = np.where(master_old_career['hired_old']==1, master_old_career['j2_s'], np.nan)
master_old_career['hired_end_old'] = np.where(master_old_career['hired_old']==1, master_old_career['j2_e'], np.nan)

#add variables for past/future ceo
master_old_career['temp1'], master_old_career['temp2'], master_old_career['future_ceo_old'], master_old_career['future_cfo_old'] = \
    zip(*master_old_career.apply(lambda row: was_will_position(row['career_clean_olddata'], \
                                          row['date_clean_old'], company_linkedin=row['hired_company_old'], hired_position=1) , axis=1))

#add variables for tenure
master_old_hired = master_old_career[master_old_career['hired_old']==1]
master_old_hired['tenure_before_old'], master_old_hired['tenure_after_old'] = zip(*master_old_hired.apply( \
                                            lambda row: find_tenure(row['date_clean_old'], \
                                            row['hired_start_old'], row['hired_end_old']) , axis=1))

master_old_nothired = master_old_career[master_old_career['hired_old']!=1]
master_old_career = master_old_hired.append(master_old_nothired)

master_old_career = master_old_career[['doc_id_old', 'career_clean_olddata', 
                                       'hired_old', 'hired_start_old', 'hired_end_old', 'tenure_before_old',
                                       'tenure_after_old', 'future_ceo_old', 'future_cfo_old']]
master_old_career = master_old_career.replace(".", np.nan)

del wb, sheet, oldvars_tokeep, master_old_hired, master_old_nothired

master_old = master_old.merge(master_old_career, how='left')

#############################################################################
#    Individual variable cleaning
#############################################################################

############################################
#  Clean Candidate Name
############################################

names_bad = ['formatted table', 'dr', 'md', 'mba', 'cfa', 'cpa', 'phd',
             'mr', 'mrs', 'ms', 'rev', 'president', 'coo', 'founder']

name_suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']

def clean_name(x):
    x = re.sub("[\\(“\\\"\\\']+.*[\\)”\\\"\\\']+", "", x) #removes nicknames
    x = re.sub("[^a-z\\s\\-]","", x) #clean punctuation
    x = re.sub("\\b[a-z]\\b", "", x) #take out one letter words likely to be middle names or ratings
    for y in names_bad:
        x = re.sub("\\b" + y + "\\b", "", x)
    x = re.sub("\\s+", " ", x) #make all whitespace a space
    x = x.strip() #trim leading and trailing whitespace
    return x

master_old['candidate_flag'] = 0
master_old['candidate_name_clean'] = master_old['candidate_name_raw'].apply(clean_name)

############################################
#  Clean Date
############################################

#make date into YYYY-MM-DD format
master_old['date_clean'] = master_old['date_raw'].apply(cleanDateSingle)


############################################
#  Place title dummies into one column
############################################

titles = ['ceo', 'coo', 'cfo', 'cto', 'cio_inv', 'cmo', 'division_manager', 
          'general_manager_other', 'president', 'dir_board_member', 'chairman',
          'counsel', 'md_executive_dir', 'vp_evp_svp', 'partner_junior_managing',
          'founder_cofounder', 'analyst_associate_assistant']

title_clean = []
for i, row in master_old.iterrows():
    curr = []
    for title in titles:
        if row[title] == 1:
            curr.append(title)
    curr = ' AND '.join(curr)
    title_clean.append(curr)
master_old['title_clean'] = title_clean
master_old = master_old.drop(titles, axis=1)
del i, row, curr, title, titles, title_clean


############################################
#  Clean Company Name and flag
############################################

def clean_gender(g):
    if g==1:
        return "f"
    return "m"

#CONVERT 0/1 TO M/F
master_old['gender'] = master_old['gender'].apply(clean_gender)


############################################
#  CleanRatings and Scorecard
############################################


def clean_rating(entry):
    rating = np.nan
    find_rating = re.match("^\\s*(a|b|c){1}\\s*(\\+|\\-)?(?:[^a-z].*)*$", str(entry).lower(), flags=re.DOTALL) #also grabs the suffix i.e."+\-"
    if find_rating:
        rating=find_rating.group(1)
        suffix = find_rating.group(2)
        if suffix:
            rating= rating + suffix
    return rating

#add rating_clean
master_old['rating_cleaned'] = master_old['rating'].apply(clean_rating)

#drop comments
for x in master_old.columns:
    if re.search("^(comp_raw_|sc_\\D)", x):
        print("cleaning", x)
        master_old[x] = master_old[x].apply(clean_rating)
del x


############################################
#  Clean Company Name and flag
############################################

def combine_flags(row):
    if pd.notnull(row['steve']) and row['steve']!="?":
        return row['steve']
    elif pd.notnull(row['morten']) and row['morten']!="?":
        return row['morten']
    else: #this picks up firms that I did not assign a company_clean to due to odd results
        return 3

#create a spreadsheet to fill in with cleaned names
old_companies = master_old[['company_raw']].copy().drop_duplicates().rename({'company_raw':'company name'}, axis=1)
new_companies_link = pd.read_excel(out_local + "companies/CompanyFinalLinks.xlsx")
all_companies_link_unclean = new_companies_link.merge(old_companies, how = 'outer').sort_values("company name")
all_companies_link_unclean.to_excel(out_local + "linking_pastdata/CompanyLinksUnclean.xlsx", sheet_name="raw", index=False)

#merge cleaned names into master
all_companies_link_clean  = pd.read_excel(out_local + "linking_pastdata/CompanyFinalLinksAll.xlsx")
all_companies_link_clean = all_companies_link_clean[['company name', 'company_clean']].rename({'company name':'company_raw'}, axis=1)
master_old = master_old.merge(all_companies_link_clean, how='left')



#find firms that were not flagged before
company_flags = pd.read_excel(out_local + "companies/CompanyFlagsUpdated.xlsx")
need_to_flag = company_flags.merge(all_companies_link_clean[['company_clean']], how="outer")
need_to_flag = need_to_flag[[pd.notnull(x) for x in need_to_flag['company_clean']]]
need_to_flag = need_to_flag[[pd.isnull(x) for x in need_to_flag['morten']]]
need_to_flag = need_to_flag[[pd.isnull(x) for x in need_to_flag['steve']]]
need_to_flag = need_to_flag.drop_duplicates()
need_to_flag.to_excel(out_local + "linking_pastdata/need_to_flag.xlsx", sheet_name="raw", index=False)

#create a master new flags to merge into master_old
new_flags = pd.read_excel(out_local + "linking_pastdata/CompanyFlagsNewFirms.xlsx")
new_flags = pd.concat([company_flags, new_flags], axis=0)
new_flags['company_flag'] = new_flags.apply(combine_flags, axis=1)
new_flags = new_flags[['company_clean', 'company_flag']]
new_flags = new_flags.drop_duplicates()
master_old = master_old.merge(new_flags, how='left')

del all_companies_link_clean, all_companies_link_unclean, company_flags, need_to_flag
del new_companies_link, new_flags, old_companies

############################################
#  Clean Prepared_by
############################################


#first do some basic cleaning on the column
prepby_clean1 = []
for x in master_old['prepared_by']:
    if pd.notnull(x):
        x = re.sub("&", " and ", str(x))
        x = re.sub("\\/"," and ", x)
        x = re.sub("^\\.", "", x)
        x = re.sub("\\bphd\\b","", x)
        x = re.sub("\\bph d\\b", "", x)
        x = re.sub("\\s+", " ", x)
    prepby_clean1.append(x)
prepby_clean1 = pd.DataFrame(prepby_clean1, columns=['prepared_by'])

#load the previous fixes and place into dictionary
prepby_pastfixed = pd.read_excel(out_local + "prepby/prepby_counts1_edited.xlsx")
prepby_pastfixed = prepby_pastfixed.drop("count", axis=1)
prepby_withpast = prepby_clean1.merge(prepby_pastfixed, how='left')
prepby_withpast['count'] = 1
prepby_withpast = prepby_withpast.fillna("").groupby(["prepared_by", "prepby_1", "prepby_2", "prepby_3"]).sum().reset_index()
prepby_withpast.to_excel(out_local + "linking_pastdata/prepby_counts1.xlsx", index=False)

#load the new fixes and merge
prepby_currfixed = pd.read_excel(out_local + "linking_pastdata/prepby_counts1_edited.xlsx")
prepby_clean2 = prepby_clean1.merge(prepby_currfixed, how='left')
prepby_clean2 = prepby_clean2.drop("count", axis=1)
prepby_clean2 = prepby_clean2.drop_duplicates()

#combines the separated prepby columns into one column 
prepby_clean3 = []
for i, row in prepby_clean2.iterrows():
    if pd.notnull(row['prepby_3']):
        row['prepared_by_clean'] = " AND ".join([row['prepby_1'], row['prepby_2'], row['prepby_3']])
    elif pd.notnull(row['prepby_2']):
        row['prepared_by_clean'] = " AND ".join([row['prepby_1'], row['prepby_2']])
    else:
        row['prepared_by_clean'] = row['prepby_1']
    prepby_clean3.append(row)
prepby_clean3 = pd.DataFrame(prepby_clean3)
del i, row


#outputs the final names to ensure we don't accidentally have the same person twice
prepby_dict3={}
for x in prepby_clean3['prepared_by_clean']:
    if pd.notnull(x):
        people = x.split(" AND ")
        for p in people:
            if p not in prepby_dict3:
                prepby_dict3[p] = 1
            else:
                prepby_dict3[p] += 1
del x, people, p
prepby_counts3 = pd.DataFrame(prepby_dict3.items(), columns = ["prepared_by_clean", "count"])
prepby_counts3 = prepby_counts3.sort_values('prepared_by_clean')
prepby_counts3['first_name'] = prepby_counts3['prepared_by_clean'].apply(lambda x: x.split(" ")[0])
prepby_counts3['last_name'] = prepby_counts3['prepared_by_clean'].apply(lambda x: x.split(" ")[-1])
prepby_counts3.to_excel(out_local + "linking_pastdata/prepby_counts3.xlsx", index=False)


#after double checking prepby_counts3, merge in our cleaned data
master_old = master_old.merge(prepby_clean3[['prepared_by', 'prepared_by_clean']], how='left')
master_old = master_old.rename({'prepared_by': 'prepared_by_raw'}, axis=1)

del prepby_clean1, prepby_clean2, prepby_clean3, prepby_counts3, prepby_currfixed
del prepby_dict3, prepby_pastfixed, prepby_withpast



############################################
#  Clean undergrad and add ivy dummy
############################################

def clean_school(c):
    if pd.isnull(c):
        return c
    else:
        c = re.sub("\\.","", c)
        c = re.sub("[^a-zA-Z\\s]", " ", c)
        c = " ".join(c.split())
        return c

master_old['undergrad_raw'] = master_old['undergrad_raw'].fillna("")
master_old['undergrad_raw'] = master_old['undergrad_raw'].apply(lambda x: re.sub("[^a-z\\s]", "", x.strip()))
master_old['undergrad_raw'] = master_old['undergrad_raw'].apply(lambda x: re.sub("\\buniv\\b", "university", x))

undergrads = pd.DataFrame(master_old['undergrad_raw'].value_counts()).reset_index()
undergrads.columns = ['undergrad_raw', 'count']
undergrads = undergrads[['undergrad_raw', 'count']].sort_values('undergrad_raw')
undergrads.to_excel(out_local + "linking_pastdata/undergrads.xlsx", index=False)

undergrads_clean = pd.read_excel(out_local + "linking_pastdata/undergrads_edited.xlsx")
undergrads_clean = undergrads_clean.drop("count", axis=1)
undergrads_clean = undergrads_clean.drop_duplicates()
master_old = master_old.merge(undergrads_clean, how='left')
master_old['undergrad_clean'] = master_old['undergrad_clean'].apply(clean_school)
del undergrads_clean, undergrads

ivies = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/universities/colleges_ivies.xlsx")
ivies.columns = ['undergrad_clean', 'undergrad_ivy']
ivies = [clean_school(x) for x in list(ivies[ivies['undergrad_ivy']==1]['undergrad_clean'])]

new_rows = []
for i, row in master_old.iterrows():
    row["undergrad_ivy"] = 0
    doc_colleges = row['undergrad_clean']
    if pd.notnull(doc_colleges):
        doc_colleges = doc_colleges.split(" AND ")
        for c in doc_colleges:
            if c in ivies:
                row['undergrad_ivy'] = 1
                break
    new_rows.append(row)
master_old = pd.DataFrame(new_rows)
print(sum(master_old['undergrad_ivy']))
del i, row, doc_colleges, c, new_rows, ivies

master_old = master_old.drop('undergrad_raw', axis=1)


############################################
#  Clean mba and add top14 dummy
############################################

master_old['mba_raw'] = master_old['mba_raw'].fillna("")
master_old['mba_raw'] = master_old['mba_raw'].apply(lambda x: re.sub("[^a-z\\s]", "", x.strip()))
master_old['mba_raw'] = master_old['mba_raw'].apply(lambda x: re.sub("\\buniv\\b", "university", x))

mbas = pd.DataFrame(master_old['mba_raw'].value_counts()).reset_index()
mbas.columns = ['mba_raw', 'count']
mbas = mbas[['mba_raw', 'count']].sort_values('mba_raw')
mbas.to_excel(out_local + "linking_pastdata/mbas.xlsx", index=False)

mbas_clean = pd.read_excel(out_local + "linking_pastdata/mbas_edited.xlsx")
mbas_clean = mbas_clean.drop("count", axis=1)
master_old = master_old.merge(mbas_clean, how='left')
master_old['mba_clean'] = master_old['mba_clean'].apply(clean_school)
del mbas, mbas_clean

top14 = pd.read_excel("C:/Users/Asser.Maamoun/Documents/TextExtraction/college_lists/business_school/business_schools_final.xlsx")
top14 = list(set(top14[top14['mba_top14']==1]['college']))

new_rows = []
for i, row in master_old.iterrows():
    row["mba_top14"] = 0
    doc_mbas = row['mba_clean']
    if pd.notnull(doc_mbas):
        doc_mbas = doc_mbas.split(" AND ")
        for c in doc_mbas:
            if c in top14:
                row['mba_top14'] = 1
                break
    new_rows.append(row)
master_old = pd.DataFrame(new_rows)
print(sum(master_old['mba_top14']))
del i, row, c, top14, new_rows, doc_mbas


master_old = master_old.drop('mba_raw', axis=1)

############################################
#  Purpose of this assessment
############################################

def evaluate_purpose(purpose):
    if pd.isnull(purpose):
        return np.nan
    p = re.sub("[^a-z0-9]", " ", purpose)
    p = " ".join(p.split())
    
    if re.search("(hire not? hire|hiring decision|hire|recruit|hiring)", p):
        return "hire no hire"
    if re.search("(promotion|promote)", p):
        return "promotion"
    if re.search("(due diligence|\\bm a\\b|merger|investment|acquire|acquisition)", p):
        return "due diligence"
    if re.search("(candidate|probability of success)", p):
        return "candidate"
    if re.search("(go no go)", p):
        return "go no go"
    if re.search("(strengths?|benefits?|maximize performance)", p) and \
       re.search("(developmental areas|improvement areas|development opportunities" +
                 "|areas of development|areas for development|development areas?" +
                 "|risks?|areas? for improvement|weaknesses|development needs)", p):
        return "general assessment"
    if re.search("(evaluate (for |current )?fit|feedback|development|reassignment|ability to lead)", p):
        return "general assessment"
    if re.search("^date", p):
        return "wrong extraction"
    return "other"
    
master_old = master_old.rename({'purpose_of_this_assessment':'purpose_raw'}, axis=1)
purpose_counts1 = master_old['purpose_raw'].value_counts().reset_index()
purpose_counts1.columns = ['purpose_raw', 'count']
purpose_counts1['purpose_clean'] = purpose_counts1['purpose_raw'].apply(evaluate_purpose)
purpose_counts1 = purpose_counts1.sort_values('purpose_raw')
purpose_counts1.to_excel(out_local + "/linking_pastdata/purpose_counts1.xlsx", index=False)

master_old['purpose_clean'] = master_old['purpose_raw'].apply(evaluate_purpose)

############################################
#  Scorecard Items
############################################

#####
#####  find percentage of words that are rev/cost
#####

from assign_scorecard_manual import assign_topic

master_old_sc = master_old[['doc_id_old', 'sc_1_desc', 'sc_2_desc', 'sc_3_desc', 'sc_4_desc', 'sc_5_desc', 'sc_6_desc', 'sc_7_desc', 'sc_8_desc']]
master_old_sc = master_old_sc.replace(np.nan, '', regex=True)
master_old_sc['sc_full'] = master_old_sc['sc_1_desc'] + " " + master_old_sc['sc_2_desc'] + " " + master_old_sc['sc_3_desc'] + " " + \
    master_old_sc['sc_4_desc'] + " " + master_old_sc['sc_5_desc'] + " " + master_old_sc['sc_6_desc'] + " " + \
    master_old_sc['sc_7_desc'] + " " + master_old_sc['sc_8_desc']

master_old_sc_eval = []
for i, row in master_old_sc.iterrows():
    if i % 1000 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['sc_total_words'], row['sc_score_revenue'], row['sc_score_cost'], row['sc_score_diff'], row['sc_type'] = assign_topic(row['sc_full'])
    master_old_sc_eval.append(row)
print(i, datetime.datetime.now().strftime('%H:%M:%S'))
del i, row
master_old_sc_eval = pd.DataFrame(master_old_sc_eval)
master_old_sc_eval = master_old_sc_eval.drop('sc_score_diff', axis=1)
master_old_sc_eval = master_old_sc_eval[['doc_id_old', 'sc_total_words', 'sc_score_revenue', 'sc_score_cost', 'sc_type']]
master_old = master_old.merge(master_old_sc_eval, how='left')

del assign_topic


#####
#####  evaluate each item
#####

from cluster_scorecard_manual import assign_topic as assign_topic_detail, grab_headline, split_growth_row, split_relations_row, merge_into

master_old_sc = master_old[['doc_id_old', 'sc_1_desc', 'sc_2_desc', 'sc_3_desc', 'sc_4_desc', 'sc_5_desc', 'sc_6_desc', 'sc_7_desc', 'sc_8_desc']]
master_old_sc = master_old_sc.replace(np.nan, '', regex=True)

# give each description its own row
master_old_sc = pd.melt(frame=master_old_sc, id_vars=['doc_id_old'], var_name='number', value_name='desc')
master_old_sc['number'] = master_old_sc['number'].apply(lambda x: int(re.search('\\d+', x).group(0)))
master_old_sc = master_old_sc[pd.notnull(master_old_sc['desc'])]
master_old_sc = master_old_sc[master_old_sc['desc']!=""]
master_old_sc = master_old_sc.sort_values(['doc_id_old', 'number'])

#grab the first part of the scorecard item i.e. everything before first bullet
master_old_sc['head'] = master_old_sc['desc'].apply(grab_headline)
master_old_sc = master_old_sc.reset_index(drop=True)

#evaluate the final
master_old_sc_eval = []
for i, row in master_old_sc.iterrows():
    if i % 1000 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['topic_pred'], row['eval_method'], row['prim_score'], row['sec_score'] = assign_topic_detail(row['head'])
    master_old_sc_eval.append(row)
del i, row
master_old_sc_eval = pd.DataFrame(master_old_sc_eval)
master_old_sc_eval['not found'] = master_old_sc_eval.apply(lambda row: int(row["prim_score"]==0 and row["sec_score"]<=1), axis=1)
master_old_sc_eval['multiple'] = master_old_sc_eval.apply(lambda row: int("," in row["topic_pred"] and (row["sec_score"] > 1 or row['prim_score']>0)), axis=1)


#####
#####  split growth topic
#####

df_growth = master_old_sc_eval[master_old_sc_eval['topic_pred']=="growth"][['doc_id_old', 'number', 'desc', 'head']]
df_growth = df_growth.reset_index(drop=True)
df_growth_eval = []
for i, row in df_growth.iterrows():
    if i % 500 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['growth_pred'], row['eval_method'] = split_growth_row(row)
    df_growth_eval.append(row)
del i, row
df_growth_eval = pd.DataFrame(df_growth_eval)
df_growth_eval['growth_pred'] = df_growth_eval['growth_pred'].apply(lambda x: "growth_" + x)
df_growth_eval = df_growth_eval.drop(['eval_method'], axis = 1)

#back into master_old_sc_eval
master_old_sc_eval = master_old_sc_eval.merge(df_growth_eval, how='left', on = ['doc_id_old', 'number', 'desc', 'head'])
master_old_sc_eval['topic_pred'] = master_old_sc_eval.apply(lambda row: merge_into(row['growth_pred'], row['topic_pred']), axis=1)
master_old_sc_eval.drop(['growth_pred'], inplace=True, axis=1)


#####
#####  split relations topic
#####

df_relations = master_old_sc_eval[master_old_sc_eval['topic_pred']=="relations"][['doc_id_old', 'number', 'desc', 'head']]
df_relations = df_relations.reset_index(drop=True)
df_relations_eval = []
for i, row in df_relations.iterrows():
    if i % 500 == 0:
        print(i, datetime.datetime.now().strftime('%H:%M:%S'))
    row['relations_pred'], row['eval_method'] = split_relations_row(row)
    df_relations_eval.append(row)
del i, row
df_relations_eval = pd.DataFrame(df_relations_eval)
df_relations_eval['relations_pred'] = df_relations_eval['relations_pred'].apply(lambda x: "relations_" + x)
df_relations_eval = df_relations_eval.drop(['eval_method'], axis = 1)

#back into master_old_sc_eval
master_old_sc_eval = master_old_sc_eval.merge(df_relations_eval, how='left', on = ['doc_id_old', 'number', 'desc', 'head'])
master_old_sc_eval['topic_pred'] = master_old_sc_eval.apply(lambda row: merge_into(row['relations_pred'], row['topic_pred']), axis=1)
master_old_sc_eval.drop(['relations_pred'], inplace=True, axis=1)


#####
#####  transform to wide format and merge
#####

df_finalclean = master_old_sc_eval.copy()
df_finalclean = df_finalclean[(df_finalclean['multiple']==0) & (df_finalclean['not found']==0)]
df_finalclean = df_finalclean[['doc_id_old', 'number', 'topic_pred']]
df_finalclean['number'] = df_finalclean['number'].apply(lambda x: "sc_" + str(x) + "_topic")
df_finalclean = df_finalclean.pivot('doc_id_old','number','topic_pred')
df_finalclean= df_finalclean.reset_index()


master_old = master_old.merge(df_finalclean, how='left')


#############################################################################
#    save
#############################################################################


master_old.to_excel(out_local + "linking_pastdata/master_old_clean.xlsx", index=False)


