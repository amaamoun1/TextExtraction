# -*- coding: utf-8 -*-



import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")

#add the relevant folders of code to the system path...so that python can access all the codes
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')

from merge_functions import overlapMatRaw
from merge_functions import overlapMatPercent
from merge_functions import checkMerge
from merge_functions import merge_vars
from clean_date import cleanDate

import re
import pandas as pd
import numpy as np

#############################################################################
#         output file locations
#############################################################################


out_local_docx = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/docx/"
out_local_pdf = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/infos/"
out_folder = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


###############################################################################
#    Compare results from docx and string methods
###############################################################################


############################################
#  Create comparable datasets
############################################

#read in the docx version and the pdf merged versions
master_docx = pd.read_excel(out_local_docx + "bigsample_infocompetency_raw.xlsx", sheet_name="values")
master_pdf = pd.read_excel(out_local_pdf + "bigsample_infos_raw.xlsx", sheet_name="values")

#subset only the variables in both sets
vars_to_compare = [x for x in master_pdf.columns if (x in master_docx.columns) & (x != "Non_Missing")]
master_pdf = master_pdf[vars_to_compare]
master_docx = master_docx[vars_to_compare]

#recreate counts
master_pdf['Non_Missing'] = len(master_pdf.columns) - 2 - master_pdf.apply(lambda x: x.isnull().sum(), axis='columns')
master_docx['Non_Missing'] = len(master_docx.columns) - 2 - master_docx.apply(lambda x: x.isnull().sum(), axis='columns')


############################################
#  Create dataframes on differences
############################################

# -1 = pdf not docx ; 0 is agree ; 1 = docx not pdf
master_diff = master_pdf.copy()
for x in master_pdf.columns:
    if x in master_pdf.columns[2:-1]:
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
master_pdf = pd.read_excel(out_local_pdf + "bigsample_infos_raw.xlsx", sheet_name="values")

#subset only the variables in both sets
vars_to_compare = [x for x in master_pdf.columns if (x != "Non_Missing")] 
master_pdf = master_pdf[vars_to_compare]
master_docx = master_docx[[x for x in master_docx.columns if x in vars_to_compare]]


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
    for x in master_pdf.columns[2:-1]:
        if x in master_docx.columns[2:-1]:
            if (pd.isnull(new_row[x])) & (pd.notnull(row_d[x])):
                new_row[x] = row_d[x]
                new_row['info_present'] = 1
                saved += 1
            elif (pd.notnull(row_d[x])) & (pd.notnull(row_p[x])) & (row_d[x] != row_p[x]):
                disagree_count += 1
                new_row[x] = row_p[x] #keep pdf version due to simplicity
                if ("purpose" in x) or ("reccommendation" in x): #keep docx because it keeps mult lines
                    new_row[x] = row_d[x]
                curr = row_p[x] + "_" + row_d[x]
                if row_p['doc_path'] in disagree_loc:
                    disagree_loc[row_p['doc_path']].append(x + "_" + curr)
                else:
                    disagree_loc[row_p['doc_path']] = [x + "_" + curr]
                if x in disagree_dict:
                    disagree_dict[x] +=1
                else:
                    disagree_dict[x] = 1
    new_rows.append(new_row)
master_all = pd.DataFrame(new_rows)
del i, new_rows, row_d, row_p, new_row, x, doc_id, curr

#Add counts
master_all['Non_Missing'] = len(master_all.columns) - 4 - master_all.apply(lambda x: x.isnull().sum(), axis='columns')
master_docx['Non_Missing'] = len(master_docx.columns) - 3 - master_docx.apply(lambda x: x.isnull().sum(), axis='columns')
master_pdf['Non_Missing'] = len(master_pdf.columns) - 4 - master_pdf.apply(lambda x: x.isnull().sum(), axis='columns')

#double check should equal saved
print("Check that saved", saved, "equals", sum(master_all['Non_Missing'] - master_pdf['Non_Missing']))




############################################
#  Counts and Save
############################################

