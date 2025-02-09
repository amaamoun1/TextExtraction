# -*- coding: utf-8 -*-
"""
This functions reads in one docx table and stores its information into a
table level dictionary. It also creates a dataframe with variable names and
entries for all variables encountered in the document. This will then be
concated with all of the document's other table dataframe to create a master
row of info for that document.

To do:
    - Add robustness by allowing a variable to be passed in identifying the
        type and/or version of the table to be parsed. This could also
        be implemented by creating multiple parse functions, one per
        type of table.

Notes:
    - Merged Cells are read as multiple cells all with the same information
    - info on the docx package: https://python-docx.readthedocs.io/en/latest/index.html
    - info on the pandas package: https://pandas.pydata.org/
"""


from docx import Document
import pandas as pd
from text_cleaning import clean_key
from text_cleaning import clean_entry
from which_table import which_table


#To add robustness, we can add a variable to let the table parser know what type
#    of table it is currently dealing with.
def parse_table(table, table_type, doc_id):
    table_dict = {}
    table_data = pd.DataFrame({'doc_id':[doc_id]})
    table_data.set_index('doc_id')
    unclean_entries = 0
    unseen_keys = []
    for i, row in enumerate(table.rows): #loop through all of the rows
        text = tuple((cell.text for cell in row.cells)) #converts all tables cells to text  
        text = tuple((' '.join(string.split()) for string in text)) #cleans out all extra whitespace objects
        j=0 #let j index over the entries in the row tuple
        while j <= len(text)-2: #while we have at least one additional entry in the row
            key, unseen_key = clean_key(text[j], table_type)
            if len(key) == 0: #if the current cell is empty, it can't be a key, so skip it
                j+=1
                continue
            if unseen_key==1:
                unseen_keys.append(key)
            while (text[j+1]==""): #look for the next non-empty entry in the row
                if j+2 == len(text):
                    break
                j+=1
            cleaned_entry, entry_clean = clean_entry(text[j+1], table_type) #the keys entry is the next cell in the table
            unclean_entries = max(unclean_entries, entry_clean)
            j=j+2 #the next key is after the current key's entry...so two indices away
            # add the keys and entries into a table specific dictionary and dataframe
            #assert(key not in table_dict)
            if key in table_dict:
                raise ValueError("Key '" + key + "' already found in doc_id " + str(doc_id))
            table_data[key] = cleaned_entry
    return table_data, unclean_entries, unseen_keys   



###############################################################################
    # This is some scratch space for debugging and testing #
# =============================================================================
# 
# 
# dummy_docs = {
#         ".\DummyDocs\Cleaning_Small.docx" : {"info": 0, "competencies": 5},
#         ".\DummyDocs\Cleaning_Small_Copy.docx" : {"info": 0, "competencies": 5},
#         ".\DummyDocs\cleaning1_v2019.docx" : {"info": 0, "competencies": 5},
#         ".\DummyDocs\cleaning2_v2012.docx" : {"info": 0, "competencies": 1},
#         ".\DummyDocs\cleaning3_v2015.docx" : {"info": 0, "competencies": 1},
#         ".\DummyDocs\cleaning4_namenotintable.docx" : {"info": 0, "competencies": 1},
#         ".\DummyDocs\cleaning5_feedback.docx" : {"info": 0, "competencies": 0},
#         ".\DummyDocs\cleaning6_v2012_nonamecell.docx" : {"info": 0, "competencies": 1},
#         ".\DummyDocs\cleaning7_v2015_competency_comments.docx" : {"info": 0, "competencies": 1},
#         ".\DummyDocs\cleaning8_v2015_long_comp_comments.docx" : {"info": 0, "competencies": 1},
#         ".\DummyDocs\cleaning9_v2008.docx" : {"info": 0, "competencies": 1},
#         ".\DummyDocs\cleaning10_v2019_NoCompetencies.docx" : {"info": 0, "competencies": 1},
#         }
# 
# dummy_docs = {".\DummyDocs\cleaning10_v2019_NoCompetencies.docx" : {"info": 0, "competencies": 1}}
# 
# to_parse = ["info", "competencies"]
# 
# test_dict = {} 
# test_data = pd.DataFrame()
# info_data = pd.DataFrame()
# comp_data = pd.DataFrame()
# for test_path in dummy_docs:
#     #select the path and convert to a docx Document
#     test_doc = Document(test_path)
#     test_doc_name = test_path.replace('.\\DummyDocs\\', '')
#     print(test_doc_name)
#     
#     #loop through all of the dummy documents
#     path_data = pd.DataFrame({'doc_id':[test_doc_name], 'doc_path':[test_path]})
#     path_dict = {}
#     for table_type in to_parse:    
#         #find the location of the table_type in the document and load table
#         table_loc = dummy_docs[test_path][table_type]
#         test_table = test_doc.tables[table_loc]
#         
#         #checks the output of which_table for table_type in test_path
#         identified_as = which_table(test_table)
#         
#         #if incorrectly identified, print the structure of the tables
#         if identified_as != table_type:
#             continue #do not parse the improper tables
#         #if correctly identified, parse the table
#         else:
#            table_data, unclean_entries, unseen_keys = parse_table(test_table, table_type, test_doc_name)
#            path_data = pd.merge(path_data, table_data, on='doc_id', how='outer')
#            if table_type=="info":
#                info_data=info_data.append(table_data)
#            elif table_type=="competencies":
#                comp_data=comp_data.append(table_data)
#     #append the path data to the test_data
#     test_data=test_data.append(path_data)
# 
# 
# =============================================================================








