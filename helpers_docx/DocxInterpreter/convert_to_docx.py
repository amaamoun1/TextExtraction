# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 00:28:21 2019

@author: Asser.Maamoun
"""

import os
import re
import win32com.client as win32
from win32com.client import constants

#%cd C:\Users\amaamoun\Desktop\Kaplan\TextExtraction

#select all of the documents to parse
#NOTE: the following files were found as .docx files but, in reality, 
#   were .doc file. So I had manually changed their extension back to .doc
#   so that the converter will identify them properly:
#   "noble_brian...", "noble_doak..."
interview_folder_path = "C:\\\\Users\\\\Asser.Maamoun\\\\Documents\\\\Interviews"
interview_docs = [os.path.join(interview_folder_path, f) for f in os.listdir(interview_folder_path) if os.path.isfile(os.path.join(interview_folder_path, f))]

#############################################################################
#         Find the number of doc files and save their paths
#############################################################################

doc_paths = []
non_doc_names = []
doc_names = []
docx_names=[]
for doc_id in range(len(interview_docs)):
    #first read in the given document
    path = interview_docs[doc_id]
    name = path.replace("C:\\\\Users\\\\Asser.Maamoun\\\\Documents\\\\Interviews", "")
    if (".docx" not in name) and (".DOCX" not in name):
        if (".doc" in name) or (".DOC" in name):
            doc_paths.append(path)
            doc_names.append(name)
        else:
            non_doc_names.append(name)
    else:
        docx_names.append(name)
print("Total documents not in docx or doc:", len(non_doc_names))
print("Total documents in doc:", len(doc_names))
print("Total documents in docx:", len(docx_names))


#############################################################################
#         Create a funciton to automatically convert one doc
#############################################################################


def convert_to_docx(path):
    #open MS Word
    word = win32.gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(path)
    doc.Activate()
    
    #rename the path with .docx
    new_file_path = re.sub(r'\.\w+$', '.docx', path)
    new_file_path = re.sub("Interviews", "ConvertedInterviews", new_file_path)
    print(new_file_path)
    
    #save and close
    word.ActiveDocument.SaveAs(
            new_file_path, FileFormat=constants.wdFormatXMLDocument
            )
    doc.Close(SaveChanges=False)
    
def remove_converted(path):
    new_file_path = re.sub(r'\.\w+$', '.docx', path)
    new_file_path = re.sub("Interviews", "ConvertedInterviews", new_file_path)
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
        return 1
    return 0

#############################################################################
#         Loop over and convert the .doc files
#############################################################################

convert_to_docx(doc_paths[198])
path=doc_paths[1]
new_file_abs = re.sub("C:\\\\Users\\\\Asser.Maamoun\\\\G.H. Smart and Company Inc\\\\Research - Documents",
                          "C:\\\\Users\\\\Asser.Maamoun\\\\Documents\\\\Interviews", path)
print(new_file_abs)

cleaned=[]
for doc_path in doc_paths:
    #first read in the given document
    if doc_path not in cleaned:
        cleaned.append(doc_path)
        convert_to_docx(doc_path)
        print(len(cleaned))
    
removed=0
for doc_path in doc_paths:
    removed = removed + remove_converted(doc_path)
print(removed)