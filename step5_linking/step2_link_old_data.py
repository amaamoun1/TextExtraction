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

import pandas as pd
import re
import numpy as np

#############################################################################
#         File locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


#############################################################################
#    Import Data
#############################################################################

#load current dataset
master_clean = pd.read_excel(out_local + "extractions.xlsx", sheet_name = "Values")
master_clean = master_clean[['doc_id', 'doc_name', 'is_pre2012', 'candidate_name_raw',
                             'candidate_name_clean', 'candidate_firstname', 
                             'candidate_lastname', 'date_clean', 'is_duplicate']]
master_clean['doc_name'] = master_clean['doc_name'].apply(lambda x: re.sub("(\\.pdf|\\.doc|\\.docx)+$", "", x.lower()))
#master_pre2012 = master_clean[master_clean['is_pre2012'] == 1]

# load the previous dataset
master_old = pd.read_excel(out_local + "/linking_pastdata/master_old_clean.xlsx")
master_old = master_old[['doc_id_old', 'candidate_name_raw', 'candidate_firstname', 
                         'candidate_lastname', 'duplicate', 'date_clean', 'doc_name_old']]
master_old['doc_name'] = master_old['doc_name_old'].apply(lambda x: re.sub("(\\.pdf|\\.doc|\\.docx)+$", "", x.lower()))
#master_old = master_old[master_old['duplicate']==0]
#master_old = master_old.drop('duplicate', axis=1)

#############################################################################
#    Merge Data
#############################################################################


# merge on the docname - date
master_old_dups_doc = master_old[master_old.duplicated(subset='doc_name', keep=False)].copy()
master_merged_doc = master_clean.merge(master_old, how='inner', on=['doc_name', 'date_clean'])
master_old_unmerged_doc = master_old[[x not in list(master_merged_doc['doc_name']) for x in master_old['doc_name']]].copy()

# merge on raw candidate name - date
master_old_unmerged_doc = master_old_unmerged_doc.rename({'doc_name':'doc_name_old_clean'}, axis=1)
master_old_dups_fullnamedate = master_old_unmerged_doc[master_old_unmerged_doc.duplicated(subset=['candidate_name_raw'], keep=False)]
master_merged_fullnamedate = master_clean.merge(master_old_unmerged_doc, how='inner', 
                                                   on=['candidate_name_raw', 'date_clean'])
master_old_unmerged_fullnamedate = master_old_unmerged_doc[[x not in list(master_merged_fullnamedate['doc_name_old_clean']) for x in master_old_unmerged_doc['doc_name_old_clean']]].copy()

# merge on candidate first and last name - date
master_old_dups_name = master_old_unmerged_fullnamedate[master_old_unmerged_fullnamedate.duplicated(subset=['candidate_firstname', 'candidate_lastname'], keep=False)]
master_merged_namedate = master_clean.merge(master_old_unmerged_fullnamedate, how='inner', 
                                                   on=['candidate_firstname', 'candidate_lastname', 'date_clean'])
master_old_unmerged_namedate = master_old_unmerged_fullnamedate[[x not in list(master_merged_namedate['doc_name_old_clean']) for x in master_old_unmerged_fullnamedate['doc_name_old_clean']]].copy()


# merge on candidate first and last name
master_old_dups_name = master_old_unmerged_namedate[master_old_unmerged_namedate.duplicated(subset=['candidate_firstname', 'candidate_lastname'], keep=False)]
master_merged_name = master_clean.merge(master_old_unmerged_namedate, how='inner', 
                                                   on=['candidate_firstname', 'candidate_lastname'])
master_old_unmerged_name = master_old_unmerged_namedate[[x not in list(master_merged_name['doc_name_old_clean']) for x in master_old_unmerged_namedate['doc_name_old_clean']]].copy()

#double check that the merge on name only is valid when comparing dates
master_merged_name.to_excel(out_local + "/linking_pastdata/check_namemerge.xlsx", index=False)
master_merged_name = pd.read_excel(out_local + "/linking_pastdata/check_namemerge_edited.xlsx")
master_merged_name = master_merged_name[master_merged_name['keep']==1]
master_merged_name = master_merged_name.drop('keep', axis=1)

#############################################################################
#    Combine and Clean Merges
#############################################################################

master_merged_all = pd.concat([master_merged_doc, master_merged_fullnamedate, master_merged_namedate, master_merged_name], ignore_index=True, join='inner')
master_merged_all = master_merged_all[['doc_id', 'doc_id_old']].sort_values('doc_id').reset_index(drop=True)
master_merged_all.to_excel(out_local + "/linking_pastdata/DOCID_to_ID.xlsx", index=False)


