import pandas as pd
import numpy as np

#manual duplicates from morten
data = pd.read_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\extractions_merged.xlsx")
dups = pd.read_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\PossibleDuplicates.2021-05-19.xlsx")
dups = dups[['duplicate_group', 'doc_id_old', 'doc_id_new']]
dups = dups.merge(data, how='left')
dups.to_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\PossibleDuplicates.2021-05-19.merged.xlsx", index=False)


#SET UP DATA
data = pd.read_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\extractions_merged.xlsx")
data = data[data['is_duplicate']==0]
merged_comps = [x for x in data.columns if "comp_merged_" in x]
data['vars_available'] = data[merged_comps].apply(lambda x: x.notnull().sum(), axis='columns')

#check duplicates using merged competency scores
dups1 = data[data.duplicated(subset=merged_comps, keep=False)]
dups1 = dups1[dups1['vars_available']>=20]
dups1 = dups1.drop('vars_available', axis=1)
dups1['group'] = dups1.groupby(by=merged_comps, dropna=False).ngroup()
dups1['method'] = 'competencies'

#check duplicates using date and interviewer
dups2 = data[data.duplicated(subset=['date_clean', 'prepared_by_clean'], keep=False)]
dups2 = dups2[[pd.notnull(x) for x in dups2['date_clean']]]
dups2 = dups2[[pd.notnull(x) for x in dups2['prepared_by_clean']]]
max_vars = dups2.groupby(['date_clean','prepared_by_clean'])['vars_available'].max().reset_index().rename({'vars_available':'vars_available_max'}, axis=1)
dups2 = dups2.merge(max_vars, how='left', on=['date_clean', 'prepared_by_clean'])
dups2 = dups2[dups2['vars_available_max']>=20]
dups2 = dups2.drop(['vars_available', 'vars_available_max'], axis=1)
dups2['group'] = dups2.groupby(by=['date_clean', 'prepared_by_clean'], dropna=False).ngroup()
dups2['method'] = 'date_interviewer'

#check duplicates using title and company
dups3 = data[data.duplicated(subset=['title_clean', 'company_clean'], keep=False)]
dups3 = dups3[[pd.notnull(x) for x in dups3['title_clean']]]
dups3 = dups3[[pd.notnull(x) for x in dups3['company_clean']]]
dups3 = dups3[[(x==1 or x==3) for x in dups3['company_flag']]]
max_vars = dups3.groupby(['title_clean','company_clean'])['vars_available'].max().reset_index().rename({'vars_available':'vars_available_max'}, axis=1)
dups3 = dups3.merge(max_vars, how='left', on=['title_clean', 'company_clean'])
dups3 = dups3[dups3['vars_available_max']>=20]
dups3 = dups3.drop(['vars_available', 'vars_available_max'], axis=1)
dups3['group'] = dups2.groupby(by=['title_clean', 'company_clean'], dropna=False).ngroup()
dups3['method'] = 'titleComp'

#combine all duplicates that make sense to check
dups_all = pd.concat([dups1, dups2])
dups_all['comps_available'] = dups_all[merged_comps].apply(lambda x: x.notnull().sum(), axis='columns')
dups_all['vars_available'] = dups_all.apply(lambda x: x.notnull().sum(), axis='columns')

dups_all = dups_all[list(dups_all.columns[-4:]) + list(dups_all.columns[:-4])]
dups_all.to_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\possible_duplicates_yann.xlsx", index=False)



######################
# this helps check the duplicates that morten found using the factor scores and company names

dups = pd.read_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\possible_dups_20210723.xlsx")
candidates = pd.read_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\extractions_merged.xlsx")

dups_merged = dups.merge(candidates, how="left")
dups_merged.to_excel(r"C:\Users\asser.maamoun\Documents\TextExtraction\output\possible_dups_20210723_merged.xlsx", index=False)