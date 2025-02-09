# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 21:13:23 2020

@author: Asser.Maamoun
"""

#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linkedin')

from fuzzy_merge_functions import clean_company
from fuzzy_merge_functions import fuzzy_merge_keepbest
from fuzzy_merge_functions import fuzzy_merge_keepthreshold

from datetime import date
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

master_clean = pd.read_excel(out_local + "extractions.xlsx", sheet_name = "Values")
linkedin_data = pd.read_excel(out_local + "CleanedLinkedInPost2012.xlsx")

# index_abbreviated = [(pd.notnull(x) and len(x)<=5) for x in master_clean['company_clean']]
# abbreviated_companies = master_clean[index_abbreviated][['doc_id', 'doc_name', 'is_pre2012', 'company_raw','company_clean']]
# abbreviated_companies = abbreviated_companies.sort_values('company_clean')
# abbreviated_companies.to_excel(out_local + "fuzzy_merge/abbreviated_firms.xlsx", index=False)
# len(set(abbreviated_companies['company_clean']))

#############################################################################
#    Clean Companies
#############################################################################

ghsmart_companies = pd.DataFrame([x for x in set(master_clean['company_clean']) if pd.notnull(x)], columns=['ghsmart_unclean'])
ghsmart_companies['ghsmart_clean'] = ghsmart_companies['ghsmart_unclean'].apply(clean_company)
ghsmart_companies.to_excel(out_local + "fuzzy_merge/cleaning_ghsmart.xlsx", index=False)


linkedin_companies = pd.DataFrame(set([x.strip().lower() for x in set(linkedin_data['Company Name']) if pd.notnull(x)]), columns=['linkedin_unclean'])
linkedin_companies['linkedin_clean'] = linkedin_companies['linkedin_unclean'].apply(clean_company)
linkedin_companies.to_excel(out_local + "fuzzy_merge/cleaning_linkedin.xlsx", index=False)



#############################################################################
#    Match Companies
#############################################################################

ghsmart_tosearch = list(set(ghsmart_companies['ghsmart_clean']))
linkedin_tocheck = list(set(linkedin_companies['linkedin_clean']))

result = fuzzy_merge_keepbest(ghsmart_tosearch, linkedin_tocheck, num_keep=50)

result = result.rename({'input_name':'ghsmart_clean', 'match_name':'linkedin_clean'}, axis=1)
result = result.merge(ghsmart_companies, how='left')
result = result.merge(linkedin_companies, how='left')
result_max_score = result.groupby(['ghsmart_clean'], as_index=False)['match_score'].max()
result_max_score.columns = ['ghsmart_clean', 'best_score']
result = result.merge(result_max_score, how='left')
result['match_start_perc'] = result['match_score'].apply(lambda x: (x//10000000)/100)
result['match_total_perc'] = result['match_score'].apply(lambda x: ((x//10000)%1000) /100)
result['match_jarowinkler'] = result['match_score'].apply(lambda x: (x%10000)/1000)
result = result[['ghsmart_clean', 'linkedin_clean', 'best_score', 'match_rank', 'match_score',
                 'match_start_perc', 'match_total_perc', 'match_jarowinkler',
                 'ghsmart_unclean', 'linkedin_unclean']]
result = result.sort_values(['match_score'], ascending=False)
result.to_excel(out_local + "fuzzy_merge/fuzzy_merge_keep50.xlsx", index=False)


