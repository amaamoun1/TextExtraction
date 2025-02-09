
# -*- coding: utf-8 -*-
"""
This function reads in a path to a word document and uses docx to decompose the
word document into various parts, which are shipped to other functions for 
parsing.
At the moment, it reads in all of the tables in that word document and uses
which_table to only send the info and competency table to be parsed by
parse_table. This function then creates an overall document dictionary
connecting the parsed tables' names to each table dictionary. It also creates
a dataframe row with entries corresponding to the identified variables in all
of the tables.

To do:
    - Try to detect other relevant information
        - Table of Contents -- to get an overview of frequency of various 
                data in the overall dataset
        - Key Strengths and Key Risks
        - Firm-Specific Mission Text
        - Firm-Specific Key Outcomes Ratings/Comments
        - Company Specific Questions
        - Candidate Specific Recommendations
        - Career Goals and Motivations
    - Transform the entire document into one parseable text. Then check
        to see how many times certain words occur in the text using
        dictionaries or arrays of strings. This can be a crude linguistic
        approach i.e. measuring the frequency of words associated with
        overconfidence (overconfident, assertive, optimistic, etc.) versus
        the frequency of words associated with caution (cautious, timid,
        scientific, etc.).
Notes:
    - info on the docx package: https://python-docx.readthedocs.io/en/latest/index.html
    - info on the pandas package: https://pandas.pydata.org/
"""

import numpy as np
import pandas as pd
import re
from parse_table import extractCompetencies
from parse_table import extractInfo
from identify_table import identify_table

def parse_document(curr_doc, doc_id, doc_path, doc_tables, tables_to_parse, clean_obs):
    #set up document level data storage
    starting_dict={'doc_id':[doc_id], 'doc_path':[doc_path]}
    doc_data = pd.DataFrame(starting_dict)
    
    table_id = 0
    unparsed = 0
    table_tracker = pd.DataFrame(columns=['doc_id', 'table', 'parsed', 'issue', 'unclean', 'string_parsed'])
    doc_unclean_entries = []
    tables_seen=[""]
    table_dict = {}
    #loop through all tables in the document and append like tables
    for table in doc_tables:
        issue = "none"
        last_table = tables_seen[-1]
        table_type = identify_table(table, last_table, clean_obs)
        tables_seen.append(table_type)
        #keep track of the number of unparsed tables
        if table_type not in tables_to_parse:
            unparsed+=1
            continue
        elif table_type in tables_seen[:-1]:
            if (table_type == tables_seen[-1]) & (issue!="multiple " + table_type): #do not allow consecutive to overide multip;e
                issue = "consecutive " + table_type
            else:
                issue="multiple "+ table_type
            if table_type=="info":
                continue #lets skip these duplicates for now..look like they are combinations of other docs...will need to revisit or manual!!!!!!!!!!!!
        if table_type in table_dict.keys():
            #if we see multiple of the same table in one interview, except for info, lets append them together
            #competencies are frequently split up into multiple tables
            table_dict[table_type][0].extend(table)
            if issue != "none":
                table_dict[table_type][1] = issue
            table_dict[table_type][2] += 1
        else:
            table_dict[table_type] = [table, issue, 1]
        table_id += 1
    #parse the appended tables
    for table_type in table_dict.keys():
        table = table_dict[table_type][0]
        issue = table_dict[table_type][1]
        parsed = table_dict[table_type][2]
        if table_type == "competency":
            table_data, is_unclean, unclean_entries, duplicate_keys = extractCompetencies(table, doc_id, curr_doc, clean_obs) 
        elif table_type == "info":
            is_unclean=np.nan
            unclean_entries=[]
            table_data, duplicate_keys = extractInfo(table, doc_id, curr_doc, clean_obs)
        else:
            raise ValueError("unaccounted for table type " + table_type)
        table_tracker = table_tracker.append({'doc_id':doc_id, 'table': table_type, 'parsed': parsed, 'issue': issue, 'unclean': is_unclean}, ignore_index=True, sort=True)
        doc_data = pd.merge(doc_data, table_data, on='doc_id', how='outer')
        doc_unclean_entries = doc_unclean_entries + unclean_entries
    #keep track of the tables_to_parse that were not found
    for tab in tables_to_parse:
        if sum(table_tracker["table"].str.contains(tab))==0:
            table_tracker = table_tracker.append({'doc_id':doc_id, 'table': tab, 'parsed':0, 'issue': np.nan, 'unclean': np.nan}, ignore_index=True, sort=True)

    return (doc_data, table_tracker, doc_unclean_entries)












