# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 14:57:44 2020

@author: Asser.Maamoun
"""

import os
import re
import win32com.client as win32
from win32com.client import constants
from shutil import copyfile

#############################################################################
#        Utility Functions for .docx 
#############################################################################

def move_docx(path, new_path):
    #open MS Word
    word = win32.gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(path)
    doc.Activate()
    
    #save and close
    word.ActiveDocument.SaveAs(
            new_path, FileFormat=constants.wdFormatXMLDocument
            )
    doc.Close(SaveChanges=False)
    
def move_docid(doc_id, folder_name, master_paths):
    print("moving " + str(doc_id) + " to " + folder_name)
    path = master_paths[doc_id]
    path = re.sub(r"C:/Users/Asser.Maamoun/Documents/Interviews\\", r"C:\\\\Users\\\\Asser.Maamoun\\\\Documents\\\\Interviews\\\\", path)
    if "ConvertedInterviews" in path:
        new_path = re.sub("ConvertedInterviews", folder_name, path)
    else:
        new_path = re.sub("Interviews", folder_name, path)
    copyfile(path, new_path)
    
def clear_folder(folder):
    path = "C:/Users/Asser.Maamoun/Documents/" + folder
    filelist = [f for f in os.listdir(path) if re.search(".docx$", f, re.IGNORECASE)]
    for f in filelist:
        os.remove(os.path.join(path, f))
        
    