#create counts of the merged variables
master_allCounts = pd.DataFrame(len(master_all) - master_all.apply(lambda x: x.isnull().sum(), axis='rows'))
master_allCounts.sort_values(0, ascending=False, inplace=True)
master_allCounts = master_allCounts.drop('Non_Missing', axis=0)

#write to excel
with pd.ExcelWriter(out_local_pdf + "bigsample_infos_PDFDocRaw.xlsx") as writer:
    master_all.to_excel(writer, sheet_name="values", index=False)
    master_allCounts.to_excel(writer, sheet_name="counts")
del writer

del disagree_count, disagree_dict, disagree_loc 
del master_all, master_allCounts, master_diff, master_docx, master_pdf
del master_onlyDOCX, master_onlyPDF, saved, vars_to_compare

###############################################################################
# Merge together variables
###############################################################################



master_all = pd.read_excel(out_local_pdf + "bigsample_infos_PDFDocRaw.xlsx", sheet_name="values")

#get overlapping matrix and get a raw and percent version
overlaps_raw = overlapMatRaw(master_all)
overlaps_percent = overlapMatPercent(overlaps_raw)



############################################
#  Perform the merge
############################################


#if candidate and candidate name present, then candidate is really position
master_dict = master_all.to_dict('records')
new_dict = []
for infos in master_dict:
    if pd.notnull(infos['candidate']) and pd.notnull(infos['candidate name']):
        if pd.notnull(infos['position']) or pd.notnull(infos['title']):
            print("did not merge candidate to position:", infos['doc_path'])
            infos['candidate'] = np.nan
            new_dict.append(infos)
            continue
        infos['position'] = infos['candidate']
        infos['candidate'] = np.nan
    new_dict.append(infos)
master_updated = pd.DataFrame(new_dict)

#get overlapping matrix and get a raw and percent version
overlaps_raw = overlapMatRaw(master_updated)
overlaps_percent = overlapMatPercent(overlaps_raw)

#load the variables to merge
mergers_df = pd.read_excel(var_path + 'mergers.xlsx', sheet_name="info_complete")

#create a dictionary of variables that we can merge
mergers_dict = checkMerge(master_updated, overlaps_raw, mergers_df)
del mergers_df

#merge together the non-overlapping variables in master_merged
master_merged = master_updated.copy()
for name in mergers_dict.keys():
    master_merged = merge_vars(master_merged, mergers_dict[name], name)
del name, mergers_dict

##########################
#           Save
##########################

#create counts of the merged variables
master_mergedCounts = pd.DataFrame(len(master_merged) - master_merged.apply(lambda x: x.isnull().sum(), axis='rows'))
master_mergedCounts.sort_values(0, ascending=False, inplace=True)
master_mergedCounts = master_mergedCounts.drop('Non_Missing', axis=0)

#write the cleaned ratings and counts to local
with pd.ExcelWriter(out_local_pdf + "bigsample_infos_PDFDocMerged.xlsx") as writer:
    master_merged.to_excel(writer, sheet_name="values", index=False)
    master_mergedCounts.to_excel(writer, sheet_name="counts")
del writer

del infos, master_all, master_dict, master_merged, master_mergedCounts
del master_updated, new_dict, overlaps_percent, overlaps_raw

###############################################################################
# Clean Variables
###############################################################################

master_merged = pd.read_excel(out_local_pdf + "bigsample_infos_PDFDocMerged.xlsx", sheet_name="values")



############################################
#  Clean Date
############################################

#Date entry
#cleanDate(["2/14/2015", "2/14/15", "tuesday february 14, 2015", "14th february, 2015"], clean_obs)
master_clean = master_merged.copy()

#manual
master_clean['date'].replace("xx", np.nan, inplace=True)
master_clean['date'].replace("nov 23d 2004", "2004-11-23", inplace=True)
master_clean['date'].replace("july10 2003", "2003-07-10", inplace=True)
master_clean['date'].replace("april111 2005", "2005-04-11", inplace=True)
master_clean['date'].replace("march10 2006", "2006-03-10", inplace=True)
master_clean['date'].replace("sept15 2007", "2007-09-15", inplace=True)
master_clean['date'].replace("9/24/2018september 24 2018", "2018-09-24", inplace=True)
master_clean['date'].replace("september 4 and 6 2019", "2019-09-06", inplace=True)
master_clean = master_clean.rename({'date':'date_raw'},axis=1)
#function
master_clean['date_clean'] = cleanDate(master_clean['date_raw'])


