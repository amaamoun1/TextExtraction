# -*- coding: utf-8 -*-

#change the working directory to be TextExtraction
import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")
os.getcwd() #double-check


#import the relevant python libraries
import pandas as pd
import re


#############################################################################
#         file locations
#############################################################################


out_local = "C:/Users/Asser.Maamoun/Documents/TextExtraction/output/"
var_path = "C:/Users/Asser.Maamoun/Documents/TextExtraction/variables/"

interview_folder_path = "C:/Users/Asser.Maamoun/Documents/Interviews"
converted_folder_path = "C:/Users/Asser.Maamoun/Documents/ConvertedInterviews"
pre2012_folder_path = "C:/Users/Asser.Maamoun/Documents/Pre2012Docs"


#############################################################################
#        Get a list of all the PDFs
#############################################################################


# Step 1: Get a list of all the original interview docs
interview_docs = [os.path.join(interview_folder_path, f) for f in os.listdir(interview_folder_path) if os.path.isfile(os.path.join(interview_folder_path, f))]
converted_docs = [os.path.join(converted_folder_path, f) for f in os.listdir(converted_folder_path) if os.path.isfile(os.path.join(converted_folder_path, f))]
pre2012_docs = [os.path.join(pre2012_folder_path, f) for f in os.listdir(pre2012_folder_path) if os.path.isfile(os.path.join(pre2012_folder_path, f))]
all_docs = interview_docs + converted_docs + pre2012_docs

del pre2012_folder_path, converted_folder_path, interview_folder_path
del interview_docs, converted_docs, pre2012_docs


#Step 2: Loop over and get corresponding .docx files and .pdf files
#This is done to ensure that docids are the same across pdfs and docx code
doc_paths = []
docx_paths = []
pdf_paths = []
txt_paths = []
for doc_id in range(len(all_docs)):
    #first read in the given document
    name = all_docs[doc_id]
    if "~$" in name:
        continue
    elif (".docx" not in name) and (".DOCX" not in name):
        doc_paths.append(name)
    else:
        docx_paths.append(name)
        pdf_path = re.sub("docx$","pdf", name, flags=re.IGNORECASE)
        txt_path = re.sub("docx$","txt", name, flags=re.IGNORECASE)
        if "ConvertedInterviews" in pdf_path:
            pdf_path = re.sub("ConvertedInterviews", "PDFs", pdf_path)
            txt_path = re.sub("ConvertedInterviews", "TXTs", txt_path)
        elif "Pre2012" in pdf_path:
            pdf_path = re.sub("Pre2012Docs", "Pre2012PDFs", pdf_path)
            txt_path = re.sub("Pre2012Docs", "Pre2012TXTs", txt_path)
        else:
            pdf_path = re.sub("Interviews", "PDFs", pdf_path)
            txt_path = re.sub("Interviews", "TXTs", txt_path)
        pdf_paths.append(pdf_path)
        txt_paths.append(txt_path)
del doc_id, name, pdf_path, txt_path

mapping_dict = {'doc_id': list(range(len(docx_paths))), 'docx_path': docx_paths, 'pdf_path':pdf_paths, 'txt_path': txt_paths}

#step 3: Save mapping as an excel file
mapping_df = pd.DataFrame(mapping_dict)
mapping_df = mapping_df.sort_values(['doc_id'])
mapping_df.to_excel(out_local + "docid_mapping.xlsx", index=False)





