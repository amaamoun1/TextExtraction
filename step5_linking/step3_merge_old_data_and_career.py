# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 14:51:54 2020

@author: Asser.Maamoun
"""


#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linkedin')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')

from merge_functions import overlapMatRaw
from merge_functions import overlapMatPercent
from merge_functions import checkMerge_nodrop
from merge_functions import merge_vars_nodrop

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


#load the linkages
docid_to_id = pd.read_excel(out_local + "linking_pastdata/DOCID_to_ID.xlsx")
docid_to_id_dups = docid_to_id[docid_to_id.duplicated(subset='doc_id', keep=False)]

# load the new dataset
master_clean = pd.read_excel(out_local + "extractions.xlsx", sheet_name = "Values")
master_clean = master_clean.drop("is_pre2012", axis=1)
column_order = list(master_clean.columns)

# load the previous dataset
master_old = pd.read_excel(out_local + "linking_pastdata/master_old_clean.xlsx")
master_old = master_old.drop_duplicates()
master_old = master_old.rename({'doc_name_old': 'doc_name'}, axis=1)

#merge in the linkages (reset index because some doc_ids are linked to multiple doc_id_olds)
master_clean = master_clean.merge(docid_to_id, how='left')
master_clean = master_clean.rename({'doc_id':'doc_id_new'}, axis=1)
master_clean = master_clean.reset_index(drop=True)
master_clean['doc_id_old'] = master_clean['doc_id_old'].fillna(-1)
         
#get old docs not in my new sample
master_append = master_old.merge(docid_to_id, how='left')
master_append = master_append[[pd.isnull(x) for x in master_append['doc_id']]]
master_append = master_append.rename({'doc_id':'doc_id_new'}, axis=1)
master_append['doc_id_new'] = master_append['doc_id_new'].fillna(-1)
master_append['gender_method'] = master_append.apply(lambda row: np.where(pd.notnull(row['gender']), 'old_data', np.nan), axis=1)




#############################################################################
#    Merge in other variables...
#############################################################################


to_sub = ['candidate_name_raw', 'candidate_firstname', 'candidate_lastname',
       'prepared_for', 'prepared_by_raw', 'purpose_raw', 'purpose_clean', 'date_raw',
       'company_raw', 'title_raw', 'rating', 'recommendation',
       'date_clean', 'title_clean', 'company_clean', 'company_flag', 
       'prepared_by_clean', 'undergrad_clean', 'doc_name',
       'undergrad_ivy', 'mba_clean', 'mba_top14', 'rating_cleaned',
       'candidate_flag', 'candidate_name_clean']

saved_vars = {}
for x in to_sub:
    saved_vars[x] = 0
        
new_rows = []
for i, row_ext in master_clean.iterrows():
    #grab new and old id
    new_id = row_ext['doc_id_new']
    old_id = row_ext['doc_id_old']
    
    if old_id==-1:
        new_rows.append(row_ext)
        continue
    
    #grab old row and check that its 1-1 link
    row_old = master_old[master_old['doc_id_old']==old_id]
    if len(row_old)>1:
        print('help', new_id)
    row_old = row_old.squeeze()
    
    new_row = row_ext.copy()
    for x in to_sub:
        if (pd.isnull(new_row[x])) & (pd.notnull(row_old[x])):
            new_row[x] = row_old[x] #merge in the variable from the old documents
            saved_vars[x] += 1
            if x=="company_clean":
                new_row['company_flag'] = row_old['company_flag']
            if x=="undergrad_clean":
                new_row['undergrad_ivy'] = row_old['undergrad_ivy']
            if x=="mba_clean":
                new_row['mba_top14'] = row_old['mba_top14']
            if x=="gender":
                new_row['gender_method'] = 'old_data'
    new_rows.append(new_row)
master_data = pd.concat(new_rows, axis=1).T
del i, row_ext, new_id, old_id, row_old, new_row, x, to_sub, new_rows

del saved_vars

#############################################################################
#    Compare Gender
#############################################################################                     


saved = 0
checked = 0
disagree_count = 0
disagree_dict = {}
saved_loc = {}
saved_var = {}
new_rows = []
disagree_df = []
saved_df = []
for i, row_ext in master_data.iterrows():
    #grab new and old id
    new_id = row_ext['doc_id_new']
    old_id = row_ext['doc_id_old']
    
    #if no old id just append new row
    if old_id==-1:
        new_rows.append(row_ext)
        continue
    
    #grab old row and check that its 1-1 link
    row_old = master_old[master_old['doc_id_old']==old_id]
    if len(row_old)>1:
        print('help', new_id)
    row_old = row_old.squeeze()
    
    #set up disagree row and saved row for caching
    disagree_row = {'doc_name_old': row_old['doc_name'], 'doc_name_new':row_ext['doc_name'],
                    'candidate_old': row_old['candidate_name_raw'], 'candidate_new':row_ext['candidate_name_raw'],
                    'date_old': row_old['date_clean'], 'date_new':row_ext['date_clean']}
    saved_row = {'doc_name_old': row_old['doc_name'], 'doc_name_new':row_ext['doc_name'],
                    'candidate_old': row_old['candidate_name_raw'], 'candidate_new':row_ext['candidate_name_raw'],
                    'date_old': row_old['date_clean'], 'date_new':row_ext['date_clean'],
                    'duplicate':row_ext['is_duplicate']}
    new_row = row_ext.copy()
    for x in ['gender']:
        checked += 1
        if (pd.isnull(new_row[x])) & (pd.notnull(row_old[x])):
            new_row[x] = row_old[x] #merge in the variable from the old documents
            if 'saved' in saved_row:
                saved_row['saved'].append(x)
            else:
                saved_row['saved'] = [x]
            if x in saved_var:
                saved_var[x] += 1
            else:
                saved_var[x] = 1
            saved += 1
        elif (pd.notnull(row_old[x])) & (pd.notnull(row_ext[x])) & (row_old[x] != row_ext[x]):
            disagree_count += 1
            new_row[x] = row_ext[x] #keep old version, they are likely to be right
            curr = row_ext[x] + "_" + row_old[x]
            if 'disagreements' in disagree_row:
                disagree_row['disagreements'].append(x + "_" + curr)
            else:
                disagree_row['disagreements'] = [x + "_" + curr]
            if curr in disagree_dict:
                disagree_dict[curr] +=1
            else:
                disagree_dict[curr] = 1
        if (pd.notnull(row_old[x])):
            new_row['gender_method'] = "old_data"
    if 'disagreements' in disagree_row:
        disagree_row['num_disagreements'] = len(disagree_row['disagreements'])
        disagree_df.append(disagree_row)
    if 'saved' in saved_row:
        saved_row['num_saved'] = len(saved_row['saved'])
        saved_df.append(saved_row)
    new_rows.append(new_row)

master_data = pd.concat(new_rows, axis=1).T
disagree_df = pd.DataFrame(disagree_df)
saved_df = pd.DataFrame(saved_df)
del i, new_rows, row_old, row_ext, new_row, x, new_id, old_id, curr, disagree_row

del saved, checked, disagree_count, disagree_dict, saved_loc
del saved_var, disagree_df, saved_df, saved_row

#############################################################################
#    Compare Competencies
#############################################################################


saved = 0
checked = 0
disagree_count = 0
disagree_dict = {}
saved_loc = {}
saved_var = {}
new_rows = []
disagree_df = []
saved_df = []
for i, row_ext in master_data.iterrows():
    #grab new and old id
    new_id = row_ext['doc_id_new']
    old_id = row_ext['doc_id_old']
    
    #if no old id just append new row
    if old_id==-1:
        new_rows.append(row_ext)
        continue
    
    #grab old row and check that its 1-1 link
    row_old = master_old[master_old['doc_id_old']==old_id]
    if len(row_old)>1:
        print('help', new_id)
    row_old = row_old.squeeze()
    
    #set up disagree row and saved row for caching
    disagree_row = {'doc_name_old': row_old['doc_name'], 'doc_name_new':row_ext['doc_name'],
                    'candidate_old': row_old['candidate_name_raw'], 'candidate_new':row_ext['candidate_name_raw'],
                    'date_old': row_old['date_clean'], 'date_new':row_ext['date_clean']}
    saved_row = {'doc_name_old': row_old['doc_name'], 'doc_name_new':row_ext['doc_name'],
                    'candidate_old': row_old['candidate_name_raw'], 'candidate_new':row_ext['candidate_name_raw'],
                    'date_old': row_old['date_clean'], 'date_new':row_ext['date_clean'],
                    'duplicate':row_ext['is_duplicate']}
    new_row = row_ext.copy()
    for x in master_old.columns:
        if 'comp_raw' in x:
            checked += 1
            if (pd.isnull(new_row[x])) & (pd.notnull(row_old[x])):
                new_row[x] = row_old[x] #merge in the variable from the old documents
                if 'saved' in saved_row:
                    saved_row['saved'].append(x)
                else:
                    saved_row['saved'] = [x]
                if x in saved_var:
                    saved_var[x] += 1
                else:
                    saved_var[x] = 1
                saved += 1
            elif (pd.notnull(row_old[x])) & (pd.notnull(row_ext[x])) & (row_old[x] != row_ext[x]):
                disagree_count += 1
                new_row[x] = row_ext[x] #keep old version, they are likely to be right
                curr = row_ext[x] + "_" + row_old[x]
                if 'disagreements' in disagree_row:
                    disagree_row['disagreements'].append(x + "_" + curr)
                else:
                    disagree_row['disagreements'] = [x + "_" + curr]
                if curr in disagree_dict:
                    disagree_dict[curr] +=1
                else:
                    disagree_dict[curr] = 1
    if 'disagreements' in disagree_row:
        disagree_row['num_disagreements'] = len(disagree_row['disagreements'])
        disagree_df.append(disagree_row)
    if 'saved' in saved_row:
        saved_row['num_saved'] = len(saved_row['saved'])
        saved_df.append(saved_row)
    new_rows.append(new_row)

master_data = pd.concat(new_rows, axis=1).T
disagree_df = pd.DataFrame(disagree_df)
saved_df = pd.DataFrame(saved_df)
del i, new_rows, row_old, row_ext, new_row, x, new_id, old_id, curr, disagree_row
del saved_row, saved_var
        

disagree_df = disagree_df.sort_values('candidate_new')
disagree_df.to_excel(out_local + "/linking_pastdata/disagreements.xlsx", index=False)

saved_df = saved_df.sort_values('candidate_new')
saved_df.to_excel(out_local + "/linking_pastdata/saved.xlsx", index=False)

del saved, checked, disagree_count, disagree_dict, saved_loc
del disagree_df, saved_df

#append the old rows not found in new interviews
master_data = pd.concat([master_data, master_append])




###############################################################################
# Merge together competencies (again...)
###############################################################################

#get overlapping matrix and write a raw and percent version
comp_vars = [x for x in master_data.columns if "comp_raw_" in x]
overlaps_raw = overlapMatRaw(master_data.rename({'doc_id_new':'doc_id'}, axis=1)[['doc_id'] + comp_vars])
overlaps_percent = overlapMatPercent(overlaps_raw)


############################################
#  Perform the merge
############################################

def rename_comp(comp):
    if pd.isnull(comp):
        return comp
    return "{}{}".format('comp_raw_', comp)

#load the variables to merge
mergers_list = []
for table in ["competency"]:
    mergers_list.append(pd.read_excel(var_path + 'mergers.xlsx', sheet_name=table+"_complete"))
mergers_df = pd.concat(mergers_list, axis=0, join='outer', ignore_index=True, sort=False)
del table

#rename
for comp_number in mergers_df.columns:
    mergers_df[comp_number] = mergers_df[comp_number].apply(rename_comp)
del comp_number

#create a dictionary of variables that we can merge
mergers_dict = checkMerge_nodrop(master_data.rename({'doc_name':'doc_path'}, axis=1), overlaps_raw, mergers_df)

#merge together the chosen variables in master_merged
master_merged = master_data.copy()
for name in mergers_dict.keys():
    master_merged = merge_vars_nodrop(master_merged, mergers_dict[name], name)
del name, mergers_dict, mergers_df, mergers_list

comp_vars = [x for x in master_merged.columns if "comp_merged_" in x]
overlaps_merged_raw = overlapMatRaw(master_merged.rename({'doc_id_new':'doc_id'}, axis=1)[['doc_id'] + comp_vars])

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
to_keep = [check_date(date) for date in master_merged['date_clean']]
copy = master_merged.copy()[to_keep]
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



#############################################################################
#    Add old scorecard variables
#############################################################################

#load old variables
master_old_sc = master_old[['doc_id_old'] + [x for x in master_old.columns if re.match("^sc_", x)]]
master_old_sc = master_old_sc.rename({'sc_total_words':'sc_total_words_old', 'sc_score_revenue':'sc_score_revenue_old',
                                      'sc_score_cost': 'sc_score_cost_old', 'sc_type':'sc_type_old'}, axis=1)
for i in range(1,9):
    master_old_sc = master_old_sc.rename({'sc_'+str(i)+'_desc': 'sc_' + str(i) + '_desc_old'}, axis=1)
    master_old_sc = master_old_sc.rename({'sc_'+str(i)+'_topic': 'sc_' + str(i) + '_topic_old'}, axis=1)

#merge
master_merged = master_merged.merge(master_old_sc, how='left')

#incorporate old sc variables into the new ones
for i in range(1,9):
    master_merged['sc_'+str(i)+'_desc'] = np.where(master_merged['doc_id_new']==-1, master_merged['sc_'+str(i)+'_desc_old'], master_merged['sc_'+str(i)+'_desc'] )
    master_merged['sc_'+str(i)+'_topic'] = np.where(master_merged['doc_id_new']==-1, master_merged['sc_'+str(i)+'_topic_old'], master_merged['sc_'+str(i)+'_topic'] )
    master_merged = master_merged.drop(['sc_'+str(i)+'_desc_old', 'sc_'+str(i)+'_topic_old'], axis=1)
for var in ['sc_total_words', 'sc_score_revenue', 'sc_score_cost', 'sc_type']:
    master_merged[var] = np.where(master_merged['doc_id_new']==-1, master_merged[var+'_old'], master_merged[var])
    master_merged = master_merged.drop(var+'_old', axis=1)
    
#############################################################################
#    Add the career variables
#############################################################################

#merge in the new career variables
master_career = pd.read_excel(out_local + "scraping\career_full_final.xlsx")
master_career = master_career[['doc_id_old', 'doc_id_new', 'linkedin_link', 'businessweek_link',
                               'other_link_1', 'other_link_2', 'career_info', 'hired_company', 
                               'hired', 'hired_start', 'hired_end', 'tenure_before',
                               'tenure_after', 'past_ceo', 
                               'past_cfo', 'future_ceo', 'future_cfo']]
master_career.columns = ['doc_id_old', 'doc_id_new', 'linkedin_link', 'businessweek_link',
                               'other_link_1', 'other_link_2', 'career_info', 'hired_new_company', 
                               'hired_new', 'hired_new_start', 'hired_new_end', 'tenure_new_before',
                               'tenure_new_after', 'past_ceo', 
                               'past_cfo', 'future_ceo', 'future_cfo']

temp = master_career.merge(master_merged[['doc_id_new', 'doc_id_old']], how='left', indicator=True)
temp_ok = temp[temp['_merge']=="both"]
temp_ok = temp_ok.drop(['_merge'], axis=1)

temp_old = temp[temp['_merge']!="both"].copy()
temp_old = temp_old[temp_old['doc_id_new']==-1].drop(['doc_id_new', '_merge'], axis=1)
temp_old = temp_old.merge(master_merged[['doc_id_new', 'doc_id_old']], how='left', indicator=True)
temp_old = temp_old.drop(['_merge'], axis=1)

temp_new = temp[temp['_merge']!="both"].copy()
temp_new = temp_new[temp_new['doc_id_old']==-1].drop(['doc_id_old', '_merge'], axis=1)
temp_new = temp_new.merge(master_merged[['doc_id_new', 'doc_id_old']], how='left', indicator=True)
temp_new = temp_new.drop(['_merge'], axis=1)

master_career = temp_ok.append(temp_old).append(temp_new)

master_merged = master_merged.merge(master_career, on=['doc_id_new','doc_id_old'], how='left')


#copy in the old career variables
master_old_ca = master_old[['doc_id_old', 'career_clean_olddata', 
                                       'hired_old', 'hired_start_old', 'hired_end_old', 'tenure_before_old',
                                       'tenure_after_old', 'future_ceo_old', 'future_cfo_old'
                                       ]].copy()
master_old_ca.columns = ['doc_id_old', 'career_clean_olddata2', 
                                       'hired_old2', 'hired_start_old2', 'hired_end_old2', 'tenure_before_old2',
                                       'tenure_after_old2', 'future_ceo_old2', 'future_cfo_old2']
master_merged = master_merged.merge(master_old_ca, how='left', on=['doc_id_old'], indicator=True)
temp_ok = master_merged[master_merged['_merge']=="both"]
master_merged = master_merged.drop('_merge', axis=1)
list(master_merged.columns)

master_merged['career_clean_olddata'] = np.where(pd.isnull(master_merged['career_clean_olddata']), master_merged['career_clean_olddata2'], master_merged['career_clean_olddata'] )
master_merged['hired_old'] = np.where(pd.isnull(master_merged['hired_old']), master_merged['hired_old2'], master_merged['hired_old'] )
master_merged['hired_old_start'] = np.where(pd.isnull(master_merged['hired_start_old']), master_merged['hired_start_old2'], master_merged['hired_start_old'] )
master_merged['hired_old_end'] = np.where(pd.isnull(master_merged['hired_end_old']), master_merged['hired_end_old2'], master_merged['hired_end_old'] )
master_merged['tenure_old_before'] = np.where(pd.isnull(master_merged['tenure_before_old']), master_merged['tenure_before_old2'], master_merged['tenure_before_old'] )
master_merged['tenure_old_after'] = np.where(pd.isnull(master_merged['tenure_after_old']), master_merged['tenure_after_old2'], master_merged['tenure_after_old'] )
master_merged['future_ceo_old'] = np.where(pd.isnull(master_merged['future_ceo_old']), master_merged['future_ceo_old2'], master_merged['future_ceo_old'] )
master_merged['future_cfo_old'] = np.where(pd.isnull(master_merged['future_cfo_old']), master_merged['future_cfo_old2'], master_merged['future_cfo_old'] )

master_merged['career_info'] = np.where(pd.isnull(master_merged['career_info']), master_merged['career_clean_olddata'], master_merged['career_info'] )
master_merged['future_ceo'] = np.where(pd.isnull(master_merged['future_ceo']), master_merged['future_ceo_old'], master_merged['future_ceo'] )
master_merged['future_cfo'] = np.where(pd.isnull(master_merged['future_cfo']), master_merged['future_cfo_old'], master_merged['future_cfo'] )


#copy in the updated success variables
import xlwings as xw
wb = xw.Book(out_local + "linking_pastdata/Decety CEO Spreadsheet New.xlsx")
sheet = wb.sheets["Summary"]
master_old_success = sheet['A1:N3027'].options(pd.DataFrame, index=False, header=True).value
master_old_success = master_old_success[[pd.notnull(x) for x in master_old_success['Candidate Name']]]
master_old_success.columns = list(master_old_success.columns)[:2] + ['doc_id_old'] + list(master_old_success.columns)[3:]
master_old_success = master_old_success[['doc_id_old', 'Successful at the Firm? Y =2, M = 1, N = 0', 'Firm Succesful with Individual? Y = 2, M =1, N = 0, N/A', 'Overall Success? Y =2, M=1, N=0', 'Narrative']] 
master_old_success.columns = ['doc_id_old', 'success_old_indiv_at_firm', 'success_old_firm_with_indiv', 'success_old_overall', 'success_old_detail']
master_old_success = master_old_success[[pd.notnull(x) for x in master_old_success['success_old_overall']]]

master_merged = master_merged.merge(master_old_success, how='left', on=['doc_id_old'], indicator=True)
temp_ok = master_merged[master_merged['_merge']=="both"]

master_merged = master_merged.drop('_merge', axis=1)


#############################################################################
#    Add the success and the company control variables
#############################################################################

#load success variables
external_success = pd.read_excel(out_local + "scraping\\Neil_Test_Extractions_merged_For_Hired.xlsx", sheet_name="Raw Merge")
external_success = external_success[['doc_id_old', 'doc_id_new', 'success', 'success_detail']]

successes = []
for i, row in external_success.iterrows():
    if len(str(row['success_detail']))>10:
        if row['success_detail'][:12].lower() == "unsuccessful":
            successes.append("0")
            continue
        elif row['success_detail'][:12].lower() == 'intermediate':
            successes.append("1")
            continue
        elif row['success_detail'][:7].lower() == 'success':
            successes.append("2")
            continue
    successes.append(row['success'])
external_success['success'] = successes
external_success.columns = ['doc_id_old', 'doc_id_new', 'success_new_overall', 'success_new_detail']

#load company variables
external_company = pd.read_excel(out_local + "scraping\\Neil_Test_Extractions_merged_For_Hired.xlsx", sheet_name="Combined Dataset")
external_company = external_company[['doc_id_old', 'doc_id_new', 
                               'SIC Code', 'BVDID', 'Orbis Operating Revenue', 'Orbis Employees',
                               'Orbis P and L', 'Pitchbook Total Revenue', 'Pitchbook Employees',
                               'Country', 'State (if US)', 'Orbis File Year', 
                               'Pitchbook File Year', 'Orbis File Type', 'Pitchbook link'
]]
external_company.columns = ['doc_id_old', 'doc_id_new', 'sic_code', 'bvdid', 'orbis_operating_rev', 'orbis_employees',
                               'orbis_p_and_l', 'pitchbook_total_rev', 'pitchbook_employees',
                               'country', 'state_if_us', 'orbis_file_year', 
                               'pitchbook_file_year', 'orbis_file_type', 'pitchbook_link'
]
external_cols = list(external_company.columns[2:])

#treat hyperlinks properly
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/scraping')
from helper_functions_career import get_hyperlinks
import openpyxl
wb = openpyxl.load_workbook(out_local + "scraping\\Neil_Test_Extractions_merged_For_Hired.xlsx")
ws = wb['Combined Dataset']
external_company['pitchbook_link'] = get_hyperlinks(ws, 15, 3804)



master_merged = master_merged.merge(external_success, how='left', on=['doc_id_old', 'doc_id_new'])
master_merged = master_merged.merge(external_company, how='left', on=['doc_id_old', 'doc_id_new'])

career_columns = ['linkedin_link', 'businessweek_link',
                               'other_link_1', 'other_link_2', 'career_info', 'past_ceo', 
                               'past_cfo', 'future_ceo', 'future_cfo',
                               'hired_old', 'hired_old_start', 'hired_old_end', 'tenure_old_before',
                               'tenure_old_after', 'success_old_indiv_at_firm', 'success_old_firm_with_indiv', 'success_old_overall', 'success_old_detail',
                               'hired_new', 'hired_new_company', 'hired_new_start', 'hired_new_end', 'tenure_new_before',
                               'tenure_new_after',
                               'success_new_overall', 'success_new_detail']

#############################################################################
#         Add flags: Duplicates
#############################################################################

master_merged = master_merged.drop(['num_docs', 'is_duplicate'], axis=1)


#find number of docs per candidate-date
dup_df = master_merged[['doc_id_new', 'candidate_firstname', 'candidate_lastname', 'date_clean']].groupby(['candidate_firstname', 'candidate_lastname', 'date_clean'], as_index=False).agg('count')
dup_df.columns = ['candidate_firstname', 'candidate_lastname', 'date_clean', 'num_docs_candate']
dup_counts = dup_df['num_docs_candate'].value_counts()
master_merged = pd.merge(master_merged, dup_df, on=['candidate_firstname', 'candidate_lastname', 'date_clean'], how='left')
del dup_df

#find number of docs per candidate
dup_df = master_merged[['doc_id_new', 'candidate_firstname', 'candidate_lastname']].groupby(['candidate_firstname', 'candidate_lastname'], as_index=False).agg('count')
dup_df.columns = ['candidate_firstname', 'candidate_lastname', 'num_docs_can']
dup_counts = dup_df['num_docs_can'].value_counts()
master_merged = pd.merge(master_merged, dup_df, on=['candidate_firstname', 'candidate_lastname'], how='left')
del dup_df



#duplicates will be when another interview of the same candidate_firstname - candidate_lastname - date exists with more available variables
master_merged['vars_available'] = master_merged.apply(lambda x: x.notnull().sum(), axis='columns')
master_merged = master_merged.sort_values(by=['candidate_firstname', 'candidate_lastname', 
                                            'date_clean', 'vars_available'], ascending = False)
master_merged['is_duplicate'] = [int(x) for x in master_merged.duplicated(subset=['candidate_firstname', 'candidate_lastname', 'date_clean'], keep='first')]


#manually assess cases when a firstname-lastname pairing exists with multiple dates
master_merged_predups = master_merged[['num_docs_can', 'num_docs_candate','doc_id_old', 'vars_available'] + list(master_merged.columns[:21])]
master_merged_predups = master_merged_predups[master_merged_predups['num_docs_can']!=master_merged_predups['num_docs_candate']]
with pd.ExcelWriter(out_local + "extractions_merged_preisduplicate.xlsx") as writer:
    master_merged_predups.to_excel(writer, sheet_name="Values", index=False)
master_merged_postdups = pd.read_excel(out_local + "extractions_merged_postisduplicate.xlsx")
master_merged_postdups = master_merged_postdups[['doc_id_old', 'doc_id_new', 'manual_duplicate']]
master_merged = master_merged.merge(master_merged_postdups, how='left')
master_merged["manual_duplicate"] = master_merged["manual_duplicate"].fillna(0)
master_merged["is_duplicate"] = master_merged[["is_duplicate", "manual_duplicate"]].max(axis=1)
master_merged = master_merged.drop('manual_duplicate', axis=1)

#manually assess cases when two or more documents have the same competency ratings (must have at least 20 ratings)
master_merged_manualdups = pd.read_excel(out_local + "possible_duplicates_yann_edited.xlsx")
master_merged_manualdups = master_merged_manualdups[['doc_id_old', 'doc_id_new', 'duplicate_manual']]
master_merged = master_merged.merge(master_merged_manualdups, how='left')
master_merged["duplicate_manual"] = master_merged["duplicate_manual"].fillna(0)
master_merged["is_duplicate"] = master_merged[["is_duplicate", "duplicate_manual"]].max(axis=1)
master_merged = master_merged.drop('duplicate_manual', axis=1)

#manually assess cases when two or more documentes have the same factor scores and company
master_merged_manualdups2 = pd.read_excel(out_local + "possible_dups_20210723_merged_evaluated.xlsx")
master_merged_manualdups2 = master_merged_manualdups2[['doc_id_old', 'doc_id_new', 'duplicate_manual']]
master_merged = master_merged.merge(master_merged_manualdups2, how='left')
master_merged["duplicate_manual"] = master_merged["duplicate_manual"].fillna(0)
master_merged["is_duplicate"] = master_merged[["is_duplicate", "duplicate_manual"]].max(axis=1)
master_merged = master_merged.drop('duplicate_manual', axis=1)

master_merged = master_merged.sort_values(by=['doc_id_new', 'doc_id_old'], ascending = True)



############################################
#  Create a dummy variable for CEOs and CFOs
############################################


bad_titles = ['succession', 'succession', 'deputy', 'division', 'region', 'assistant', 'office', 'region']

def is_ceo(title):
    if pd.isnull(title):
        return np.nan
    splits = title.split(" AND ")
    for title in splits:
        if "ceo" not in title:
            continue
        total=0
        for bad_word in bad_titles:
            if  bad_word in title:
                total+=1
        if total>0:
            continue
        return 1
    return 0

def is_cfo(title):
    if pd.isnull(title):
        return np.nan
    splits = title.split(" AND ")
    for title in splits:
        if "cfo" not in title:
            continue
        total=0
        for bad_word in bad_titles:
            if  bad_word in title:
                total+=1
        if total>0:
            continue
        return 1
    return 0
    
master_merged['is_ceo'] = master_merged['title_clean'].apply(is_ceo)
master_merged['is_cfo'] = master_merged['title_clean'].apply(is_cfo)


master_merged[master_merged['is_ceo']==1]['title_clean'].value_counts()
master_merged[master_merged['is_cfo']==1]['title_clean'].value_counts()

column_order = column_order[:15] + ['is_ceo', 'is_cfo'] + column_order[15:]

############################################
#  Write Information to excels
############################################

#create the pre_2012 variable
master_merged['is_pre2012'] = np.where(master_merged['doc_id_old']==-1, 0, 1)

#order variables
new_cols = [x for x in master_merged.columns if x not in column_order]
dropped_cols = [x for x in column_order if x not in master_merged.columns]
new_order = ['doc_id_new', 'doc_id_old', 'is_pre2012'] + column_order[1:37] + ['career_clean_olddata'] + career_columns + external_cols + \
    column_order[38:] + ['sc_growth_revenue', 'sc_growth_ebitda', 'sc_staffing', 
    'sc_relations', 'sc_innovate', 'sc_growth_both', 'sc_other', 'sc_deals', 
    'sc_strategy']
new_order.remove('num_docs')
master_merged = master_merged[new_order]
del new_cols, dropped_cols, new_order

#create counts of the merged variables
master_mergedCounts = pd.DataFrame(len(master_merged) - master_merged.apply(lambda x: x.isnull().sum(), axis='rows'))
master_mergedCounts = master_mergedCounts.reset_index()
master_mergedCounts.columns = ['variable', 'count']

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

CompanyFinalCounts = master_merged[["company_clean", "company_raw"]].copy()
CompanyFinalCounts = CompanyFinalCounts.groupby('company_clean', as_index=False).count()
CompanyFinalCounts.columns = ['company_clean', 'count']
CompanyFinalCounts = CompanyFinalCounts.merge(master_merged[['company_clean', 'company_flag']].drop_duplicates(), how='left')

TitleFinalCounts = {}
for titles in master_merged['title_clean']:
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
for x in master_merged['prepared_by_clean']:
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

GenderFinalCounts = master_merged[['doc_id_new','gender', 'gender_method']]
GenderFinalCounts['gender_method'] = GenderFinalCounts['gender_method'].astype(str)
GenderFinalCounts = GenderFinalCounts.groupby(['gender_method', 'gender'], as_index=False).count()
GenderFinalCounts.columns = ['method','gender', 'count']

CollegesFinalCounts={}
for x in master_merged['college_raw']:
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
for x in master_merged['undergrad_clean']:
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
UndergradFinalCounts = UndergradFinalCounts.merge(master_merged[['undergrad_clean', 'undergrad_ivy']].drop_duplicates(), how='left')
UndergradFinalCounts['undergrad_ivy'] = UndergradFinalCounts['undergrad_ivy'].fillna(0)

MBAFinalCounts={}
for x in master_merged['mba_clean']:
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
MBAFinalCounts = MBAFinalCounts.merge(master_merged[['mba_clean', 'mba_top14']].drop_duplicates(), how='left')
MBAFinalCounts['mba_top14'] = MBAFinalCounts['mba_top14'].fillna(0)

CompMergers = pd.read_excel(var_path + 'mergers.xlsx', sheet_name="competency_complete")
CompTemplate = pd.read_excel(var_path + 'keywords.xlsx', sheet_name="competency")
CompTemplate = CompTemplate.drop('main',axis=1).sort_values('competency')
CompTemplateCounts = pd.read_excel(out_local + "/competencies/templateCounts.xlsx")

ScorecardResults = pd.read_excel(out_local + "scorecard/clustering/scorecard_evalresults.xlsx")
ScorecardFinalCounts = pd.read_excel(out_local + "scorecard/clustering/scorecard_finalcleanCounts.xlsx")


#write the ratings and counts to local
with pd.ExcelWriter(out_local + "extractions_merged.xlsx") as writer:
    master_merged.to_excel(writer, sheet_name="Values", index=False)
    master_mergedCounts.to_excel(writer, sheet_name="Counts", index=False)
    CompanyFinalCounts.to_excel(writer, sheet_name="CompanyCounts", index=False)
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



