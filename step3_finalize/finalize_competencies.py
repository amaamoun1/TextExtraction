# -*- coding: utf-8 -*-

#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")

import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')

from merge_functions import overlapMatRaw
from merge_functions import overlapMatPercent
from merge_functions import checkMerge
from merge_functions import merge_vars

import re
import pandas as pd
import numpy as np
import xlwings as xw


#############################################################################
#         output file locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
out_local_docx = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/docx/"
out_local_pdf = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/competencies/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


###############################################################################
#    Compare results from docx and string methods
###############################################################################


############################################
#  Create comparable datasets
############################################

#read in the docx version and the pdf merged versions
master_docx = pd.read_excel(out_local_docx + "bigsample_infocompetency_raw.xlsx", sheet_name="values")
master_pdf = pd.read_excel(out_local_pdf + "bigsample_competencies_raw.xlsx", sheet_name="values")

#subset only the variables in both sets
to_drop = ["doc_id", "doc_path", "comp_present", "Non_Missing"]
vars_to_compare = ["doc_id", "doc_path"] + [x for x in master_pdf.columns if (x not in to_drop)]
master_pdf = master_pdf[vars_to_compare]
master_docx = master_docx[[x for x in vars_to_compare if x in master_docx.columns]]
del to_drop

#recreate counts
master_pdf['Non_Missing'] = len(master_pdf.columns) - 2 - master_pdf.apply(lambda x: x.isnull().sum(), axis='columns')
master_docx['Non_Missing'] = len(master_docx.columns) - 2 - master_docx.apply(lambda x: x.isnull().sum(), axis='columns')


############################################
#  Create dataframes on differences
############################################

# -1 = pdf not docx ; 0 is agree ; 1 = docx not pdf
master_diff = master_pdf.copy()
for x in master_pdf.columns:
    if x not in master_docx.columns:
        master_diff[x] = - pd.notnull(master_pdf[x]).astype(int)
    elif x in master_pdf.columns[2:-1]:
        master_diff[x] = pd.notnull(master_docx[x]).astype(int) - pd.notnull(master_pdf[x]).astype(int)
    elif x == "Non_Missing":
        master_diff[x] = master_docx[x] - master_pdf[x]

#counts that only PDF captures
master_onlyPDF = master_diff.copy()
master_onlyPDF = master_onlyPDF.replace(1, 0)
master_onlyPDF = master_onlyPDF.replace(-1, 1)


#counts that only DOCX captures
master_onlyDOCX = master_diff.copy()
master_onlyDOCX = master_onlyDOCX.replace(-1,0)


############################################
#  Statistics
############################################


print("mean", master_diff['Non_Missing'].mean())
print("std", master_diff['Non_Missing'].std())
print("\n\n DIFF \n\n", master_diff.sum(axis=0, skipna=True))
print("\n\n ONLY PDF \n\n", master_onlyPDF.sum(axis=0, skipna=True))
print("\n\n ONLY DOCX \n\n", master_onlyDOCX.sum(axis=0, skipna=True))



#############################################################################
#    Merge the two types of competency tables
#############################################################################


#read in the docx version and the pdf merged versions
master_docx = pd.read_excel(out_local_docx + "bigsample_infocompetency_raw.xlsx", sheet_name="values")
master_pdf = pd.read_excel(out_local_pdf + "bigsample_competencies_raw.xlsx", sheet_name="values")

#subset only the variables in both sets
to_drop = ["doc_id", "doc_path", "comp_present", "Non_Missing"]
comps = [x for x in master_pdf.columns if (x not in to_drop)]
vars_to_compare = ["doc_id", "doc_path", "comp_present"] + comps
master_pdf = master_pdf[vars_to_compare]
master_docx = master_docx[[x for x in vars_to_compare if x in master_docx.columns]]
del to_drop

#only keep the letter ratings
to_replace = ["n/a", "no issues", "limited experience", "NF", "asterisk", "limited", "na"]
master_docx = master_docx.replace(to_replace, np.nan)
unclean = set()
for x in comps:
    if x in master_docx.columns:
        d = master_docx[x].value_counts()
        for e in d.keys():
            if e not in ["a+", "a", "a-", "b+", "b", "b-", "c", "c+", "c-"]:
                unclean.add(e)
