# -*- coding: utf-8 -*-


#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")

import pandas as pd
import numpy as np
import re


#############################################################################
#         File locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################################################################
#         Combine information
#############################################################################

############################################
#  Info
############################################

#merge in the colleges
master_all = pd.read_excel(out_local + "/infos/bigsample_infos_PDFDocFinal.xlsx", sheet_name="values")
master_all = master_all.drop("Non_Missing", axis=1)
vars_info = ['doc_id', 'doc_name', 'is_pre2012', 'info_present', 'candidate_name_raw',
             'candidate_name_clean', 'candidate_firstname', 'candidate_lastname',
             'candidate_flag',
             'company_raw', 'company_clean', 'company_flag', 'date_raw', 'date_clean', 
             'title_raw', 'title_clean', 'prepared_by_raw', 'prepared_by_clean',
             'prepared_for', 'purpose_raw', 'purpose_clean', 'rating', 'rating_cleaned',
             'recommendation']
CompanyFinalCounts = pd.read_excel(out_local + "/companies/CompanyFinalCounts.xlsx")
TitleFinalCounts = pd.read_excel(out_local + "/titles/TitleFinalCounts.xlsx")
PrepByFinalCounts = pd.read_excel(out_local + "/prepby/prepby_countsFinal.xlsx")
PurposeFinalCounts = pd.read_excel(out_local + "purpose/PurposeFinalCounts.xlsx", sheet_name="raw", index=False)

###############################
# gender
###############################

#merge in the genders
master_genders = pd.read_excel(out_local + "/gender/bigsample_genders.xlsx", sheet_name="values")
master_genders = master_genders[["doc_id", "gender", "method"]]
master_genders.columns = ['doc_id', 'gender', 'gender_method']
vars_gender = list(master_genders.columns)[1:]
master_all = pd.merge(master_all, master_genders, how='left', on=['doc_id'])
del master_genders

GenderFinalCounts = pd.read_excel(out_local + "/gender/GenderFinalCounts.xlsx")


###############################
# Colleges
###############################

#merge in the colleges, undergrads, and mbas
master_colleges = pd.read_excel(out_local + "/colleges/bigsample_colleges.xlsx", sheet_name="values")
master_colleges = master_colleges[['doc_id', 'college_raw', 'college_potential']]
master_all = pd.merge(master_all, master_colleges, how='left', on=['doc_id'])

master_undergrad = pd.read_excel(out_local + "/colleges/bigsample_undergrad_ivies.xlsx", sheet_name="values")
master_undergrad = master_undergrad[["doc_id", "undergrad_clean", "undergrad_ivy"]]
master_all = pd.merge(master_all, master_undergrad, how='left', on=['doc_id'])

master_mba = pd.read_excel(out_local + "/colleges/bigsample_mba_top14.xlsx", sheet_name= "values")
master_mba = master_mba[['doc_id','mba_clean', 'mba_top14']]
master_all = pd.merge(master_all, master_mba, how='left', on=['doc_id'])

vars_college = list(master_colleges.columns)[1:] + list(master_undergrad.columns)[1:] + list(master_mba.columns)[1:]
del master_colleges, master_undergrad, master_mba

CollegesFinalCounts = pd.read_excel(out_local + "/colleges/CollegesFinalCounts.xlsx")
UndergradFinalCounts = pd.read_excel(out_local + "/colleges/UndergradFinalCounts_withIvies.xlsx")
MBAFinalCounts =  pd.read_excel(out_local + "/colleges/MBAFinalCounts_withTop14.xlsx")


###############################
# Careers
###############################

master_careers = pd.read_excel(out_local + "/career/career_clean.xlsx")
master_careers = master_careers[['doc_id', 'career_found', 'career_clean']]
master_all = pd.merge(master_all, master_careers, how='left', on=['doc_id'])
vars_career = ['career_found', 'career_clean']
del master_careers


###############################
# Competencies
###############################

#load the competencies
master_comps_raw = pd.read_excel(out_local + "/competencies/bigsample_competencies_PDFDocRawTemplate.xlsx", sheet_name="values")
master_comps_raw = master_comps_raw.drop(["doc_path", "Non_Missing"], axis=1)
master_comps_raw.columns = ["doc_id", "comp_present"] + ["comp_raw_" + x for x in master_comps_raw.columns[2:-1]] + ['comp_template']
master_comps_raw = master_comps_raw[["doc_id", "comp_present", "comp_template"] + list(master_comps_raw.columns[2:-1])]
master_comps_merged = pd.read_excel(out_local + "/competencies/bigsample_competencies_PDFDocMerged.xlsx", sheet_name="values")
master_comps_merged = master_comps_merged.drop(["doc_path", "Non_Missing", 'comp_present'], axis=1)
master_comps_merged.columns = ["doc_id"] + ["comp_merged_" + x for x in master_comps_merged.columns[1:]]
vars_comp = ["comp_present", "comp_template"] + sorted(list(master_comps_raw.columns)[3:]) + sorted(list(master_comps_merged.columns)[1:])

#merge the competencies
master_all = pd.merge(master_all, master_comps_raw, how='left', on=['doc_id'])
master_all = pd.merge(master_all, master_comps_merged, how='left', on=['doc_id'])
del master_comps_raw, master_comps_merged

