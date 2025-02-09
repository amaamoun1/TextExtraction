"""
This function reads in a docx table and outputs the the possible variables of that
    tables. Since info and competency tables are structured differently,
    they have seperate functions.
"""

from clean_cell import clean_key
from clean_cell import clean_entry
from identify_table import identify_table
from parse_table import clean_row

##### Table level

def findInfo(table, clean_obs):
    variables=set()
    for row in table:
        clean_var,_ = clean_key(row[0], "info", clean_obs)
        variables.add(clean_var)
    return variables


def findCompetency(table, clean_obs):
    variables=set()
    #check every row
    for row in table:
        if len(row) < 1: 
            continue
        #clean row contents
        cleaned_row = clean_row(row)
        curr_comp = ""
        for cell in cleaned_row:
            #check if we are seeing a rating
            _, is_unclean = clean_entry(cell, "competency")
            is_rating = 1 - is_unclean
            #add the curr_comp if we saw a rating follow it
            if (is_rating == 1):
                if (curr_comp != ""):
                    variables.add(curr_comp)
                    curr_comp = ""
            #if no rating was found, update the curr_comp value to be the current non-rating
            else:
                curr_comp, _ = clean_key(cell, "competency", clean_obs)
    return variables
            



##### easier calling

def findVars_table(table, table_type, clean_obs):
    if table_type == "info":
        return findInfo(table, clean_obs)
    elif table_type == "competency":
        return findCompetency(table, clean_obs)
    else:
        raise ValueError(table_type + " not incorporated in findvar_table")
    return set()





##### document level
        

def findVars_document(curr_doc, doc_id, doc_path, doc_tables, tables_to_parse, clean_obs):
    #set up
    tables_seen=[""]
    table_dict = {}
    var_dict = {}
    #loop through all tables in the document and append like tables
    for table in doc_tables:
        last_table = tables_seen[-1]
        table_type = identify_table(table, last_table, clean_obs)
        tables_seen.append(table_type)
        if table_type in table_dict.keys():
            #if we see multiple of the same table in one interview lets append them together
            #competencies are frequently split up into multiple tables
            table_dict[table_type].extend(table)
        else:
            table_dict[table_type] = table
    #create sets of variables in each table_type
    for table_type in table_dict.keys():
        if table_type=="other":
            continue
        table = table_dict[table_type]
        var_dict[table_type] = findVars_table(table, table_type, clean_obs)
        if "strategy" in var_dict[table_type]:
            print("strategy found in " + str(doc_id))
    #return the variables found
    return var_dict