print("unclean:", list(unclean))
del x, d, e, unclean, to_replace



#replace when not available in pdf but available in docx
saved = 0
disagree_count = 0
disagree_dict = {}
disagree_loc = {}
new_rows = []
for i, row_p in master_pdf.iterrows():
    doc_id = row_p['doc_id']
    row_d = master_docx[master_docx['doc_id']==doc_id].squeeze()
    new_row = row_p.copy()
    for x in master_pdf.columns[3:]:
        if x in master_docx.columns[2:]:
            if (pd.isnull(new_row[x])) & (pd.notnull(row_d[x])):
                new_row[x] = row_d[x]
                new_row['comp_present'] = 1
                saved += 1
            elif (pd.notnull(row_d[x])) & (pd.notnull(row_p[x])) & (row_d[x] != row_p[x]):
                disagree_count += 1
                new_row[x] = row_p[x] #keep pdf version due to simplicity
                curr = row_p[x] + "_" + row_d[x]
                if row_p['doc_path'] in disagree_loc:
                    disagree_loc[row_p['doc_path']].append(x + "_" + curr)
                else:
                    disagree_loc[row_p['doc_path']] = [x + "_" + curr]
                if curr in disagree_dict:
                    disagree_dict[curr] +=1
                else:
                    disagree_dict[curr] = 1
    new_rows.append(new_row)
master_data = pd.DataFrame(new_rows)
del i, new_rows, row_d, row_p, new_row, x, doc_id, curr

#drop marketing when sales and marketing is present
def clean_marketing(row):
    if pd.notnull(row['sales and marketing']):
        return np.nan
    else:
        return row['marketing']
    
master_data['marketing'] = master_data.apply(clean_marketing, axis=1)

#Add counts
master_data['Non_Missing'] = len(master_data.columns) - 3 - master_data.apply(lambda x: x.isnull().sum(), axis='columns')
master_docx['Non_Missing'] = len(master_docx.columns) - 2 - master_docx.apply(lambda x: x.isnull().sum(), axis='columns')
master_pdf['Non_Missing'] = len(master_pdf.columns) - 3 - master_pdf.apply(lambda x: x.isnull().sum(), axis='columns')

#double check should equal saved
print("Check that saved", saved, "equals", sum(master_data['Non_Missing'] - master_pdf['Non_Missing']))

del disagree_count, disagree_dict, disagree_loc, saved, vars_to_compare, master_docx, master_pdf


############################################
#  Counts and Save
############################################


print("max", master_data['Non_Missing'].max())
print("mean", master_data['Non_Missing'].mean())
print("min", master_data['Non_Missing'].min())
print("std", master_data['Non_Missing'].std())

master_data.columns = [x.replace(" ", "_") for x in master_data.columns]
master_dataCounts = pd.DataFrame(len(master_data) - master_data.apply(lambda x: x.isnull().sum(), axis='rows'))
master_dataCounts = master_dataCounts.reset_index()
master_dataCounts.columns = ["variable", "count"]
master_dataCounts.sort_values("count", ascending=False, inplace=True)
zero_counts = list(master_dataCounts[master_dataCounts['count']==0]['variable'])
keep = [(x not in zero_counts + ["Non_Missing"]) for x in master_dataCounts['variable']]
master_dataCounts = master_dataCounts[keep]
master_data = master_data.drop(zero_counts, axis=1)
del keep, zero_counts


with pd.ExcelWriter(out_local_pdf + "bigsample_competencies_PDFDocRaw.xlsx") as writer:
    master_data.to_excel(writer, sheet_name= "values", index=False)
    master_dataCounts.to_excel(writer, sheet_name= "counts", index=False)
    
    
###############################################################################
# Find Templates
###############################################################################