CompTemplate = pd.read_excel(var_path + 'keywords.xlsx', sheet_name="competency")
CompTemplate = CompTemplate.drop('main',axis=1).sort_values('competency')
CompTemplateCounts = pd.read_excel(out_local + "/competencies/templateCounts.xlsx")
CompMergers = pd.read_excel(var_path + 'mergers.xlsx', sheet_name="competency_complete")
CompRawOverlaps = pd.read_excel(out_local + "/competencies/bigsample_competencies_PDFDocRaw_Overlaps.xlsx")
CompMergedOverlaps = pd.read_excel(out_local + "/competencies/bigsample_competencies_PDFDocMerged_Overlaps.xlsx")
CompRawCountsYear = pd.read_excel(out_local + "/competencies/bigsample_competencies_PDFDocRaw_CountsbyYear.xlsx")
CompMergedCountsYear = pd.read_excel(out_local + "/competencies/bigsample_competencies_PDFDocMerged_CountsbyYear.xlsx")

###############################
# Scorecard
###############################

#merge in scorecard
master_scorecard = pd.read_excel(out_local + "/scorecard/bigsample_scorecard_clean.xlsx", sheet_name="values")
# master_scorecard = master_scorecard[master_scorecard.columns[:-9]] #only keep up till 14
master_scorecard = master_scorecard.rename({'Outcomes_Amount':'outcomes_amount'}, axis=1)
master_scorecard.columns = ["doc_id", "sc_present"] + ["sc_" + x for x in master_scorecard.columns[2:]]
vars_scorecard = list(master_scorecard.columns)[1:]
master_all = pd.merge(master_all, master_scorecard, how='left', on=['doc_id'])
del master_scorecard

scorecard_assigned = pd.read_excel(out_local + "/scorecard/clustering/scorecard_full_finaleval.xlsx")
scorecard_assigned = scorecard_assigned[['doc_id', 'total_words', 'score_revenue', 'score_cost', 'outcome']]
scorecard_assigned.columns = ['doc_id'] + ['sc_' + x for x in scorecard_assigned.columns[1:-1]] + ['sc_type']
vars_scorecard += list(scorecard_assigned.columns[1:])
master_all = pd.merge(master_all, scorecard_assigned, how='left', on=['doc_id'])
del scorecard_assigned

scorecard_topics = pd.read_excel(out_local + "/scorecard/clustering/scorecard_finalclean.xlsx")
vars_scorecard += list(scorecard_topics.columns[1:])
master_all = pd.merge(master_all, scorecard_topics, how='left', on=['doc_id'])
del scorecard_topics

vars_scorecard1dig = [x for x in vars_scorecard if re.search("\\D\\d{1}\\D", x)]
vars_scorecard2dig = [x for x in vars_scorecard if re.search("\\d{2}", x)]
vars_scorecard = ['sc_present', 'sc_outcomes_amount', 'sc_total_words', 'sc_score_revenue', 'sc_score_cost', 'sc_type'] + sorted(vars_scorecard1dig) + sorted(vars_scorecard2dig)
del vars_scorecard1dig, vars_scorecard2dig

ScorecardResults = pd.read_excel(out_local + "scorecard/clustering/scorecard_evalresults.xlsx")
ScorecardFinalCounts = pd.read_excel(out_local + "scorecard/clustering/scorecard_finalcleanCounts.xlsx")


###############################
# Order
###############################

vars_all = vars_info + vars_gender + vars_college + vars_career + vars_comp + vars_scorecard
master_all = master_all[vars_all]




#############################################################################
#         Add flags: Duplicates, Pre2012
#############################################################################


#find number of docs per candidate-date
dup_df = master_all[['doc_id', 'candidate_firstname', 'candidate_lastname', 'date_clean']].groupby(['candidate_firstname', 'candidate_lastname', 'date_clean'], as_index=False).agg('count')
dup_df.columns = ['candidate_firstname', 'candidate_lastname', 'date_clean', 'num_docs']
dup_counts = dup_df['num_docs'].value_counts()

#add back into master_all
master_clean = pd.merge(master_all, dup_df, on =['candidate_firstname', 'candidate_lastname', 'date_clean'], how='left')
del dup_df

#duplicates will be dummy variable equal to 1 if there exists another interview of the same candidate_firstname - candidate_lastname - date with more available variables
master_clean['vars_available'] = master_clean.apply(lambda x: x.notnull().sum(), axis='columns')
master_clean = master_clean.sort_values(by=['candidate_firstname', 'candidate_lastname', 
                                            'date_clean', 'vars_available'], ascending = False)
master_clean['is_duplicate'] = [int(x) for x in master_clean.duplicated(subset=['candidate_firstname', 'candidate_lastname', 'date_clean'], keep='first')]

vars_info.extend(['is_duplicate', 'num_docs'])




#############################################################################
#         Order and Save
#############################################################################

#order columns
vars_all = vars_info + vars_gender + vars_college + vars_career + vars_comp + vars_scorecard
master_clean = master_clean[vars_all]
master_clean = master_clean.sort_values("doc_id")

master_cleanCounts = pd.DataFrame(master_clean.apply(lambda x: x.notnull().sum(), axis='index'))
master_cleanCounts.reset_index(level=0, inplace=True)
master_cleanCounts.columns = ["variable", "count"]

#write to excel
with pd.ExcelWriter(out_local + "extractions.xlsx") as writer:
    master_clean.to_excel(writer, sheet_name="Values", index=False)
    master_cleanCounts.to_excel(writer, sheet_name="Counts", index=False)
    CompanyFinalCounts.to_excel(writer, sheet_name="CompanyCounts", index=False)
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

