############################################
#  Clean filename
############################################

#grab just the file name
master_clean['doc_name'] = master_clean['doc_path'].apply(lambda x: re.sub("^.*[\\/\\\\]", "",x))

#flag for pre-2012 sample
master_clean['is_pre2012'] = master_clean['doc_path'].apply(lambda x: int("Pre2012PDFs" in x))

############################################
#  Clean info rating
############################################


#rating entry
def clean_rating(entry):
    # print(entry)
    if pd.isnull(entry):
        return np.nan
    rating = np.nan
    find_rating = re.match("^\\s*(a|b|c){1}\\s*(\\+|\\-)?(?:[^a-z].*)*$", entry, flags=re.DOTALL) #also grabs the suffix i.e."+\-"
    if find_rating:
        rating=find_rating.group(1)
        suffix = find_rating.group(2)
        if suffix:
            rating= rating + suffix
    return rating

master_clean["rating_cleaned"] = master_clean["rating"].apply(clean_rating)



############################################
#  Clean Company Name
############################################


#look at the company names and possible misnames
company_counts = pd.DataFrame(master_clean['company name'].value_counts())
company_counts.reset_index(level=0, inplace=True)
company_counts.columns = ['company name', 'count']
company_counts = company_counts.sort_values('company name')
company_counts.to_excel(out_folder + "companies/CompanyRawCounts.xlsx", sheet_name="raw", index=False)

#clean company names...CompanyRawCleaned tries to unify spelling for all companies in CompanRawCounts
clean_companies_link = pd.read_excel(out_folder + "companies/CompanyFinalLinks.xlsx")

#add the company flags
def combine_flags(row):
    if pd.notnull(row['steve']):
        return row['steve']
    elif pd.notnull(row['morten']):
        return row['morten']
    else: #this picks up firms that I did not assign a company_clean to due to odd results
        return 3
company_flags = pd.read_excel(out_folder + "companies/CompanyFlagsUpdated.xlsx")
company_flags.columns = ['company_clean', 'morten', 'steve']
clean_companies_link = clean_companies_link.merge(company_flags, how='outer', on='company_clean')
clean_companies_link['company_flag'] = clean_companies_link.apply(combine_flags, axis=1)
clean_companies_link = clean_companies_link[['company name', 'company_clean', 'company_flag']]
clean_companies_link = clean_companies_link[[pd.notnull(x) for x in clean_companies_link['company name']]].copy()

#replace the company name with the cleaned version
master_clean = master_clean.merge(clean_companies_link, how='left')
master_clean = master_clean.rename({"company name": "company_raw"}, axis=1)
master_clean['company_flag'] = master_clean['company_flag'].fillna(-1)
clean_companies_counts = master_clean[["company_clean", "company_raw"]].copy()
clean_companies_counts = clean_companies_counts.groupby('company_clean', as_index=False).count()
clean_companies_counts.columns = ['company_clean', 'count']
clean_companies_counts = clean_companies_counts.merge(master_clean[['company_clean', 'company_flag']].drop_duplicates(), how='left')
clean_companies_counts.to_excel(out_folder + "companies/CompanyFinalCounts.xlsx", index=False)
del company_counts, clean_companies_link, clean_companies_counts, company_flags


############################################
#  Clean Title
############################################

def clean_title(title):
    if pd.isnull(title):
        return title
    #cleans some systematic issues before manual cleaning
    #clear punctuation
    title = re.sub(" & ", " and ", title)
    title = re.sub("&"," and ", title)
    #title = re.sub("[^\sa-z]",",", title)
    #clear accidental (or smart tag) inclusion of "title"
    title = re.sub("^title", "", title)
    title = re.sub("title$", "", title)
    title = re.sub("candidate: ", "", title)
    #abbreviations
    title = re.sub("chief executive officer", "ceo", title)
    title = re.sub("chief financial officer", "cfo", title)
    title = re.sub("chief operating officer", "coo", title)
    title = re.sub("senior vice president", "svp", title)
    title = re.sub("vice president", "vp", title)
    title = re.sub("managing director", "md", title)
    
    return title

