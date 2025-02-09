# TextExtraction

Author: Asser Maamoun (permanent email: assermaamoun@gmail.com)  
Date: 10/01/2020  
Purpose: Extracts useful information from ghsmart interviews.  

## Run Sequence

Code should be run in this order:  
1. codes in step1_prep need to be run to  
    - convert_to_pdf.py converts the word documents into pdf documents
    - convert_to_text.r converts the pdfs into txts
    - clean_txts.py clean all the txt files of useless spaces, and other cleaning procedures
    - create_docid_mapping.py gives each document a doc_id  

2. codes in step2_extract need to be run to extract the variables of interest  
    - one file of codes per type of variable extracted
        - extract_docx.py
        - extract_docx_toc.py
        - extract_infos.py
        - extract_gender.py*
        - extract_colleges.py
        - extract_undergrad.py
        - extract_mba.py
        - extract_competencies.py
        - extract_scorecard.py
    - *you need to have run step3_finalize/finalize_infos.py before running extract_genders.py. This is because extract_genders relies on the names
	found in the interviews.

3. codes in step3_finalize need to be run to clean up the data  
    - first run finalize_infos.py
    - then run finalize_competencies.py
    - run cluster_scorecard_manual.py

4. codes in step4_combine need to be run to combine the various extractions into one workbook 
    - run combine_extractions.py    

5. codes in step5_linking need to be run to combine these extractions with the old data
    - oldvars_tokeep.xlsx has the names and indices of the columns we want to keep from the old data and their corresponding names in the extractions dataset
    - first run step1_clean_old_data.py, then step2_link_old_data.py, then step3_merge_old_data.py, then step4_anonymize_data.py, then step5_deduplicate.py
    - then you can run  find_competency_sets.py and find_teams.py
    - fuzzy_merge_functions.py holds the functions that will help identify similar companies across linkedin and ghsmart data
    - match_linkedin_companies.py executes the fuzzy merge

## FOLDERS

**college_lists** - contains code that creates the lists of colleges and business schools that we search for in the documents  

**helpers_docx** - contains code that helps us read in a docx file and extract information from it  

**helpers_general** - contains helper functions  

**helpers_txt** - contains codes that help us extract information from the txt versions of the docx interviews. These are regexes.  

**old** - old codes archived  

**step1_prep** - codes that create the docid mapping and convert the interviews to docx, pdf, and txt versions  

**step2_extract** - codes that extract information from the documents, whether in docx form or in txt form  

**step3_finalize** - codes that merge the info and competency extractions from the docx and txt methods 
	also codes that assign the scorecard topics  

**step4_combine** - codes that combine all of the extractions and other useful information into one giant workbook

**step5_linking** - codes that combine all of the extractions with the extracted data from the old interviews 
	also codes that merge in the LinkedIn variables and spot when a LinkedIn company is also in the ghSMART data
	also codes that anonymize this workbook, find teams, and common competencies included 

**variables** - excels that show which competencies and info variables we extract, and which of them we should merge  