def select_template(row):
    #only look at rows with at least 20 competencies extracted
    if row['Non_Missing'] < 20:
        return -1
    temp1_count = 0
    temp2_count = 0
    temp3_count = 0
    #count only the variables that are unique to a template
    for var in temp1_only_vars:
        if pd.notnull(row[var]):
            temp1_count += 1
    for var in temp2_only_vars:
        if pd.notnull(row[var]):
            temp2_count += 1
    for var in temp3_only_vars:
        if pd.notnull(row[var]):
            temp3_count += 1
    #to pick a template we require that all other counts are 0
    #if not all other counts are 0 then doc doesnt follow only one template
    if temp1_count>0 and temp2_count==0 and temp3_count==0:
        return 1
    elif temp1_count==0 and temp2_count>0 and temp3_count==0:
        return 2
    elif temp1_count==0 and temp2_count==0 and temp3_count>0:
        return 3
    else:
        return 0

#load data
master_raw = pd.read_excel(out_local_pdf + "bigsample_competencies_PDFDocRaw.xlsx", sheet_name="values")
templates_comp = pd.read_excel(var_path + "keywords.xlsx", sheet_name="competency")

#find the variables that are unique to each template
temp1_vars = set([x.replace(" ", "_") for x in templates_comp[[pd.notnull(x) for x in templates_comp['template_1_group']]]['competency']])
temp2_vars = set([x.replace(" ", "_") for x in templates_comp[[pd.notnull(x) for x in templates_comp['template_2_group']]]['competency']])
temp3_vars = set([x.replace(" ", "_") for x in templates_comp[[pd.notnull(x) for x in templates_comp['template_3_group']]]['competency']])

temp1_only_vars = temp1_vars - temp2_vars - temp3_vars
temp2_only_vars = temp2_vars - temp1_vars - temp3_vars
temp3_only_vars = temp3_vars - temp1_vars - temp2_vars

#find templates
master_raw['template'] = master_raw.apply(select_template, axis=1)

#find counts
master_rawCounts = pd.DataFrame(len(master_raw) - master_raw.apply(lambda x: x.isnull().sum(), axis='rows'))
master_rawCounts = master_rawCounts.reset_index()
master_rawCounts.columns = ["variable", "count"]
master_rawCounts.sort_values("count", ascending=False, inplace=True)

master_templateCounts = pd.DataFrame(master_raw['template'].value_counts())
master_templateCounts = master_templateCounts.reset_index()
master_templateCounts.columns = ['template', 'count']
master_templateCounts = master_templateCounts.sort_values("template")
master_templateCounts['description'] = ['less than 20 competencies', 'ambiguous template',
                                        'template 1 (mostly 2000-2014)', 
                                        'template 2 (mostly 2014-2016)', 
                                        'template 3 (mostly 2016-2019)']

#save
with pd.ExcelWriter(out_local_pdf + "bigsample_competencies_PDFDocRawTemplate.xlsx") as writer:
    master_raw.to_excel(writer, sheet_name= "values", index=False)
    master_rawCounts.to_excel(writer, sheet_name= "counts", index=False)

with pd.ExcelWriter(out_local_pdf + "templateCounts.xlsx") as writer:
    master_templateCounts.to_excel(writer, sheet_name = "templateCounts", index=False)
    
###############################################################################
# Merge together variables
###############################################################################

master_data = pd.read_excel(out_local_pdf + "bigsample_competencies_PDFDocRaw.xlsx", sheet_name="values")

#get overlapping matrix and write a raw and percent version
overlaps_raw = overlapMatRaw(master_data)
overlaps_percent = overlapMatPercent(overlaps_raw)



############################################
#  Perform the merge
############################################

#load the variables to merge
mergers_list = []
for table in ["competency"]:
    mergers_list.append(pd.read_excel(var_path + 'mergers.xlsx', sheet_name=table+"_complete"))
mergers_df = pd.concat(mergers_list, axis=0, join='outer', ignore_index=True, sort=False)
del table, mergers_list

#create a dictionary of variables that we can merge
mergers_dict = checkMerge(master_data, overlaps_raw, mergers_df)
del mergers_df

#merge together the chosen variables in master_merged
master_merged = master_data.copy()
for name in mergers_dict.keys():
    master_merged = merge_vars(master_merged, mergers_dict[name], name)
del name, mergers_dict





############################################
#  Counts and Overlaps on merged data
############################################