#look at the company names and possible misnames
master_clean['title'] = [clean_title(x) for x in master_clean['title']]
title_counts = pd.DataFrame(master_clean['title'].value_counts())
title_counts.reset_index(level=0, inplace=True)
title_counts.columns = ['title', 'count']
title_counts = title_counts.sort_values('title')
title_counts.to_excel(out_folder + "titles/TitlesCounts.xlsx", sheet_name="raw", index=False)


#merge
clean_titles = pd.read_excel(out_folder + "titles/TitlesFinalCleaned.xlsx")
master_clean = master_clean.merge(clean_titles, how='left', on='title')
master_clean = master_clean.rename({'title':'title_raw'} ,axis=1)

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
TitleFinalCounts.to_excel(out_folder + "titles/TitleFinalCounts.xlsx", index=False)

del clean_titles, title_counts, titles, TitleFinalCounts, t


############################################
#  Prepared_by
############################################

#first do some basic cleaning on the column
prepby_clean1 = []
for x in master_clean['prepared by']:
    if pd.notnull(x):
        x = re.sub("&", " and ", str(x))
        x = re.sub("\\.", "", x)
        x = re.sub("\\/"," and ", x)
        x = re.sub("\\bphd\\b","", x)
        x = re.sub("\\bph d\\b", "", x)
        x = re.sub("\\s+", " ", x)
    prepby_clean1.append(x)
prepby_clean1 = pd.DataFrame(prepby_clean1, columns=['prepared_by'])


#find a first approximation of counts and who is included
prepby_dict1={}
for x in prepby_clean1['prepared_by']:
    if pd.notnull(x):
        people = x.split(" and ")
        for p in people:
            if p not in prepby_dict1:
                prepby_dict1[p] = 1
            else:
                prepby_dict1[p] += 1
prepby_counts1 = pd.DataFrame(prepby_dict1.items(), columns = ["prepared_by", "count"])
prepby_counts1 = prepby_counts1.sort_values('prepared_by')
prepby_counts1.to_excel(out_folder + "prepby/prepby_counts1.xlsx", index=False)
del p, people, x

#put the manual fixes into a dictionary of original_naming -> true_name
prepby_fixed = pd.read_excel(out_folder + "prepby/prepby_counts1_edited.xlsx")
prepby_fixes = {}
for i, row in prepby_fixed.iterrows():
    if pd.isnull(row['prepby_2']) and pd.notnull(row['prepby_1']):
        prepby_fixes[row['prepared_by']] = row['prepby_1']

#merge the fixes back into the datadrame with 1 row per docid
#and uses the dictionary in case of multiple people listed
prepby_clean2 = prepby_clean1.merge(prepby_fixed, how='left')
new_rows = []
for i, row in prepby_clean2.iterrows():
    if pd.isnull(row['prepared_by']):
        new_rows.append(row)
    elif pd.notnull(row['prepby_1']):
        new_rows.append(row)
    else:
        split = row['prepared_by'].split(" and ")
        total = 0
        for person in split:
            if person in prepby_fixes:
                total += 1
                col = "prepby_" + str(total)
                clean = prepby_fixes[person]
                row[col] = clean
        new_rows.append(row)
prepby_clean2 = pd.DataFrame(new_rows)
del new_rows, i, row, split, total, person, col, clean

#combines the separated prepby columns into one column 
prepby_clean3 = []
for i, row in prepby_clean2.iterrows():
    if pd.notnull(row['prepby_3']):
        row['prepby_all'] = " AND ".join([row['prepby_1'], row['prepby_2'], row['prepby_3']])
    elif pd.notnull(row['prepby_2']):
        row['prepby_all'] = " AND ".join([row['prepby_1'], row['prepby_2']])
    else:
        row['prepby_all'] = row['prepby_1']
    prepby_clean3.append(row)
