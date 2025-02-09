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


import pandas as pd
from clean_cell import clean_key
from clean_cell import clean_entry

def clean_row(cell_list):
    new_list=[]
    #clear out the duplicates arising from merged cells and drop empty cells
    last_cell=""
    for cell in cell_list:
        if not isinstance(cell, str):
            raise ValueError("cell entry is not string!")
        elif cell==last_cell: #skip duplicates
            continue
        elif cell=="": #skip empties
            last_cell=""
            continue
        new_list.append(cell)
        last_cell=cell
    #clear out all trailing, leading, and consecutive whitespace
    new_list =[' '.join(cell.split()) for cell in new_list]
    return new_list


def extractCompetencies(table, doc_id, curr_id, clean_obs):
    table_data = pd.DataFrame({'doc_id':[doc_id]})
    table_data.set_index('doc_id')
    seen_keys = set() #tracks which keys we have already seen
    duplicate_keys = [] #tracks if a key has been seen multiple times
    is_unclean = 0 #tracks if the table contains unclean entries
    unclean_entries = [] #stores the unclean entries
    
    for row in table: #loop through all of the rows
        #skip rows that have 0 cells
        if len(row) < 1: 
            continue
        #clean row contents
        cleaned_row = clean_row(row)
        #start without a competency, and search through the row for competencies and their ratings
        competency = "" 
        track_key = 0
        for cell in cleaned_row:
            #if no current competency, then we look for the next one
            if competency=="": 
                competency, track_key = clean_key(cell, 'competency', clean_obs)
                if track_key==0: #only parse the keywords so we skip these
                    # if competency == "strategy":
                    #     print("strategy found in " + str(doc_id))
                    competency=""
                    continue 
                elif competency in seen_keys: #check if we have already seen the key
                    duplicate_keys.append(competency)
                else:
                    seen_keys.add(competency)
            #once we have seen a competency, look for its rating in the adjacent cell
            else: 
                cleaned_entry, entry_unclean = clean_entry(cell, 'competency') 
                #double check those cells without a rating
                if entry_unclean: 
                    #keep track if we have had an unclean entry in the table
                    is_unclean = max(is_unclean, entry_unclean)
                    
                    #since the adjacent cell did not contain a rating, check if it is because the adjacent sell is a new competency
                    new_competency, new_track_key = clean_key(cell, 'competency', clean_obs) #lets check if it is an identifiable rating
                    if new_track_key==1: 
                        table_data[competency] = "NF" #note that we could Not Find the rating for the old compentency
                        #update the competency as usual
                        if new_competency in seen_keys: 
                            duplicate_keys.append(new_competency)
                        else:
                            seen_keys.add(new_competency)
                        competency = new_competency
                        continue
                    else: #if the cell is not a competency, then keep track of it
                        unclean_entries.append(cleaned_entry)
                        table_data[competency] = "NF"
                        competency=""
                        continue
                elif cleaned_entry=="": #if the cleaned entry is empty, then keep looking for a rating in the next cell
                    continue
                #add the key-entry pair to our dataset and reset the competency
                table_data[competency] = cleaned_entry
                competency = ""
        #if we have not found a rating and we checked all cells in the row, let the cell entry be "NF" for not found
        if (competency != "") & (track_key==1):
            table_data[competency] = "NF"
    return table_data, is_unclean, unclean_entries, duplicate_keys
        

def extractInfo(table, doc_id, curr_id, clean_obs):
    table_data = pd.DataFrame({'doc_id':[doc_id]})
    table_data.set_index('doc_id')
    seen_keys = set()
    duplicate_keys = []
    for row in table: #loop through all of the rows
        #skip empty rows
        if len(row)==0:
            continue
        #find and clean the key..first item in the row
        key = row[0]
        if not isinstance(key, str):
            raise ValueError("non-string row element: " + str(key))
        cleaned_key, track_key = clean_key(key, "info", clean_obs)
        
        #if we dont need to track the key, skip the current row
        if track_key==0:
            continue
        elif cleaned_key in seen_keys: #keep track if we have already seen the key...if so keep the first instance
            duplicate_keys.append(cleaned_key)
            continue
        else:
            seen_keys.add(cleaned_key)
        
        #find and clean the entry...append together the rest of the row
        entry = clean_row(row[1:])  #the keys entry is the next cell in the table
        entry = ' '.join(entry)
        cleaned_entry, unclean_entry = clean_entry(entry, "info")
        
        #keep track of the key-entry pairing
        table_data[cleaned_key] = cleaned_entry
        
    return table_data, duplicate_keys 






