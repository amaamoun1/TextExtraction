# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 00:28:21 2019

@author: Asser.Maamoun
"""

import os
os.chdir(r"C:\Users\Asser.Maamoun\Documents\TextExtraction")

import re
import win32com.client as win32
from win32com.client import constants
from datetime import datetime
from pytz import timezone



#############################################################################
#         Find the number of  files and save their paths
#############################################################################


#check the interview folder and the folder with doc converted to docx
interview_folder_path = "C:/Users/Asser.Maamoun/Documents/Interviews"
converted_folder_path = "C:/Users/Asser.Maamoun/Documents/ConvertedInterviews"
interview_docs = [os.path.join(interview_folder_path, f) for f in os.listdir(interview_folder_path) if os.path.isfile(os.path.join(interview_folder_path, f))]
converted_docs = [os.path.join(converted_folder_path, f) for f in os.listdir(converted_folder_path) if os.path.isfile(os.path.join(converted_folder_path, f))]
all_docs = interview_docs + converted_docs

# interview_folder_path = "C:/Users/Asser.Maamoun/Documents/Pre2012Docs"
# all_docs = [os.path.join(interview_folder_path, f) for f in os.listdir(interview_folder_path) if os.path.isfile(os.path.join(interview_folder_path, f))]

#keep a seperate list for just the docx files
doc_paths = []
docx_paths = []
for doc_id in range(len(all_docs)):
    #first read in the given document
    name = all_docs[doc_id]
    if "~$" in name:
        continue
    elif (".docx" not in name) and (".DOCX" not in name):
        doc_paths.append(name)
    else:
        docx_paths.append(name)
print("Total documents not in docx:", len(doc_paths))
print("Total documents in docx:", len(docx_paths))

# del interview_folder_path, converted_folder_path, interview_docs, converted_docs, all_docs
del interview_folder_path, all_docs
del doc_paths, doc_id, name

#############################################################################
#         Create a funciton to automatically convert one doc
#############################################################################

wdFormatPDF = 17
  
def clear_folder(folder):
    path = "C:/Users/Asser.Maamoun/Documents/" + folder
    filelist = [f for f in os.listdir(path)]
    for f in filelist:
        os.remove(os.path.join(path, f))
        
def docx_to_pdf(docx_paths, doc_id, new_folder, word):
    path = docx_paths[doc_id]
    if "ConvertedInterviews" in path:
        path = re.sub(r"C:/Users/Asser.Maamoun/Documents/ConvertedInterviews\\", r"C:\\\\Users\\\\Asser.Maamoun\\\\Documents\\\\ConvertedInterviews\\\\", path)
        new_path = re.sub("ConvertedInterviews", new_folder, path)
    elif "Pre2012Docs" in path:
        path = re.sub(r"C:/Users/Asser.Maamoun/Documents/Pre2012Docs\\", r"C:\\\\Users\\\\Asser.Maamoun\\\\Documents\\\\Pre2012Docs\\\\", path)
        new_path = re.sub("Pre2012Docs", new_folder, path)
    else:
        path = re.sub(r"C:/Users/Asser.Maamoun/Documents/Interviews\\", r"C:\\\\Users\\\\Asser.Maamoun\\\\Documents\\\\Interviews\\\\", path)
        new_path = re.sub("Interviews", new_folder, path)
    new_path = re.sub("docx$", "pdf", new_path, flags=re.IGNORECASE)
    #open
    doc = word.Documents.Open(path)
    doc.Activate()
    #save and close
    word.ActiveDocument.SaveAs(new_path, FileFormat=wdFormatPDF)
    doc.Close(SaveChanges=False)
    return new_path

#############################################################################
#         Loop over and convert the .doc files
#############################################################################

# clear_folder("Pre2012PDFs")

pdf_paths = []
# word = win32.gencache.EnsureDispatch('Word.Application')
word = win32.Dispatch('Word.Application')
for doc_id in range(len(docx_paths)):
    pdf_path = docx_to_pdf(docx_paths, doc_id, "PDFs", word)
    pdf_paths.append(pdf_path)
    if doc_id % 100 == 0:
        chi_time = datetime.now(timezone('America/Chicago'))
        print(doc_id, "parsing at", chi_time.strftime('%H:%M:%S'))
word.Quit()  
    
    
    