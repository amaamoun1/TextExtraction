# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:09:52 2019

@author: Asser.Maamoun
"""

def parse_for_name(Document):
    
    
    

#############################################################################
#         Scratch space to play around with smart tags
#############################################################################
            

import docx2txt
            
#lets also take a look into all of the paragraphs in one of the docs
curr_path = no_info_paths[0]
#curr_path = "C:/Users/Asser.Maamoun/Documents/Interviews\EH Sr. Dir Prov Net Mgnt Michael Lynch Final Report (2).docx"
document = Document(curr_path)
text = docx2txt.process(curr_path)
print(text)

p_counter = 0
for para in document.paragraphs:
    print(p_counter, para.text)
    para = para._element.xpath('.//w:t')
    text = u" ".join(c.text for c in para)
    print(p_counter, text)
    p_counter+=1
    
t_counter = 0
for t in document.tables:
    for i, row in enumerate(t.rows): #loop through all of the rows
        for cell in row.cells:
            cell = cell._element.xpath('.//w:t') #also extracts text from smart tags
            tag = u" ".join(c.tag for c in cell)
            text = u" ".join(c.text for c in cell)
            print(t_counter, i, ":", text)
    t_counter+=1
    
import zipfile as zf
import xml.etree.ElementTree as ET

zip_doc = zf.ZipFile(curr_path)
doc = zip_doc.open("word/document.xml")
doc_tree = ET.parse(doc)

for elem in doc_tree.iter():
    print(elem)

   
d_counter = 0
names = []
for doc_path in no_info_paths:
    print("id:", d_counter)
    curr_doc = Document(doc_path)
    names.append("")
    if len(curr_doc.tables) == 0:
        print('no tables')
        continue
    first_table = curr_doc.tables[0]
    t_info = 0
    for i, row in enumerate(first_table.rows): #loop through all of the rows
        for cell in row.cells:
            cell = cell._element.xpath('.//w:t') #also extracts text from smart tags
            tag = u" ".join(c.tag for c in cell)
            text = u" ".join(c.text for c in cell)
            if "assessment" in text.lower():
                print("identified")
                t_info = 1
                continue
            if t_info == 1 and text!="":
                print("Name:", text)
                names[d_counter]=text
                t_info = 0
                break
    d_counter += 1

