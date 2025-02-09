# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 19:23:51 2021

@author: Asser.Maamoun
"""

#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
import sys
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/step5_linkedin')
sys.path.insert(1, 'C:/Users/Asser.Maamoun/Documents/TextExtraction/helpers_general')

import pandas as pd
import numpy as np
import re

#############################################################################
#         File locations
#############################################################################

out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"


master_career = pd.read_excel(out_local + "scraping\scrape_success.xlsx")
master_career = master_career[['doc_id_old', 'doc_id_new', 'linkedin_url', 'linkedin_info', 'company_linkedin', 
                               'hired', 'hired_start', 'hired_end', 'tenure_before',
                               'tenure_after', 'flag', 'past_ceo', 
                               'past_cfo', 'future_ceo', 'future_cfo']]
career_columns = ['linkedin_url', 'linkedin_info', 'company_linkedin', 
                               'hired', 'hired_start', 'hired_end', 'tenure_before',
                               'tenure_after', 'career_flag', 'past_ceo', 
                               'past_cfo', 'future_ceo', 'future_cfo']
master_career.columns = ['doc_id_old', 'doc_id_new'] + career_columns 

career_manual = pd.read_excel(out_local + "scraping\manual_search2_neil_2.xlsx")

career_manual['career_info']
career_manual