prepby_clean3 = pd.DataFrame(prepby_clean3)
del i, row

#outputs the final names to ensure we don't accidentally have the same person twice
prepby_dict3={}
for x in prepby_clean3['prepby_all']:
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
prepby_counts3.to_excel(out_folder + "prepby/prepby_counts3.xlsx", index=False)



#after double checking prepby_counts3, merge in our cleaned data
master_clean['prepared_by_clean'] = prepby_clean3['prepby_all']
master_clean = master_clean.rename({'prepared by': 'prepared_by_raw'}, axis=1)
prepby_countsFinal = prepby_counts3[['prepared_by_clean', 'count']]
prepby_countsFinal.to_excel(out_folder + "prepby/prepby_countsFinal.xlsx", index=False)

del prepby_clean1, prepby_clean2, prepby_clean3, prepby_counts1, prepby_counts3
del prepby_countsFinal, prepby_dict1, prepby_dict3, prepby_fixed, prepby_fixes


############################################
#  Clean and Separate Candidate Name
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

def grab_first(x):
    return re.sub(" .*$", "", x)

def grab_last(x):
    for y in name_suffixes:
        x = re.sub("\\b" + y + "\\b", "", x)
    x = re.sub("\\s+", " ", x) #make all whitespace a space
    x = x.strip() #trim leading and trailing whitespace
    return re.sub("^.* ", "", x)

#look at the candidate names
name_counts = pd.DataFrame(master_clean['candidate name'].value_counts())
name_counts.reset_index(level=0, inplace=True)
name_counts.columns = ['candidate name', 'count']
name_counts = name_counts.sort_values('candidate name')
name_counts['candidate_name_clean'] = name_counts['candidate name'].apply(clean_name)
name_counts['candidate_firstname'] = name_counts['candidate_name_clean'].apply(grab_first)
name_counts['candidate_lastname'] = name_counts['candidate_name_clean'].apply(grab_last)
name_counts.to_excel(out_folder + "names/NameRawCounts.xlsx", sheet_name="raw", index=False)

name_countsClean = pd.read_excel(out_folder + "names/NameRawCounts_edited.xlsx")
name_countsClean = name_countsClean.drop("count", axis=1)
master_clean = master_clean.merge(name_countsClean, how='left')
master_clean = master_clean.rename({'candidate name':'candidate_name_raw'}, axis=1)


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
    
master_clean = master_clean.rename({'purpose of this assessment':'purpose_raw'}, axis=1)
purpose_counts1 = master_clean['purpose_raw'].value_counts().reset_index()
purpose_counts1.columns = ['purpose_raw', 'count']
purpose_counts1['purpose_clean'] = purpose_counts1['purpose_raw'].apply(evaluate_purpose)
purpose_counts1 = purpose_counts1.sort_values('purpose_raw')
purpose_counts1.to_excel(out_folder + "/purpose/purpose_counts1.xlsx", index=False)

master_clean['purpose_clean'] = master_clean['purpose_raw'].apply(evaluate_purpose)

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
master_purposeCounts.to_excel(out_folder + "purpose/PurposeFinalCounts.xlsx", sheet_name="raw", index=False)

############################################
#  Counts and Overlaps on merged data
############################################

#create counts of the merged variables
master_clean.columns = [x.replace(" ", "_") for x in master_clean.columns]
master_cleanCounts = pd.DataFrame(len(master_clean) - master_clean.apply(lambda x: x.isnull().sum(), axis='rows'))
master_cleanCounts.sort_values(0, ascending=False, inplace=True)
master_cleanCounts = master_cleanCounts.drop('Non_Missing', axis=0)



##############################################################################
#           Save
##############################################################################

#write the cleaned ratings and counts to local
with pd.ExcelWriter(out_local_pdf + "bigsample_infos_PDFDocFinal.xlsx") as writer:
    master_clean.to_excel(writer, sheet_name="values", index=False)
    master_cleanCounts.to_excel(writer, sheet_name="counts")
del writer