#create counts of the merged variables
master_mergedCounts = pd.DataFrame(len(master_merged) - master_merged.apply(lambda x: x.isnull().sum(), axis='rows'))
master_mergedCounts.sort_values(0, ascending=False, inplace=True)
master_mergedCounts = master_mergedCounts.drop('Non_Missing', axis=0)


#create overlaps of the merged (unclean) variables
overlaps_merged_raw = overlapMatRaw(master_merged)
overlaps_merged_percent = overlapMatPercent(overlaps_merged_raw)


############################################
#  Write Information to excels
############################################

#write unmerged uncleaned overlaps
with pd.ExcelWriter(out_local_pdf + "bigsample_competencies_PDFDocRaw_overlaps.xlsx") as writer:
    overlaps_raw.to_excel(writer, sheet_name="overlaps_raw")
    overlaps_percent.to_excel(writer, sheet_name="overlap_percent")
del writer

#write merged uncleaned overlaps
with pd.ExcelWriter(out_local_pdf + "bigsample_competencies_PDFDocMerged_overlaps.xlsx") as writer:
    overlaps_merged_raw.to_excel(writer, sheet_name="overlaps_raw")
    overlaps_merged_percent.to_excel(writer, sheet_name="overlap_percent")
del writer

#write the ratings and counts to local
with pd.ExcelWriter(out_local_pdf + "bigsample_competencies_PDFDocMerged.xlsx") as writer:
    master_merged.to_excel(writer, sheet_name="values", index=False)
    master_mergedCounts.to_excel(writer, sheet_name="counts")
del writer



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
master_info = pd.read_excel(out_local + "/infos/bigsample_infos_PDFDocFinal.xlsx", sheet_name="values")
master_info = master_info[["doc_id", "date_clean"]]
to_keep = [check_date(date) for date in master_info['date_clean']]
master_info = master_info[to_keep]
master_info['year'] = master_info['date_clean'].apply(lambda x: int(x[:4]))
master_info = master_info[master_info['year']<2020]
master_info = master_info.drop(['date_clean'], axis=1)
del to_keep

#add to the raw and merged dataframes
master_raw = pd.read_excel(out_local_pdf + "bigsample_competencies_PDFDocRaw.xlsx", sheet_name="values")
master_raw.drop(['comp_present', 'Non_Missing', 'doc_path'],axis=1, inplace=True)
master_raw = master_info.merge(master_raw, how='left')

master_merged = pd.read_excel(out_local_pdf + "bigsample_competencies_PDFDocMerged.xlsx", sheet_name="values")
master_merged.drop(['comp_present', 'Non_Missing', 'doc_path'],axis=1, inplace=True)
master_merged = master_info.merge(master_merged, how='left')
del master_info

#create counts by year
master_raw = pd.melt(master_raw, id_vars=['doc_id', 'year'], value_name='rating')
master_raw = master_raw[pd.notnull(master_raw['rating'])]
raw_year_counts = pd.DataFrame(master_raw.groupby(['year', 'variable']).size()).reset_index()
raw_year_counts.columns = ['year', 'competency', 'count']
raw_year_counts = raw_year_counts.set_index(['competency', 'year'])['count'].unstack().reset_index()

master_merged = pd.melt(master_merged, id_vars=['doc_id', 'year'], value_name='rating')
master_merged = master_merged[pd.notnull(master_merged['rating'])]
merged_year_counts = pd.DataFrame(master_merged.groupby(['year', 'variable']).size()).reset_index()
merged_year_counts.columns = ['year', 'competency', 'count']
merged_year_counts = merged_year_counts.set_index(['competency', 'year'])['count'].unstack().reset_index()
del master_raw, master_merged


#write the ratings and counts to local
with pd.ExcelWriter(out_local_pdf + "bigsample_competencies_PDFDocRaw_CountsbyYear.xlsx") as writer:
    raw_year_counts.to_excel(writer, sheet_name="values", index=False)
del writer

with pd.ExcelWriter(out_local_pdf + "bigsample_competencies_PDFDocMerged_CountsbyYear.xlsx") as writer:
    merged_year_counts.to_excel(writer, sheet_name="values", index=False)
del writer



